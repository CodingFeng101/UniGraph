#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import json
import logging
from typing import Annotated

import anyio
from fastapi import APIRouter, Depends, File, Form, Path, Query, Request, UploadFile
from fastapi.responses import StreamingResponse

from backend.app.kgbase.schema import GetIndexDetail, GetKnowledgeGraphDetail, GetSchemaGraphDetail
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
from backend.app.kgbase.service.community_service import community_service
from backend.app.kgbase.service.embedding_service import embedding_service
from backend.app.kgbase.service.knowledge_entity_service import knowledge_entity_service
from backend.app.kgbase.service.knowledge_graph_service import knowledge_graph_service
from backend.app.kgbase.service.knowledge_relationship_service import knowledge_relationship_service
from backend.app.kgbase.service.schema_graph_service import schema_graph_service
from backend.app.task.celery import celery_app
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import CustomResponse, ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.task_progress import scaled_progress, should_report, task_error_result, task_progress, task_result
from backend.core.conf import settings
from backend.database.db_mysql import CurrentSession
from backend.utils.serializers import select_as_dict

logger = logging.getLogger(__name__)

# 定义心跳间隔（50秒）
HEARTBEAT_INTERVAL = 50

router = APIRouter()


# 心跳机制，保持发起QA请求时保持链接活跃
async def merge_async_generators(*gens):
    """
    合并多个异步生成器，按照产生的顺序返回结果
    """
    queue = asyncio.Queue()

    async def run_generator(gen):
        try:
            async for item in gen:
                await queue.put(item)
        except Exception:
            await queue.put(None)  # 作为错误信号
        finally:
            if not queue.empty():
                await queue.put(None)  # 结束信号

    try:
        # 创建取消作用域
        async with anyio.create_task_group() as tg:
            for gen in gens:
                tg.start_soon(run_generator, gen)

            while True:
                item = await queue.get()
                if item is None:  # 收到结束信号
                    break
                yield item
                queue.task_done()
    except anyio.get_cancelled_exc_class():
        # 取消时不做特殊处理，让上层处理
        raise
    except Exception:
        raise


@router.get('/all/{kg_base_uuid}', summary='获取kgbase下所有实例图谱', dependencies=[DependsJwtAuth])
async def get_all_knowledge_graphs(kg_base_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    knowledge_graphs = await knowledge_graph_service.get_all(kg_base_uuid=kg_base_uuid)
    data = [KnowledgeGraphResponse(**select_as_dict(knowledge_graph)) for knowledge_graph in knowledge_graphs]
    return response_base.success(data=data)


@router.get('/{uuid}', summary='获取实例图谱详情', dependencies=[DependsJwtAuth])
async def get_knowledge_graph(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
    data = GetKnowledgeGraphDetail(**select_as_dict(knowledge_graph))
    return response_base.success(data=data)


@router.get('/explore/{uuid}/overview', summary='获取渐进式图谱概览', dependencies=[DependsJwtAuth])
async def get_exploration_overview(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    data = await knowledge_graph_service.get_exploration_overview(uuid=uuid)
    return response_base.success(data=data)


@router.get('/explore/{uuid}/type', summary='按实体类型展开图谱', dependencies=[DependsJwtAuth])
async def get_exploration_type(
    uuid: Annotated[str, Path(...)],
    entity_type: Annotated[str, Query(...)],
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
) -> ResponseModel:
    result = await knowledge_graph_service.get_exploration_type(uuid=uuid, entity_type=entity_type, limit=limit)
    return response_base.success(
        data={
            'entities': [select_as_dict(entity) for entity in result['entities']],
            'relationships': [select_as_dict(item) for item in result['relationships']],
        }
    )


@router.get('/explore/{uuid}/neighbors/{entity_uuid}', summary='按跳数展开实体邻居', dependencies=[DependsJwtAuth])
async def get_exploration_neighbors(
    uuid: Annotated[str, Path(...)],
    entity_uuid: Annotated[str, Path(...)],
    depth: Annotated[int, Query(ge=1, le=5)] = 1,
    limit: Annotated[int, Query(ge=1, le=500)] = 300,
) -> ResponseModel:
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
async def get_depth(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    depth = await knowledge_graph_service.get_depth(uuid=uuid)
    return response_base.success(data=depth)


@router.post('/export-index-file/{uuid}', summary='将索引导出为文件', dependencies=[DependsJwtAuth])
async def export_knowledge_graph_index_file(uuid: Annotated[str, Path(...)]) -> ResponseModel:
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
async def export_knowledge_graph_index_url(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    url = f'{settings.INDEX_EXPORT_URL_ROOT}/{uuid}'
    return response_base.success(data={'url': url})


@router.post('/import-index', summary='导入索引', dependencies=[DependsJwtAuth])
async def import_knowledge_graph_index(
    knowledge_graph_uuid: str = Form(...), file: UploadFile = File(...)
) -> ResponseModel:
    try:
        # 读取文件内容
        file_content = await file.read()
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


@router.post('/ask/{uuid}', summary='基于索引进行问答', dependencies=[DependsJwtAuth])
async def ask_knowledge_graph(uuid: Annotated[str, Path(...)], obj: AskKnowledgeGraphParam):
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
                yield (
                    json.dumps(
                        {'type': 'processing', 'message': '正在解析问题', 'detail': '已接收问题，开始准备查询上下文'},
                        ensure_ascii=False,
                    )
                    + '\n'
                )
                # 获取用户信息和知识图谱
                api_key, base_url, model = await knowledge_graph_service.get_user_llm_info(user_token=obj.user_token)
                yield (
                    json.dumps(
                        {'type': 'processing', 'message': '模型配置加载完成', 'detail': f'将使用 {model} 生成回答'},
                        ensure_ascii=False,
                    )
                    + '\n'
                )
                knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
                data = GetIndexDetail(**select_as_dict(knowledge_graph))
                yield (
                    json.dumps(
                        {
                            'type': 'processing',
                            'message': '知识索引加载完成',
                            'detail': (
                                f'已载入 {len(data.entities)} 个实体、{len(data.relationships)} 条关系'
                                f'和 {len(data.communities)} 份社区报告'
                            ),
                        },
                        ensure_ascii=False,
                    )
                    + '\n'
                )

                # 执行查询
                yield (
                    json.dumps(
                        {
                            'type': 'processing',
                            'message': '正在检索实体与关系',
                            'detail': '正在构建与问题相关的局部知识上下文',
                        },
                        ensure_ascii=False,
                    )
                    + '\n'
                )
                response = await knowledge_graph_service.query(
                    knowledge_graph=data,
                    query=obj.message,
                    infer=obj.infer,
                    depth=obj.depth,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                )
                yield (
                    json.dumps(
                        {
                            'type': 'processing',
                            'message': '正在整理回答',
                            'detail': '知识检索完成，正在汇总回答与信息源',
                        },
                        ensure_ascii=False,
                    )
                    + '\n'
                )

                # 返回成功结果（保持原有 ResponseModel 格式）
                yield json.dumps({'type': 'final_result', 'data': response, 'code': 200, 'msg': 'success'}) + '\n'

            except asyncio.TimeoutError as e:
                yield json.dumps({'type': 'error', 'code': 500, 'msg': str(e)}) + '\n'
            except Exception as e:
                yield json.dumps({'type': 'error', 'code': 500, 'msg': str(e)}) + '\n'
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
                'message': '任务失败, 请检查API账户并稍后重试!',
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
                    except Exception:
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
                    except Exception:
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
                    except Exception:
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
                    except Exception:
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
                'message': '任务失败, 请检查API账户并稍后重试!',
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
        task_progress(self, '准备执行知识推理', 3, detail='正在读取模型配置')

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
            self, '知识推理完成', 75, detail=f'得到 {infer_total} 条候选三元组', metrics={'triples': infer_total}
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
                except Exception:
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
                except Exception:
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
            '知识推理完成',
            detail=f'已处理 {infer_total} 条候选三元组，写入 {relationships_written} 条新关系',
            metrics={'triples': infer_total, 'entities': len(entity_names), 'relationships': relationships_written},
        )

    except Exception as e:
        error_payload = {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '任务失败, 请检查API账户并稍后重试!',
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
async def delete_knowledge_graph(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    count = await knowledge_graph_service.delete(uuid=uuid)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/status',
    summary='更新实例图谱状态',
    dependencies=[Depends(RequestPermission('sys:knowledge_graph:status'))],
)
async def update_knowledge_graph_status(pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await knowledge_graph_service.update_status(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
