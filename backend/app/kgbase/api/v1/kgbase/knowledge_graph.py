#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import json
import logging
from contextlib import suppress
from typing import Annotated

import anyio
from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Query, Request, UploadFile
from fastapi.responses import StreamingResponse

from backend.app.file.file import MAX_UPLOAD_SIZE
from backend.app.kgbase.schema import GetIndexDetail, GetKnowledgeGraphDetail, GetSchemaGraphDetail
from backend.app.kgbase.schema.chat_library import AppendMessageParam
from backend.app.kgbase.schema.community import AddCommunityParam, UpdateCommunityParam
from backend.app.kgbase.schema.embedding import EmbeddingBase
from backend.app.kgbase.schema.knowledge_entity import AddKnowledgeEntityParam
from backend.app.kgbase.schema.knowledge_graph import (
    AddKnowledgeGraphParam,
    AskKnowledgeGraphParam,
    KnowledgeGraphResponse,
    UpdateKnowledgeGraphParam,
)
from backend.app.kgbase.schema.knowledge_relationship import AddKnowledgeRelationshipParam
from backend.app.kgbase.service.chat_context_service import chat_context_service
from backend.app.kgbase.service.chat_library_service import chat_library_service
from backend.app.kgbase.service.community_service import community_service
from backend.app.kgbase.service.embedding_service import embedding_service
from backend.app.kgbase.service.knowledge_entity_service import knowledge_entity_service
from backend.app.kgbase.service.knowledge_graph_service import knowledge_graph_service
from backend.app.kgbase.service.knowledge_relationship_service import knowledge_relationship_service
from backend.app.kgbase.service.ownership_service import ownership_service
from backend.app.kgbase.service.schema_graph_service import schema_graph_service
from backend.app.task.celery import celery_app
from backend.common.core_layer.unigraph.module.sapperrag.retriver.structured_search.local_search.system_prompt import (
    LOCAL_SEARCH_SYSTEM_PROMPT,
)
from backend.common.exception.errors import ForbiddenError
from backend.common.pagination import DependsPagination, paging_data
from backend.common.rate_limit import rate_limiter
from backend.common.response.response_schema import CustomResponse, ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth, get_token
from backend.common.security.permission import RequestPermission
from backend.common.task_progress import scaled_progress, should_report, task_error_result, task_progress, task_result
from backend.core.conf import settings
from backend.database.db_mysql import CurrentSession
from backend.utils.serializers import select_as_dict

logger = logging.getLogger(__name__)

# 定义心跳间隔（50秒）
HEARTBEAT_INTERVAL = 50

router = APIRouter()


def _safe_question_error(exc: Exception) -> tuple[int, str]:
    """Map model-provider failures to stable messages without leaking responses."""
    raw_message = str(exc).lower()
    response = getattr(exc, 'response', None)
    candidate_codes = (
        getattr(exc, 'status_code', None),
        getattr(response, 'status_code', None),
    )
    normalized_codes = {int(code) for code in candidate_codes if isinstance(code, (int, str)) and str(code).isdigit()}
    status_code = next(
        iter(normalized_codes),
        500,
    )

    if 401 in normalized_codes or any(
        marker in raw_message
        for marker in ('error code: 401', '401 unauthorized', '无效的令牌', 'invalid token', 'invalid api key')
    ):
        return 401, '当前模型凭据无效，请到个人中心重新配置 API Key'
    if 429 in normalized_codes or 'error code: 429' in raw_message:
        return 429, '模型服务请求过于频繁，请稍后重试'
    if status_code in {502, 503, 504}:
        return status_code, '模型服务暂时不可用，请稍后重试'
    if isinstance(exc, HTTPException) and isinstance(exc.detail, str):
        return status_code, exc.detail
    return 500, '问答处理失败，请检查模型配置或稍后重试'


# 心跳机制，保持发起QA请求时保持链接活跃
async def merge_async_generators(*gens):
    """
    合并多个异步生成器，按照产生的顺序返回结果
    """
    queue = asyncio.Queue()

    async def run_generator(gen):
        try:
            async for item in gen:
                await queue.put(('item', item))
        except Exception as exc:
            await queue.put(('error', exc))
        finally:
            await queue.put(('done', None))

    try:
        # 创建取消作用域
        async with anyio.create_task_group() as tg:
            for gen in gens:
                tg.start_soon(run_generator, gen)

            remaining = len(gens)
            while remaining:
                kind, payload = await queue.get()
                if kind == 'done':
                    remaining -= 1
                elif kind == 'error':
                    raise payload
                else:
                    yield payload
    except anyio.get_cancelled_exc_class():
        # 取消时不做特殊处理，让上层处理
        raise
    except Exception:
        raise


async def _run_knowledge_question(
    *,
    uuid: str,
    obj: AskKnowledgeGraphParam,
    user_uuid: str,
    progress_callback=None,
    token_callback=None,
):
    async def report(message: str, detail: str, data: dict | None = None) -> None:
        if progress_callback:
            await progress_callback(message, detail, data)

    await report('正在解析问题', '正在识别查询意图并准备检索上下文')
    api_key, base_url, model = await knowledge_graph_service.get_user_llm_info(
        user_token=obj.user_token,
        model_uuid=obj.llm_model_uuid,
    )
    embedding_api_key, embedding_base_url, embedding_model = (
        await knowledge_graph_service.get_user_embedding_info(user_token=obj.user_token)
    )
    await report('模型配置加载完成', f'将使用 {model} 生成回答')

    knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
    data = GetIndexDetail(**select_as_dict(knowledge_graph))
    await report(
        '知识索引加载完成',
        f'已载入 {len(data.entities)} 个实体、{len(data.relationships)} 条关系和 {len(data.communities)} 份社区报告',
    )
    await report('正在检索实体与关系', '正在构建与问题相关的局部知识上下文')

    async def provide_conversation_context(context_text: str):
        return await chat_context_service.prepare(
            chat_library_uuid=obj.chat_library_uuid,
            current_message_uuid=obj.current_message_uuid,
            user_uuid=user_uuid,
            current_question=obj.message,
            knowledge_context=context_text,
            system_prompt=LOCAL_SEARCH_SYSTEM_PROMPT,
            api_key=api_key,
            base_url=base_url,
            model=model,
            progress_callback=progress_callback,
        )

    response = await knowledge_graph_service.query(
        knowledge_graph=data,
        query=obj.message,
        infer=obj.infer,
        depth=obj.depth,
        api_key=api_key,
        base_url=base_url,
        model=model,
        embedding_api_key=embedding_api_key,
        embedding_base_url=embedding_base_url,
        embedding_model=embedding_model,
        context_provider=provide_conversation_context if obj.chat_library_uuid else None,
        token_callback=token_callback,
        progress_callback=progress_callback,
    )
    await report('正在整理回答', '知识检索完成，正在汇总回答与信息源')
    return response, model


@router.get('/all/{kg_base_uuid}', summary='获取kgbase下所有实例图谱', dependencies=[DependsJwtAuth])
async def get_all_knowledge_graphs(request: Request, kg_base_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_kg_base(user_uuid=request.user.uuid, uuid=kg_base_uuid)
    knowledge_graphs = await knowledge_graph_service.get_all(kg_base_uuid=kg_base_uuid)
    data = [KnowledgeGraphResponse(**select_as_dict(knowledge_graph)) for knowledge_graph in knowledge_graphs]
    return response_base.success(data=data)


@router.get('/{uuid}', summary='获取实例图谱详情', dependencies=[DependsJwtAuth])
async def get_knowledge_graph(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=uuid)
    knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
    data = GetKnowledgeGraphDetail(**select_as_dict(knowledge_graph))
    return response_base.success(data=data)


@router.get('/explore/{uuid}/overview', summary='获取渐进式图谱概览', dependencies=[DependsJwtAuth])
async def get_exploration_overview(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=uuid)
    data = await knowledge_graph_service.get_exploration_overview(uuid=uuid)
    return response_base.success(data=data)


@router.get('/explore/{uuid}/type', summary='按实体类型展开图谱', dependencies=[DependsJwtAuth])
async def get_exploration_type(
    request: Request,
    uuid: Annotated[str, Path(...)],
    entity_type: Annotated[str, Query(...)],
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=uuid)
    result = await knowledge_graph_service.get_exploration_type(uuid=uuid, entity_type=entity_type, limit=limit)
    return response_base.success(
        data={
            'entities': [select_as_dict(entity) for entity in result['entities']],
            'relationships': [select_as_dict(item) for item in result['relationships']],
        }
    )


@router.get('/explore/{uuid}/neighbors/{entity_uuid}', summary='按跳数展开实体邻居', dependencies=[DependsJwtAuth])
async def get_exploration_neighbors(
    request: Request,
    uuid: Annotated[str, Path(...)],
    entity_uuid: Annotated[str, Path(...)],
    depth: Annotated[int, Query(ge=1, le=5)] = 1,
    limit: Annotated[int, Query(ge=1, le=500)] = 300,
) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=uuid)
    await ownership_service.require_knowledge_entity_in_graph(
        user_uuid=request.user.uuid, entity_uuid=entity_uuid, knowledge_graph_uuid=uuid
    )
    result = await knowledge_graph_service.get_exploration_neighbors(
        uuid=uuid, entity_uuid=entity_uuid, depth=depth, limit=limit
    )
    return response_base.success(
        data={
            'entities': [select_as_dict(entity) for entity in result['entities']],
            'relationships': [select_as_dict(item) for item in result['relationships']],
        }
    )


@router.get('/depth/{uuid}', summary='获取最大索引深度', dependencies=[DependsJwtAuth])
async def get_depth(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=uuid)
    depth = await knowledge_graph_service.get_depth(uuid=uuid)
    return response_base.success(data=depth)


@router.post('/export-index-file/{uuid}', summary='将索引导出为文件', dependencies=[DependsJwtAuth])
async def export_knowledge_graph_index_file(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=uuid)
    knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
    data = GetKnowledgeGraphDetail(**select_as_dict(knowledge_graph))
    entities = json.dumps([entity.to_dict() for entity in data.entities], ensure_ascii=False, indent=4)
    relationships = json.dumps(
        [relationship.to_dict() for relationship in data.relationships], ensure_ascii=False, indent=4
    )
    communities = json.dumps([community.to_dict() for community in data.communities], ensure_ascii=False, indent=4)
    data = {'entities': entities, 'relationships': relationships, 'communities': communities}
    json_data = json.dumps(data)
    return response_base.success(data=json_data)


@router.post('/export-index-url/{uuid}', summary='将索引导出为url', dependencies=[DependsJwtAuth])
async def export_knowledge_graph_index_url(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=uuid)
    url = f'{settings.INDEX_EXPORT_URL_ROOT}/{uuid}'
    return response_base.success(data={'url': url})


@router.post('/import-index', summary='导入索引', dependencies=[DependsJwtAuth])
async def import_knowledge_graph_index(
    request: Request, knowledge_graph_uuid: str = Form(...), file: UploadFile = File(...)
) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=knowledge_graph_uuid)
    try:
        # 读取文件内容
        file_content = await file.read(MAX_UPLOAD_SIZE + 1)
        if len(file_content) > MAX_UPLOAD_SIZE:
            return response_base.fail(res=CustomResponse(code=413, msg='索引文件不能超过 50 MB'))
        index_data = json.loads(file_content.decode('utf-8'))  # 将文件解析为 JSON
        entities = json.loads(index_data['entities'])
        communities = json.loads(index_data['communities'])
    except json.JSONDecodeError:
        return response_base.fail(res=CustomResponse(code=500, msg='解析错误，请重试'))

    # 以下为原有逻辑：处理 communities 和 entities
    triple_community_hash_table = {}
    for community in communities:
        await community_service.update(
            uuid=community.get('uuid'),
            obj=UpdateCommunityParam(
                title=community.get('title', ''),
                content=community.get('content', ''),
                level=community.get('level', ''),
                rating=str(community.get('rating', '')),
                attributes=community.get('attributes', ''),
                knowledge_graph_uuid=knowledge_graph_uuid,
            ),
        )
        triple_community_hash_table[community['id']] = community.get('uuid')

    for entity in entities:
        await embedding_service.update(
            uuid=entity.get('uuid'),
            obj=EmbeddingBase(knowledge_entity_uuid=entity.get('uuid'), vector=json.dumps(entity.get('embeddings'))),
        )
        entity_community = []
        if entity.get('community_ids', '{}'):
            try:
                entity_community = json.loads(entity.get('community_ids', '{}').replace("'", '"'))
            except json.JSONDecodeError:
                continue
        for community in entity_community:
            community_uuid = triple_community_hash_table.get(community, None)
            if community_uuid:
                await knowledge_entity_service.add_community_relation(
                    knowledge_entity_uuid=entity.get('id'), community_uuid=community_uuid
                )

    return response_base.success(data={'results': '索引导入成功'})


@router.post(
    '/ask/{uuid}',
    summary='基于索引进行问答',
    dependencies=[DependsJwtAuth, Depends(rate_limiter(times=30, seconds=60))],
)
async def ask_knowledge_graph(request: Request, uuid: Annotated[str, Path(...)], obj: AskKnowledgeGraphParam):
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=uuid)
    obj.user_token = get_token(request)

    async def generate_stream():
        # 创建事件标志来控制心跳任务
        stop_event = asyncio.Event()

        async def send_heartbeats():
            while not stop_event.is_set():
                try:
                    # 使用wait_for而不是sleep，这样可以被事件中断
                    await asyncio.wait_for(stop_event.wait(), timeout=HEARTBEAT_INTERVAL)
                except asyncio.TimeoutError:
                    # 50秒到了，发送心跳
                    yield (
                        json.dumps({
                            'type': 'processing',
                            'message': '正在检索并生成回答',
                            'detail': '模型仍在处理，请稍候',
                        })
                        + '\n'
                    )

        async def process_request():
            try:
                context_progress: asyncio.Queue[dict] = asyncio.Queue()

                async def report_context_progress(message: str, detail: str, data: dict | None = None) -> None:
                    payload = {
                        'type': 'processing',
                        'message': message,
                        'detail': detail,
                    }
                    if data:
                        payload['data'] = data
                    await context_progress.put(payload)

                async def report_answer_delta(delta: str) -> None:
                    await context_progress.put({'type': 'answer_delta', 'delta': delta})

                query_task = asyncio.create_task(
                    _run_knowledge_question(
                        uuid=uuid,
                        obj=obj,
                        user_uuid=request.user.uuid,
                        progress_callback=report_context_progress,
                        token_callback=report_answer_delta,
                    )
                )
                try:
                    while not query_task.done() or not context_progress.empty():
                        try:
                            progress = await asyncio.wait_for(context_progress.get(), timeout=0.1)
                        except asyncio.TimeoutError:
                            continue
                        yield json.dumps(progress, ensure_ascii=False) + '\n'
                    response, _ = await query_task
                finally:
                    if not query_task.done():
                        query_task.cancel()
                        with suppress(asyncio.CancelledError):
                            await query_task
                yield json.dumps({'type': 'final_result', 'data': response, 'code': 200, 'msg': 'success'}) + '\n'

            except asyncio.TimeoutError:
                payload = {'type': 'error', 'code': 504, 'msg': '模型响应超时，请稍后重试'}
                yield json.dumps(payload, ensure_ascii=False) + '\n'
            except Exception as e:
                logger.exception('Knowledge graph question failed')
                status_code, message = _safe_question_error(e)
                yield json.dumps({'type': 'error', 'code': status_code, 'msg': message}, ensure_ascii=False) + '\n'
            finally:
                stop_event.set()  # 停止心跳

        try:
            async for item in merge_async_generators(send_heartbeats(), process_request()):
                yield item
        except asyncio.CancelledError:
            stop_event.set()
            raise

    # 返回 StreamingResponse，保持 NDJSON 格式
    return StreamingResponse(generate_stream(), media_type='application/x-ndjson')


@celery_app.task(bind=True, name='knowledge_graph.ask')
async def ask_knowledge_graph_task(
    self,
    uuid: str,
    user_uuid: str,
    user_token: str,
    obj_data: dict,
):
    try:
        obj = AskKnowledgeGraphParam(**obj_data)
        obj.user_token = user_token
        progress_by_stage = {
            '正在解析问题': 8,
            '模型配置加载完成': 18,
            '知识索引加载完成': 32,
            '正在检索实体与关系': 48,
            '实体检索完成': 58,
            '关系检索完成': 66,
            '信息源检索完成': 72,
            '社区报告检索完成': 78,
            '正在整理回答': 94,
        }
        partial_answer: list[str] = []
        generation_started = False
        last_partial_update = 0.0

        async def report_progress(message: str, detail: str, data: dict | None = None) -> None:
            progress = progress_by_stage.get(message, 62)
            metrics = {'retrieval': data} if data else None
            task_progress(self, message, progress, detail=detail, metrics=metrics)

        async def report_answer_delta(delta: str) -> None:
            nonlocal generation_started, last_partial_update
            if not delta:
                return
            partial_answer.append(delta)
            if not generation_started:
                generation_started = True
                task_progress(self, '正在生成回答', 82, detail='正在根据检索到的知识逐步生成回答')
            now = asyncio.get_running_loop().time()
            if now - last_partial_update < 0.18:
                return
            last_partial_update = now
            self.update_state(
                state='PROGRESS',
                meta={
                    'type': 'answer_delta',
                    'message': '正在生成回答',
                    'detail': '正在根据检索到的知识逐步生成回答',
                    'progress': 88,
                    'partial_answer': ''.join(partial_answer),
                    'logs': list(getattr(self, '_unigraph_progress_logs', [])),
                },
            )

        response, model = await _run_knowledge_question(
            uuid=uuid,
            obj=obj,
            user_uuid=user_uuid,
            progress_callback=report_progress,
            token_callback=report_answer_delta,
        )
        answer = str(response.get('results') or '')
        assistant_message_uuid = None
        if obj.chat_library_uuid and answer:
            saved = await chat_library_service.append_message(
                uuid=obj.chat_library_uuid,
                user_uuid=user_uuid,
                obj=AppendMessageParam(
                    role='assistant',
                    content=answer,
                    knowledge_graph_uuid=uuid,
                    model_name=model,
                    effort=obj.effort,
                    sources=response.get('context_data') or {},
                ),
            )
            assistant_message_uuid = saved.get('message_uuid')

        result_data = dict(response)
        result_data['assistant_message_uuid'] = assistant_message_uuid
        return task_result(
            self,
            '问答已完成',
            data=result_data,
            detail='回答与信息源已保存到当前对话',
            metrics={'chat_library_uuid': obj.chat_library_uuid},
        )
    except Exception as exc:
        logger.exception('Background knowledge graph question failed')
        status_code, message = _safe_question_error(exc)
        return task_error_result(
            self,
            {
                'error': {
                    'code': status_code,
                    'message': message,
                    'type': exc.__class__.__name__,
                    'details': {'task_id': self.request.id},
                },
                'exc_type': f'{exc.__class__.__module__}.{exc.__class__.__name__}',
                'exc_message': message,
            },
        )


@celery_app.task(bind=True, name='knowledge_graph.build_index')
async def build_index(self, uuid: str, user_token: str, depth: int = 4):
    """
    Celery task: Build index for knowledge graph with progress simulation.
    :param self: Celery task instance
    :param uuid: Knowledge graph UUID
    :param user_token: User JWT token
    :param depth: Index depth, fixed to four levels by default
    """
    try:
        # 初始化任务状态
        task_progress(self, '准备构建知识索引', 3, detail='正在读取模型配置和图谱数据')

        # 获取用户信息和知识图谱
        api_key, base_url, model = await knowledge_graph_service.get_user_llm_info(user_token=user_token)
        embedding_api_key, embedding_base_url, embedding_model = await knowledge_graph_service.get_user_embedding_info(
            user_token=user_token
        )
        knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
        data = GetIndexDetail(**select_as_dict(knowledge_graph))
        entity_total = len(data.entities)
        relationship_total = len(data.relationships)
        task_progress(
            self,
            '图谱初始化完成',
            10,
            detail=f'已加载 {entity_total} 个实体、{relationship_total} 条关系，索引深度 4 层',
            metrics={'entities': entity_total, 'relationships': relationship_total, 'depth': 4},
        )

        def report_index_progress(stage, completed, total, item):
            if stage == 'communities':
                community_ids = [str(getattr(community, 'id', '')) for community in item]
                preview = '、'.join(filter(None, community_ids[:6]))
                suffix = f'：{preview}' if preview else ''
                task_progress(
                    self,
                    '社区划分完成',
                    28,
                    detail=f'得到 {completed} 个社区{suffix}',
                    metrics={'communities': completed},
                )
                return
            if not should_report(completed, total):
                return
            if stage == 'reports':
                title = getattr(item, 'title', '') or f'社区 {getattr(item, "id", completed)}'
                task_progress(
                    self,
                    '正在生成社区报告',
                    scaled_progress(completed, total, 30, 58),
                    detail=f'报告“{title}”生成完毕（{completed}/{total}）',
                    metrics={'reports_done': completed, 'reports_total': total},
                )
            elif stage == 'embeddings':
                entity, error = item
                name = getattr(entity, 'name', '') or f'实体 {completed}'
                task_progress(
                    self,
                    '正在生成实体向量',
                    scaled_progress(completed, total, 60, 82),
                    detail=f'实体“{name}”向量{"生成失败" if error else "生成完毕"}（{completed}/{total}）',
                    metrics={'embeddings_done': completed, 'embeddings_total': total},
                )

        # 执行构建索引任务
        index_result = await knowledge_graph_service.build_index(
            knowledge_graph=data,
            level=4,
            api_key=api_key,
            base_url=base_url,
            model=model,
            embedding_api_key=embedding_api_key,
            embedding_base_url=embedding_base_url,
            embedding_model=embedding_model,
            progress_callback=report_index_progress,
        )

        # 处理索引结果
        entities = index_result.get('entities', [])
        community_reports = index_result.get('community_reports', [])
        triple_community_hash_table = {}

        # 删除旧的社区数据
        await community_service.delete_all(knowledge_graph_uuid=uuid)

        # 添加社区数据
        report_total = len(community_reports)
        for report_index, item in enumerate(community_reports, start=1):
            community_uuid = await community_service.add(
                obj=AddCommunityParam(
                    title=item.get('title', ''),
                    content=item.get('full_content', ''),
                    level=str(item.get('level', '')),
                    rating=str(item.get('rating', '')),
                    attributes=item.get('attributes', ''),
                    knowledge_graph_uuid=uuid,
                )
            )
            triple_community_hash_table[item['id']] = community_uuid
            if should_report(report_index, report_total, checkpoints=10):
                task_progress(
                    self,
                    '正在保存社区报告',
                    scaled_progress(report_index, report_total, 83, 89),
                    detail=f'已保存 {report_index}/{report_total} 份社区报告',
                    metrics={'reports_saved': report_index, 'reports_total': report_total},
                )

        # 添加实体和嵌入数据
        embedding_total = len(entities)
        for embedding_index, entity in enumerate(entities, start=1):
            entity_uuid = entity.get('id')
            vector = entity.get('attributes_embedding')
            await embedding_service.add(obj=EmbeddingBase(knowledge_entity_uuid=entity_uuid, vector=json.dumps(vector)))
            entity_community = []
            if entity.get('community_ids', '{}'):
                entity_community = json.loads(json.dumps(entity.get('community_ids', '[]')))
            for community in entity_community:
                community_uuid = triple_community_hash_table.get(community, None)
                if community_uuid:
                    await knowledge_entity_service.add_community_relation(
                        knowledge_entity_uuid=entity_uuid, community_uuid=community_uuid
                    )
            if should_report(embedding_index, embedding_total, checkpoints=12):
                task_progress(
                    self,
                    '正在写入实体索引',
                    scaled_progress(embedding_index, embedding_total, 90, 98),
                    detail=f'已写入 {embedding_index}/{embedding_total} 个实体向量及社区映射',
                    metrics={'entities_saved': embedding_index, 'entities_total': embedding_total},
                )

        # 更新索引状态和深度
        await knowledge_graph_service.update_index_status(uuid=uuid, index_status=1)
        await knowledge_graph_service.update_depth(uuid=uuid, depth=4)
        # 完成任务
        return task_result(
            self,
            '索引生成完毕',
            data={'results': '成功构建索引'},
            detail=f'共生成 {report_total} 份社区报告和 {embedding_total} 个实体向量',
            metrics={'communities': report_total, 'embeddings': embedding_total},
        )

    except Exception as e:
        error_payload = {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e) or '知识图谱索引构建失败，请稍后重试',
                'type': e.__class__.__name__,
                'details': {'task_id': self.request.id, 'module': e.__class__.__module__},
            },
            'exc_type': f'{e.__class__.__module__}.{e.__class__.__name__}',
            'exc_message': str(e),
        }
        return task_error_result(self, error_payload)


@router.get(
    '',
    summary='（模糊条件）分页获取所有实例图谱',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_knowledge_graphs(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseModel:
    knowledge_graph_select = await knowledge_graph_service.get_select(
        user_uuid=request.user.uuid, name=name, status=status
    )
    page_data = await paging_data(db, knowledge_graph_select, KnowledgeGraphResponse)
    return response_base.success(data=page_data)


@celery_app.task(bind=True, name='knowledge_graph.create_knowledge_graph')
async def create_knowledge_graph(self, user_token: str, obj_data: dict):
    """
    Celery task: Create a knowledge graph with progress simulation.
    :param self: Celery task instance
    :param user_token: User JWT token
    :param obj_data: Serialized AddKnowledgeGraphParam data (JSON string)
    """
    try:
        # 初始化任务状态
        task_progress(self, '准备创建知识图谱', 3, detail='正在校验创建参数')

        # 反序列化参数
        obj_dict = obj_data
        obj = AddKnowledgeGraphParam(**obj_dict)

        # 获取用户信息
        api_key, base_url, model = await knowledge_graph_service.get_user_llm_info(user_token=user_token)
        task_progress(
            self,
            '文档与模型配置已就绪',
            8,
            detail=f'待处理 {len(obj.file_paths)} 个文件',
            metrics={'files': len(obj.file_paths)},
        )
        # 调用 schema_service 创建图谱
        knowledge_uuid = await knowledge_graph_service.add(obj=obj.data)

        # 获取模式图谱数据
        schema_graph = await schema_graph_service.get_schema_graph(uuid=obj.data.schema_graph_uuid)
        schema_data = GetSchemaGraphDetail(**select_as_dict(schema_graph))
        task_progress(
            self,
            '知识架构加载完成',
            14,
            detail=f'包含 {len(schema_data.entities)} 类实体、{len(schema_data.relationships)} 类关系',
            metrics={'entity_types': len(schema_data.entities), 'relationship_types': len(schema_data.relationships)},
        )

        # 执行提取任务
        knowledge_graph_data_all = await knowledge_graph_service.extract(
            file_paths=obj.file_paths,
            schema=schema_data,
            api_key=api_key,
            base_url=base_url,
            model=model,
            task_client=self,
        )
        total_triples = sum(len(item.get('semantic_kg', [])) for item in knowledge_graph_data_all)
        task_progress(
            self,
            '实体与关系抽取完成',
            65,
            detail=f'共得到 {total_triples} 条三元组，开始写入图数据库',
            metrics={'triples': total_triples},
        )
        processed_triples = 0
        entity_names = set()
        relationships_written = 0

        # 处理提取的图谱数据
        for knowledge_graph_data in knowledge_graph_data_all:
            knowledge_graph = knowledge_graph_data['semantic_kg']
            triple_source = knowledge_graph_data['triple_source']

            # 转换三元组源哈希表
            triple_source_hash_table_ = {}
            for item in triple_source:
                triple_source_hash_table_[item['ID']] = item['TripleSource']

            # 同时处理每个三元组及其ID对应的TripleSource
            for triple in knowledge_graph:
                directional_entity = triple.get('DirectionalEntity')
                directed_entity = triple.get('DirectedEntity')
                relation = triple.get('Relation')
                source_id = triple.get('ID')
                source_entity_uuid, target_entity_uuid = None, None

                # 处理头实体
                if directional_entity:
                    entity_names.add(directional_entity.get('Name'))
                    source_entity = AddKnowledgeEntityParam(
                        knowledge_graph_uuid=knowledge_uuid,
                        name=directional_entity.get('Name'),
                        type=directional_entity.get('Type'),
                        attributes=json.dumps(directional_entity.get('Attributes')),
                    )
                    try:
                        # 如果数据库没有实体，则新建
                        source_entity_uuid = await knowledge_entity_service.add(obj=source_entity)
                    except ForbiddenError:
                        exist_source_entity = await knowledge_entity_service.get_knowledge_entity(
                            name=source_entity.name, knowledge_graph_uuid=source_entity.knowledge_graph_uuid
                        )
                        source_entity_uuid = exist_source_entity.uuid

                # 处理尾实体
                if directed_entity:
                    entity_names.add(directed_entity.get('Name'))
                    target_entity = AddKnowledgeEntityParam(
                        knowledge_graph_uuid=knowledge_uuid,
                        name=directed_entity.get('Name'),
                        type=directed_entity.get('Type'),
                        attributes=json.dumps(directed_entity.get('Attributes')),
                    )
                    try:
                        # 如果数据库没有，则新建
                        target_entity_uuid = await knowledge_entity_service.add(obj=target_entity)
                    except ForbiddenError:
                        exist_target_entity = await knowledge_entity_service.get_knowledge_entity(
                            name=target_entity.name, knowledge_graph_uuid=target_entity.knowledge_graph_uuid
                        )
                        target_entity_uuid = exist_target_entity.uuid

                # 处理关系
                if relation and source_entity_uuid and target_entity_uuid:
                    relationship = AddKnowledgeRelationshipParam(
                        knowledge_graph_uuid=knowledge_uuid,
                        source_entity_uuid=source_entity_uuid,
                        target_entity_uuid=target_entity_uuid,
                        name=relation.get('Name'),
                        attributes='{}',
                        type=relation.get('Type'),
                        source=triple_source_hash_table_[source_id],
                    )
                    # 创建关系
                    await knowledge_relationship_service.add(obj=relationship)
                    relationships_written += 1
                processed_triples += 1
                if should_report(processed_triples, total_triples):
                    task_progress(
                        self,
                        '正在写入图谱数据',
                        scaled_progress(processed_triples, total_triples, 66, 98),
                        detail=f'已处理 {processed_triples}/{total_triples} 条三元组，识别 {len(entity_names)} 个实体',
                        metrics={
                            'triples_done': processed_triples,
                            'triples_total': total_triples,
                            'entities': len(entity_names),
                            'relationships': relationships_written,
                        },
                    )

        # 完成任务
        return task_result(
            self,
            '知识图谱创建完毕',
            detail=f'已处理 {total_triples} 条三元组，写入 {len(entity_names)} 个实体、{relationships_written} 条关系',
            metrics={'triples': total_triples, 'entities': len(entity_names), 'relationships': relationships_written},
        )

    except Exception as e:
        logger.info(f'Task {self.request.id} failed: {str(e)}')
        error_payload = {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '新建知识图谱已存在！'
                if f'{e.__class__.__module__}.{e.__class__.__name__}'
                == 'backend.common.exception.errors.ForbiddenError'
                else str(e),
                'type': e.__class__.__name__,
                'details': {'task_id': self.request.id, 'module': e.__class__.__module__},
            },
            'exc_type': f'{e.__class__.__module__}.{e.__class__.__name__}',
            'exc_message': str(e),
        }
        return task_error_result(self, error_payload)


@celery_app.task(bind=True, name='knowledge_graph.update_knowledge_graph')
async def update_knowledge_graph(self, uuid: str, user_token: str, obj_data: dict):
    """
    Celery task: Update a knowledge graph with progress simulation.
    :param self: Celery task instance
    :param uuid: Knowledge graph UUID
    :param user_token: User JWT token
    :param obj_data: Serialized UpdateKnowledgeGraphParam data (JSON string)
    """
    try:
        # 初始化任务状态
        task_progress(self, '准备更新知识图谱', 3, detail='正在校验更新参数')

        # 反序列化参数
        obj_dict = obj_data
        obj = UpdateKnowledgeGraphParam(**obj_dict)

        # 获取用户信息
        api_key, base_url, model = await knowledge_graph_service.get_user_llm_info(user_token=user_token)
        task_progress(
            self,
            '更新资料已就绪',
            8,
            detail=f'待处理 {len(obj.file_paths)} 个文件',
            metrics={'files': len(obj.file_paths)},
        )

        # 更新知识图谱
        await knowledge_graph_service.update(uuid=uuid, obj=obj.data)

        # 获取模式图谱数据
        schema_graph = await schema_graph_service.get_schema_graph(uuid=obj.data.schema_graph_uuid)
        schema_data = GetSchemaGraphDetail(**select_as_dict(schema_graph))
        task_progress(
            self,
            '知识架构加载完成',
            14,
            detail=f'包含 {len(schema_data.entities)} 类实体、{len(schema_data.relationships)} 类关系',
            metrics={'entity_types': len(schema_data.entities), 'relationship_types': len(schema_data.relationships)},
        )

        # 执行提取任务
        knowledge_graph_data_all = await knowledge_graph_service.extract(
            file_paths=obj.file_paths,
            schema=schema_data,
            api_key=api_key,
            base_url=base_url,
            model=model,
            task_client=self,
        )
        total_triples = sum(len(item.get('semantic_kg', [])) for item in knowledge_graph_data_all)
        task_progress(
            self,
            '增量抽取完成',
            65,
            detail=f'共得到 {total_triples} 条待合并三元组',
            metrics={'triples': total_triples},
        )
        processed_triples = 0
        entity_names = set()
        relationships_written = 0
        # 处理提取的图谱数据
        for knowledge_graph_data in knowledge_graph_data_all:
            knowledge_graph = knowledge_graph_data['semantic_kg']
            triple_source = knowledge_graph_data['triple_source']

            # 转换三元组源哈希表
            triple_source_hash_table_ = {}
            for item in triple_source:
                triple_source_hash_table_[item['ID']] = item['TripleSource']

            # 同时处理每个三元组及其ID对应的TripleSource
            for triple in knowledge_graph:
                directional_entity = triple.get('DirectionalEntity')
                directed_entity = triple.get('DirectedEntity')
                relation = triple.get('Relation')
                source_id = triple.get('ID')
                source_entity_uuid, target_entity_uuid = None, None

                # 处理头实体
                if directional_entity:
                    entity_names.add(directional_entity.get('Name'))
                    source_entity = AddKnowledgeEntityParam(
                        knowledge_graph_uuid=uuid,
                        name=directional_entity.get('Name'),
                        type=directional_entity.get('Type'),
                        attributes=json.dumps(directional_entity.get('Attributes')),
                    )
                    try:
                        # 如果数据库没有实体，则新建
                        source_entity_uuid = await knowledge_entity_service.add(obj=source_entity)
                    except ForbiddenError:
                        exist_source_entity = await knowledge_entity_service.get_knowledge_entity(
                            name=source_entity.name, knowledge_graph_uuid=source_entity.knowledge_graph_uuid
                        )
                        source_entity_uuid = exist_source_entity.uuid

                # 处理尾实体
                if directed_entity:
                    entity_names.add(directed_entity.get('Name'))
                    target_entity = AddKnowledgeEntityParam(
                        knowledge_graph_uuid=uuid,
                        name=directed_entity.get('Name'),
                        type=directed_entity.get('Type'),
                        attributes=json.dumps(directed_entity.get('Attributes')),
                    )
                    try:
                        # 如果数据库没有，则新建
                        target_entity_uuid = await knowledge_entity_service.add(obj=target_entity)
                    except ForbiddenError:
                        exist_target_entity = await knowledge_entity_service.get_knowledge_entity(
                            name=target_entity.name, knowledge_graph_uuid=target_entity.knowledge_graph_uuid
                        )
                        target_entity_uuid = exist_target_entity.uuid

                # 处理关系
                if relation and source_entity_uuid and target_entity_uuid:
                    relationship = AddKnowledgeRelationshipParam(
                        knowledge_graph_uuid=uuid,
                        source_entity_uuid=source_entity_uuid,
                        target_entity_uuid=target_entity_uuid,
                        name=relation.get('Name'),
                        attributes='{}',
                        type=relation.get('Type'),
                        source=triple_source_hash_table_.get(source_id),
                    )
                    # 创建关系
                    await knowledge_relationship_service.add(obj=relationship)
                    relationships_written += 1
                processed_triples += 1
                if should_report(processed_triples, total_triples):
                    task_progress(
                        self,
                        '正在合并图谱数据',
                        scaled_progress(processed_triples, total_triples, 66, 98),
                        detail=f'已合并 {processed_triples}/{total_triples} 条三元组',
                        metrics={
                            'triples_done': processed_triples,
                            'triples_total': total_triples,
                            'entities': len(entity_names),
                            'relationships': relationships_written,
                        },
                    )

        # 完成任务
        return task_result(
            self,
            '知识图谱更新完毕',
            detail=f'已合并 {total_triples} 条三元组，涉及 {len(entity_names)} 个实体、{relationships_written} 条关系',
            metrics={'triples': total_triples, 'entities': len(entity_names), 'relationships': relationships_written},
        )

    except Exception as e:
        error_payload = {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e) or '知识图谱更新失败，请稍后重试',
                'type': e.__class__.__name__,
                'details': {'task_id': self.request.id, 'module': e.__class__.__module__},
            },
            'exc_type': f'{e.__class__.__module__}.{e.__class__.__name__}',
            'exc_message': str(e),
        }
        return task_error_result(self, error_payload)


@celery_app.task(bind=True, name='knowledge_graph.infer_knowledge_graph')
async def infer_knowledge_graph(self, uuid: str, user_token: str):
    """
    Celery task: Infer a knowledge graph with progress simulation.
    :param self: Celery task instance
    :param uuid: Knowledge graph UUID
    :param user_token: User JWT token
    """
    try:
        task_id = self.request.id
        # 初始化任务状态
        task_progress(self, '准备执行知识迁移', 3, detail='正在读取模型配置')

        # 获取用户信息和知识图谱
        api_key, base_url, model = await knowledge_graph_service.get_user_llm_info(user_token=user_token)
        knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
        knowledge_graph_data = GetKnowledgeGraphDetail(**select_as_dict(knowledge_graph))
        task_progress(
            self,
            '待推理图谱加载完成',
            14,
            detail=(
                f'已加载 {len(knowledge_graph_data.entities)} 个实体、{len(knowledge_graph_data.relationships)} 条关系'
            ),
            metrics={
                'entities': len(knowledge_graph_data.entities),
                'relationships': len(knowledge_graph_data.relationships),
            },
        )

        # 执行推理任务
        infer_graph = await knowledge_graph_service.infer(
            knowledge_graph=knowledge_graph_data,
            api_key=api_key,
            base_url=base_url,
            model=model,
            task_client=self,
        )
        infer_kg = infer_graph['infer_kg']
        infer_total = len(infer_kg)
        task_progress(
            self, '知识迁移完成', 75, detail=f'得到 {infer_total} 条候选三元组', metrics={'triples': infer_total}
        )
        processed_triples = 0
        entity_names = set()
        relationships_written = 0
        # 处理推理的三元组数据
        for triple in infer_kg:
            directional_entity = triple.get('DirectionalEntity')
            directed_entity = triple.get('DirectedEntity')
            relation = triple.get('Relation')
            source_entity_uuid, target_entity_uuid = None, None

            # 处理头实体
            if directional_entity:
                entity_names.add(directional_entity.get('Name'))
                source_entity = AddKnowledgeEntityParam(
                    knowledge_graph_uuid=uuid,
                    name=directional_entity.get('Name'),
                    type=directional_entity.get('Type'),
                    attributes=json.dumps(directional_entity.get('Attributes')),
                )
                try:
                    # 如果数据库没有实体，则新建
                    source_entity_uuid = await knowledge_entity_service.add(obj=source_entity)
                except ForbiddenError:
                    exist_source_entity = await knowledge_entity_service.get_knowledge_entity(
                        name=source_entity.name, knowledge_graph_uuid=source_entity.knowledge_graph_uuid
                    )
                    source_entity_uuid = exist_source_entity.uuid

            # 处理尾实体
            if directed_entity:
                entity_names.add(directed_entity.get('Name'))
                target_entity = AddKnowledgeEntityParam(
                    knowledge_graph_uuid=uuid,
                    name=directed_entity.get('Name'),
                    type=directed_entity.get('Type'),
                    attributes=json.dumps(directed_entity.get('Attributes')),
                )
                try:
                    # 如果数据库没有，则新建
                    target_entity_uuid = await knowledge_entity_service.add(obj=target_entity)
                except ForbiddenError:
                    exist_target_entity = await knowledge_entity_service.get_knowledge_entity(
                        name=target_entity.name, knowledge_graph_uuid=target_entity.knowledge_graph_uuid
                    )
                    target_entity_uuid = exist_target_entity.uuid

            # 处理关系
            if relation and source_entity_uuid and target_entity_uuid:
                source = ''  # 保持原代码中 source 为空字符串
                relationship = AddKnowledgeRelationshipParam(
                    knowledge_graph_uuid=uuid,
                    source_entity_uuid=source_entity_uuid,
                    target_entity_uuid=target_entity_uuid,
                    name=relation.get('Name'),
                    attributes='{}',
                    type=relation.get('Type'),
                    source=source,
                )
                try:
                    # 创建关系
                    await knowledge_relationship_service.add(obj=relationship)
                    relationships_written += 1
                except Exception as e:
                    logger.error(f'Task {task_id} failed to add relationship: {str(e)}')
            processed_triples += 1
            if should_report(processed_triples, infer_total):
                task_progress(
                    self,
                    '正在写入推理结果',
                    scaled_progress(processed_triples, infer_total, 76, 98),
                    detail=f'已处理 {processed_triples}/{infer_total} 条候选三元组',
                    metrics={
                        'triples_done': processed_triples,
                        'triples_total': infer_total,
                        'entities': len(entity_names),
                        'relationships': relationships_written,
                    },
                )

        # 完成任务
        return task_result(
            self,
            '知识迁移完成',
            detail=f'已处理 {infer_total} 条候选三元组，写入 {relationships_written} 条新关系',
            metrics={'triples': infer_total, 'entities': len(entity_names), 'relationships': relationships_written},
        )

    except Exception as e:
        error_payload = {
            'error': {
                'code': 'INTERNAL_ERROR',
                    'message': str(e) or '知识迁移失败，请稍后重试',
                'type': e.__class__.__name__,
                'details': {'task_id': self.request.id, 'module': e.__class__.__module__},
            },
            'exc_type': f'{e.__class__.__module__}.{e.__class__.__name__}',
            'exc_message': str(e),
        }
        return task_error_result(self, error_payload)


@router.delete(
    '/{uuid}',
    summary='（批量）删除实例图谱',
    dependencies=[Depends(RequestPermission('sys:knowledge_graph:del'))],
)
async def delete_knowledge_graph(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=uuid)
    count = await knowledge_graph_service.delete(uuid=uuid)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/status',
    summary='更新实例图谱状态',
    dependencies=[Depends(RequestPermission('sys:knowledge_graph:status'))],
)
async def update_knowledge_graph_status(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, pk=pk)
    count = await knowledge_graph_service.update_status(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
