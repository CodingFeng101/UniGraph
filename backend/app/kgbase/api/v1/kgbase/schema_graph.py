#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.app.kgbase.schema import GetSchemaGraphDetail
from backend.app.kgbase.schema.schema_entity import AddSchemaEntityParam
from backend.app.kgbase.schema.schema_graph import (
    AddSchemaGraphParam,
    ImportSchemaGraphParam,
    SchemaGraphResponse,
    UpdateSchemaGraphBase,
    UpdateSchemaGraphParam,
)
from backend.app.kgbase.schema.schema_relationship import AddSchemaRelationshipParam
from backend.app.kgbase.service.ownership_service import ownership_service
from backend.app.kgbase.service.schema_entity_service import schema_entity_service
from backend.app.kgbase.service.schema_graph_service import resolve_local_file_path, schema_graph_service
from backend.app.kgbase.service.schema_relationship_service import schema_relationship_service
from backend.app.task.celery import celery_app
from backend.common.exception.errors import NotFoundError
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.task_progress import scaled_progress, should_report, task_error_result, task_progress, task_result
from backend.database.db_mysql import CurrentSession
from backend.utils.serializers import select_as_dict

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/all/{kg_base_uuid}', summary='获取kgbase下所有架构图谱', dependencies=[DependsJwtAuth])
async def get_all_schema_graphs(request: Request, kg_base_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_kg_base(user_uuid=request.user.uuid, uuid=kg_base_uuid)
    schema_graphs = await schema_graph_service.get_all(kg_base_uuid=kg_base_uuid)
    data = [SchemaGraphResponse(**select_as_dict(schema_graph)) for schema_graph in schema_graphs]
    return response_base.success(data=data)


@router.get('/{uuid}', summary='获取架构图谱详情', dependencies=[DependsJwtAuth])
async def get_schema_graph(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_schema_graph(user_uuid=request.user.uuid, uuid=uuid)
    schema_graph = await schema_graph_service.get_schema_graph(uuid=uuid)
    data = GetSchemaGraphDetail(**select_as_dict(schema_graph))
    return response_base.success(data=data)


@router.get(
    '',
    summary='（模糊条件）分页获取所有架构图谱',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_schema_graphs(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseModel:
    schema_graph_select = await schema_graph_service.get_select(user_uuid=request.user.uuid, name=name, status=status)
    page_data = await paging_data(db, schema_graph_select, SchemaGraphResponse)
    return response_base.success(data=page_data)


@router.get(
    '/export/{uuid}',
    summary='导出选中架构',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def export_schema_graph(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_schema_graph(user_uuid=request.user.uuid, uuid=uuid)
    schema_graph = await schema_graph_service.get_schema_graph(uuid=uuid)

    # 处理 entities
    entities = []
    for entity in schema_graph.entities:
        entities.append({
            'name': entity.name,
            'attributes': json.loads(entity.attributes),
            'definition': entity.definition,
            'uuid': entity.uuid,
            'source': json.loads(entity.source),
        })

    # 处理 relationships
    relationships = []
    for relationship in schema_graph.relationships:
        relationships.append({
            'name': relationship.name,
            'attributes': relationship.attributes,
            'definition': relationship.definition,
            'source_entity_uuid': relationship.source_entity_uuid,
            'target_entity_uuid': relationship.target_entity_uuid,
            'source': json.loads(relationship.source),
        })

    definition = {}
    for i in relationships:
        definition[i['name']] = i['definition']
    for i in entities:
        definition[i['name']] = i['definition']

    def get_triples(relations, entities):
        # 创建一个字典，用于根据uuid快速查找entity
        entity_dict = {entity['uuid']: entity for entity in entities}

        triples = []

        for relation in relations:
            source_entity = entity_dict.get(relation['source_entity_uuid'])
            target_entity = entity_dict.get(relation['target_entity_uuid'])

            if source_entity and target_entity:
                # 构造三元组
                triple = (
                    (source_entity['name'], source_entity['attributes'], source_entity['source']),
                    (relation['name'], relation['source']),
                    (target_entity['name'], target_entity['attributes'], target_entity['source']),
                )
                triples.append(triple)

        return triples

    # 获取三元组
    triples = get_triples(relationships, entities)

    def transform_triples(triples):
        result = []
        relation_sources = {}

        # 先提取所有关系及其来源信息
        for triple in triples:
            _, relation, _ = triple
            if isinstance(relation, tuple) and len(relation) == 2:
                relation_name, sources = relation
                if relation_name not in relation_sources:
                    relation_sources[relation_name] = sources

        # 生成 schema 结构
        for triple in triples:
            source_entity, relation, target_entity = triple

            # 获取关系名
            if isinstance(relation, tuple) and len(relation) == 2:
                relation_name, _ = relation
            else:
                relation_name = relation

            # 构造 schema 部分
            schema = {
                'DirectionalEntityType': {'Name': source_entity[0], 'Attributes': source_entity[1]},
                'RelationType': relation[0],
                'DirectedEntityType': {'Name': target_entity[0], 'Attributes': target_entity[1]},
            }

            # 构造 source 部分
            source_data = {}
            if relation_name in relation_sources and relation_sources[relation_name]:
                for key, value in relation_sources[relation_name].items():
                    entities = key.strip('() ').split(', ')
                    if len(entities) == 3 and entities[0] in source_entity[2] and entities[2] in target_entity[2]:
                        source_data[key] = value

            # 构造完整的字典
            transformed = {'schema': schema, 'source': source_data}

            result.append(transformed)

        return result

    # 转换三元组
    kg_schema = transform_triples(triples)

    # 构造最终返回的数据
    result = {
        'name': schema_graph.name,
        'aim': schema_graph.aim,
        'kg_schema': kg_schema,
        'definition': definition,
        'modify_info': schema_graph.modify_info,
        'modify_suggestion': schema_graph.modify_suggestion,
    }

    return response_base.success(data=result)


@router.post(
    '/import',
    summary='导入知识架构',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:schema_graph:add'))],
)
async def import_schema_graph(request: Request, obj: ImportSchemaGraphParam) -> ResponseModel:
    await ownership_service.require_kg_base(user_uuid=request.user.uuid, uuid=obj.data.kg_base_uuid)
    for file_path in obj.file_paths:
        # 从文件中读取架构以及架构的定义（都存储在kg_schema中）
        try:
            with open(resolve_local_file_path(file_path), 'r', encoding='utf-8') as file:
                json_string = file.read()
                kg_schema_info = json.loads(json_string)
        except FileNotFoundError:
            return response_base.fail(message='文件未找到')
        schema = kg_schema_info.get('kg_schema')
        schema_definition = kg_schema_info.get('definition')
        name = kg_schema_info.get('name')
        aim = kg_schema_info.get('aim')
        modify_info = kg_schema_info.get('modify_info')
        modify_suggestion = kg_schema_info.get('modify_suggestion')
        # 将该架构的aim和name临时加载到data里
        obj.data.aim = aim
        obj.data.name = name
        obj.data.modify_info = modify_info
        obj.data.modify_suggestion = modify_suggestion
        schema_uuid = await schema_graph_service.add(obj=obj.data)
        # 从架构中获取实体类型的source
        entity_source = {}

        for item in schema:
            # 提取 DirectionalEntityType 和 DirectedEntityType 的名称
            directional_entity = item['schema']['DirectionalEntityType']['Name']
            directed_entity = item['schema']['DirectedEntityType']['Name']

            # 提取 source 中的实体名称
            try:
                source_key = next(iter(item['source'].keys()))  # 获取 source 字典的第一个键
                source_entities = source_key.strip('()').split(', ')  # 去掉括号并按逗号分割

                # 将实体名称添加到结果字典中
                if directional_entity not in entity_source:
                    entity_source[directional_entity] = []
                if directed_entity not in entity_source:
                    entity_source[directed_entity] = []

                # 添加 source 中的实体名称
                entity_source[directional_entity].append(source_entities[0])
                entity_source[directed_entity].append(source_entities[2])
            except StopIteration:
                continue

        # 去重并保持顺序
        for key in entity_source:
            entity_source[key] = list(dict.fromkeys(entity_source[key]))

        # 从架构中得到关系类型的source
        relation_source = {}

        for item in schema:
            relation_type = item['schema']['RelationType']  # 获取关系类型
            sources = item['source']  # 获取 source 字典

            # 如果关系类型不存在于结果字典中，则初始化一个空字典
            if relation_type not in relation_source:
                relation_source[relation_type] = {}

            # 将当前 item 的 source 合并到结果字典中
            relation_source[relation_type].update(sources)

        # 遍历提取的架构数据，处理实体和关系
        for item in schema:
            item = item.get('schema')
            directional_entity = item.get('DirectionalEntityType')
            directed_entity = item.get('DirectedEntityType')
            target_entity_uuid, source_entity_uuid = None, None

            # 处理源实体 (DirectionalEntity)
            if directional_entity:
                try:
                    entity = await schema_entity_service.get_schema_entity(
                        name=directional_entity.get('Name'), schema_graph_uuid=schema_uuid
                    )
                    source_entity_uuid = entity.uuid  # 如果实体已存在，则获取其 uuid
                except NotFoundError:
                    # 如果实体不存在，则创建新的实体
                    source_entity = AddSchemaEntityParam(
                        schema_graph_uuid=schema_uuid,
                        name=directional_entity.get('Name'),
                        attributes=json.dumps(directional_entity.get('Attributes')),
                        definition=schema_definition.get(directional_entity.get('Name')),
                        source=json.dumps(entity_source.get(directional_entity.get('Name'))),
                    )
                    source_entity_uuid = await schema_entity_service.add(obj=source_entity)

            # 处理目标实体 (DirectedEntity)
            if directed_entity:
                try:
                    entity = await schema_entity_service.get_schema_entity(
                        name=directed_entity.get('Name'), schema_graph_uuid=schema_uuid
                    )
                    target_entity_uuid = entity.uuid  # 如果实体已存在，则获取其 uuid
                except NotFoundError:
                    # 如果实体不存在，则创建新的实体
                    target_entity = AddSchemaEntityParam(
                        schema_graph_uuid=schema_uuid,
                        name=directed_entity.get('Name'),
                        attributes=json.dumps(directed_entity.get('Attributes')),
                        definition=schema_definition.get(directed_entity.get('Name')),
                        source=json.dumps(entity_source.get(directed_entity.get('Name'))),
                    )
                    target_entity_uuid = await schema_entity_service.add(obj=target_entity)

            # 处理关系 (Relationship)
            relationship = item.get('RelationType')
            if source_entity_uuid and target_entity_uuid and relationship:
                schema_relationship = AddSchemaRelationshipParam(
                    target_entity_uuid=target_entity_uuid,
                    source_entity_uuid=source_entity_uuid,
                    schema_graph_uuid=schema_uuid,
                    type=relationship,
                    name=relationship,
                    definition=schema_definition.get(relationship),
                    source=json.dumps(relation_source.get(relationship)),
                )
                # 创建关系
                await schema_relationship_service.add(obj=schema_relationship)

        # 返回成功响应
        return response_base.success()


@celery_app.task(bind=True, name='schema_graph.create_schema_graph')
async def create_schema_graph(self, user_token: str, obj_data: dict):
    """
    Celery task: Create a schema graph with progress simulation.
    :param self: Celery task instance
    :param user_token: User JWT token
    :param obj_data: Serialized AddSchemaGraphParam data (JSON string)
    """
    try:
        # 初始化任务状态
        task_progress(self, '准备创建知识架构', 3, detail='正在校验架构名称、需求和文档')

        # 反序列化参数
        obj_dict = obj_data
        obj = AddSchemaGraphParam(**obj_dict)

        # 获取用户信息
        api_key, base_url, model = await schema_graph_service.get_user_llm_info(user_token=user_token)
        embedding_api_key, embedding_base_url, embedding_model = await schema_graph_service.get_user_embedding_info(
            user_token=user_token
        )
        task_progress(
            self,
            '架构资料已就绪',
            10,
            detail=f'待分析 {len(obj.file_paths)} 个文件',
            metrics={'files': len(obj.file_paths)},
        )

        # 初始化建议信息，防止为空时读取出错
        obj.data.modify_info = json.dumps({'add_entity': [], 'del_entity': []})
        obj.data.modify_suggestion = ' '

        # 调用 schema_service 创建图谱
        schema_uuid = await schema_graph_service.add(obj=obj.data)

        def report_schema_progress(stage, completed, total, constraints):
            if stage == 'extract' and should_report(completed, total):
                task_progress(
                    self,
                    '正在分析文档中的类型约束',
                    scaled_progress(completed, total, 12, 48),
                    detail=f'已分析 {completed}/{total} 个文本片段，累计识别 {constraints} 条类型约束',
                    metrics={'chunks_done': completed, 'chunks_total': total, 'constraints': constraints},
                )
            elif stage == 'definitions':
                task_progress(
                    self,
                    '正在生成类型定义' if completed < total else '类型定义生成完成',
                    50 if completed < total else 60,
                    detail=f'共需定义 {total} 个实体与关系类型' if completed < total else f'已完成 {total} 个类型定义',
                    metrics={'definitions_done': completed, 'definitions_total': total},
                )

        # 创建架构
        schema, schema_definition = await schema_graph_service.create_schema(
            file_paths=obj.file_paths,
            aim=obj.data.aim,
            api_key=api_key,
            base_url=base_url,
            model=model,
            embedding_api_key=embedding_api_key,
            embedding_base_url=embedding_base_url,
            embedding_model=embedding_model,
            progress_callback=report_schema_progress,
        )
        entity_types = {
            entity.get('Name')
            for item in schema
            for entity in (
                item.get('schema', {}).get('DirectionalEntityType', {}),
                item.get('schema', {}).get('DirectedEntityType', {}),
            )
            if entity.get('Name')
        }
        relationship_types = {item.get('schema', {}).get('RelationType') for item in schema}
        relationship_types.discard(None)
        task_progress(
            self,
            '知识架构生成完成',
            62,
            detail=f'识别 {len(entity_types)} 类实体、{len(relationship_types)} 类关系，共 {len(schema)} 条类型约束',
            metrics={
                'entity_types': len(entity_types),
                'relationship_types': len(relationship_types),
                'constraints': len(schema),
            },
        )

        # 从架构中获取实体类型的source
        entity_source = {}
        schema_total = len(schema)
        for item in schema:
            directional_entity = item['schema']['DirectionalEntityType']['Name']
            directed_entity = item['schema']['DirectedEntityType']['Name']
            source_key = next(iter(item['source'].keys()))  # 获取 source 字典的第一个键
            source_entities = source_key.strip('()').split(', ')  # 去掉括号并按逗号分割

            if directional_entity not in entity_source:
                entity_source[directional_entity] = []
            if directed_entity not in entity_source:
                entity_source[directed_entity] = []

            entity_source[directional_entity].append(source_entities[0])
            entity_source[directed_entity].append(source_entities[2])

        # 去重并保持顺序
        for key in entity_source:
            entity_source[key] = list(dict.fromkeys(entity_source[key]))

        # 从架构中得到关系类型的source
        relation_source = {}
        for item in schema:
            relation_type = item['schema']['RelationType']
            sources = item['source']

            if relation_type not in relation_source:
                relation_source[relation_type] = {}
            relation_source[relation_type].update(sources)

        # 遍历提取的架构数据，处理实体和关系
        for schema_index, item in enumerate(schema, start=1):
            item = item.get('schema')
            directional_entity = item.get('DirectionalEntityType')
            directed_entity = item.get('DirectedEntityType')
            target_entity_uuid, source_entity_uuid = None, None

            # 处理源实体 (DirectionalEntity)
            if directional_entity:
                try:
                    entity = await schema_entity_service.get_schema_entity(
                        name=directional_entity.get('Name'), schema_graph_uuid=schema_uuid
                    )
                    source_entity_uuid = entity.uuid
                except NotFoundError:
                    source_entity = AddSchemaEntityParam(
                        schema_graph_uuid=schema_uuid,
                        name=directional_entity.get('Name'),
                        attributes=json.dumps(directional_entity.get('Attributes')),
                        definition=schema_definition.get(directional_entity.get('Name')),
                        source=json.dumps(entity_source.get(directional_entity.get('Name'))),
                    )
                    source_entity_uuid = await schema_entity_service.add(obj=source_entity)

            # 处理目标实体 (DirectedEntity)
            if directed_entity:
                try:
                    entity = await schema_entity_service.get_schema_entity(
                        name=directed_entity.get('Name'), schema_graph_uuid=schema_uuid
                    )
                    target_entity_uuid = entity.uuid
                except NotFoundError:
                    target_entity = AddSchemaEntityParam(
                        schema_graph_uuid=schema_uuid,
                        name=directed_entity.get('Name'),
                        attributes=json.dumps(directed_entity.get('Attributes')),
                        definition=schema_definition.get(directed_entity.get('Name')),
                        source=json.dumps(entity_source.get(directed_entity.get('Name'))),
                    )
                    target_entity_uuid = await schema_entity_service.add(obj=target_entity)

            # 处理关系 (Relationship)
            relationship = item.get('RelationType')
            if source_entity_uuid and target_entity_uuid and relationship:
                schema_relationship = AddSchemaRelationshipParam(
                    target_entity_uuid=target_entity_uuid,
                    source_entity_uuid=source_entity_uuid,
                    schema_graph_uuid=schema_uuid,
                    type=relationship,
                    name=relationship,
                    definition=schema_definition.get(relationship),
                    source=json.dumps(relation_source.get(relationship)),
                )
                await schema_relationship_service.add(obj=schema_relationship)
            if should_report(schema_index, schema_total):
                task_progress(
                    self,
                    '正在保存架构类型',
                    scaled_progress(schema_index, schema_total, 64, 98),
                    detail=f'已保存 {schema_index}/{schema_total} 条类型约束',
                    metrics={'constraints_done': schema_index, 'constraints_total': schema_total},
                )

        # 完成任务
        return task_result(
            self,
            '知识架构创建完毕',
            detail=f'已生成 {len(entity_types)} 类实体、{len(relationship_types)} 类关系',
            metrics={'entity_types': len(entity_types), 'relationship_types': len(relationship_types)},
        )

    except Exception as e:
        error_payload = {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '新建知识架构已存在！'
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


@celery_app.task(bind=True, name='schema_graph.update_schema_graph')
async def update_schema_graph(self, uuid: str, user_token: str, obj_data: dict):
    """
    Celery task: Update a schema graph with progress simulation.
    :param self: Celery task instance
    :param uuid: Schema graph UUID
    :param user_token: User JWT token
    :param obj_data: Serialized UpdateSchemaGraphParam data (JSON string)
    """
    try:
        # 获取当前任务的id，以便查询对应长耗时异步API的状态信息，并针对性采取任务热重载
        # 初始化任务状态
        task_progress(self, '准备更新知识架构', 3, detail='正在读取原架构与更新资料')

        # 反序列化参数
        obj_dict = obj_data
        obj = UpdateSchemaGraphParam(**obj_dict)

        # 获取用户信息和架构图谱
        api_key, base_url, model = await schema_graph_service.get_user_llm_info(user_token=user_token)
        embedding_api_key, embedding_base_url, embedding_model = await schema_graph_service.get_user_embedding_info(
            user_token=user_token
        )
        task_progress(
            self,
            '架构更新资料已就绪',
            10,
            detail=f'待分析 {len(obj.file_paths)} 个文件',
            metrics={'files': len(obj.file_paths)},
        )

        pre_schema_graph = await schema_graph_service.get_schema_graph(uuid=uuid)
        obj.data.aim = pre_schema_graph.aim

        # 更新架构图谱
        schema_uuid = await schema_graph_service.update(uuid=uuid, obj=obj.data)

        if schema_uuid > 0:
            schema_graph = await schema_graph_service.get_schema_graph(uuid=uuid, name=pre_schema_graph.name)
            schema_data = GetSchemaGraphDetail(**select_as_dict(schema_graph))

            def report_schema_progress(stage, completed, total, constraints):
                if stage == 'extract' and should_report(completed, total):
                    task_progress(
                        self,
                        '正在分析增量文档',
                        scaled_progress(completed, total, 12, 48),
                        detail=f'已分析 {completed}/{total} 个文本片段，当前共有 {constraints} 条类型约束',
                        metrics={'chunks_done': completed, 'chunks_total': total, 'constraints': constraints},
                    )
                elif stage == 'definitions':
                    task_progress(
                        self,
                        '正在更新类型定义' if completed < total else '类型定义更新完成',
                        50 if completed < total else 60,
                        detail=f'共需处理 {total} 个实体与关系类型'
                        if completed < total
                        else f'已完成 {total} 个类型定义',
                        metrics={'definitions_done': completed, 'definitions_total': total},
                    )

            # 执行更新架构任务
            schema, schema_definition = await schema_graph_service.update_schema(
                file_paths=obj.file_paths,
                schema=schema_data,
                api_key=api_key,
                base_url=base_url,
                model=model,
                embedding_api_key=embedding_api_key,
                embedding_base_url=embedding_base_url,
                embedding_model=embedding_model,
                progress_callback=report_schema_progress,
            )
            entity_types = {
                entity.get('Name')
                for item in schema
                for entity in (
                    item.get('schema', {}).get('DirectionalEntityType', {}),
                    item.get('schema', {}).get('DirectedEntityType', {}),
                )
                if entity.get('Name')
            }
            relationship_types = {item.get('schema', {}).get('RelationType') for item in schema}
            relationship_types.discard(None)
            task_progress(
                self,
                '架构增量分析完成',
                62,
                detail=(
                    f'得到 {len(entity_types)} 类实体、{len(relationship_types)} 类关系，共 {len(schema)} 条类型约束'
                ),
                metrics={
                    'entity_types': len(entity_types),
                    'relationship_types': len(relationship_types),
                    'constraints': len(schema),
                },
            )

            # 从架构中获取实体类型的source
            entity_source = {}
            schema_total = len(schema)
            for item in schema:
                if item['source']:
                    directional_entity = item['schema']['DirectionalEntityType']['Name']
                    directed_entity = item['schema']['DirectedEntityType']['Name']
                    source_key = next(iter(item['source'].keys()))  # 获取 source 字典的第一个键
                    source_entities = source_key.strip('()').split(', ')  # 去掉括号并按逗号分割

                    if directional_entity not in entity_source:
                        entity_source[directional_entity] = []
                    if directed_entity not in entity_source:
                        entity_source[directed_entity] = []

                    entity_source[directional_entity].append(source_entities[0])
                    entity_source[directed_entity].append(source_entities[2])

            # 去重并保持顺序
            for key in entity_source:
                entity_source[key] = list(dict.fromkeys(entity_source[key]))

            # 从架构中得到关系类型的source
            relation_source = {}
            for item in schema:
                if item['source']:
                    relation_type = item['schema']['RelationType']
                    sources = item['source']

                    if relation_type not in relation_source:
                        relation_source[relation_type] = {}
                    relation_source[relation_type].update(sources)

            # 遍历提取的架构数据，处理实体和关系
            for schema_index, item in enumerate(schema, start=1):
                item = item.get('schema')
                directional_entity = item.get('DirectionalEntityType')
                directed_entity = item.get('DirectedEntityType')
                target_entity_uuid, source_entity_uuid = None, None

                # 处理源实体 (DirectionalEntity)
                if directional_entity:
                    try:
                        entity = await schema_entity_service.get_schema_entity(
                            name=directional_entity.get('Name'), schema_graph_uuid=uuid
                        )
                        source_entity_uuid = entity.uuid
                    except NotFoundError:
                        source_entity = AddSchemaEntityParam(
                            schema_graph_uuid=uuid,
                            name=directional_entity.get('Name'),
                            attributes=json.dumps(directional_entity.get('Attributes')),
                            definition=schema_definition.get(directional_entity.get('Name')),
                            source=json.dumps(entity_source.get(directional_entity.get('Name'))),
                        )
                        source_entity_uuid = await schema_entity_service.add(obj=source_entity)

                # 处理目标实体 (DirectedEntity)
                if directed_entity:
                    try:
                        entity = await schema_entity_service.get_schema_entity(
                            name=directed_entity.get('Name'), schema_graph_uuid=uuid
                        )
                        target_entity_uuid = entity.uuid
                    except NotFoundError:
                        target_entity = AddSchemaEntityParam(
                            schema_graph_uuid=uuid,
                            name=directed_entity.get('Name'),
                            attributes=json.dumps(directed_entity.get('Attributes')),
                            definition=schema_definition.get(directed_entity.get('Name')),
                            source=json.dumps(entity_source.get(directed_entity.get('Name'))),
                        )
                        target_entity_uuid = await schema_entity_service.add(obj=target_entity)

                # 处理关系 (Relationship)
                relationship = item.get('RelationType')
                if source_entity_uuid and target_entity_uuid and relationship:
                    schema_relationship = AddSchemaRelationshipParam(
                        target_entity_uuid=target_entity_uuid,
                        source_entity_uuid=source_entity_uuid,
                        schema_graph_uuid=uuid,
                        type=relationship,
                        name=relationship,
                        definition=schema_definition.get(relationship),
                        source=json.dumps(relation_source.get(relationship)),
                    )
                    await schema_relationship_service.add(obj=schema_relationship)
                if should_report(schema_index, schema_total):
                    task_progress(
                        self,
                        '正在合并架构类型',
                        scaled_progress(schema_index, schema_total, 64, 98),
                        detail=f'已合并 {schema_index}/{schema_total} 条类型约束',
                        metrics={'constraints_done': schema_index, 'constraints_total': schema_total},
                    )

        # 完成任务
        return task_result(self, '知识架构更新完毕', detail='架构类型与关系约束已完成合并')

    except Exception as e:
        is_conflict = e.__class__.__name__ == 'ForbiddenError'
        error_payload = {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '知识架构已存在' if is_conflict else (str(e) or '知识架构更新失败，请稍后重试'),
                'type': e.__class__.__name__,
                'details': {
                    'task_id': self.request.id,
                    'module': e.__class__.__module__,  # 获取当前模块名称
                    'uuid': uuid,  # 返回当前异步任务API UUID
                },
            },
            'exc_type': f'{e.__class__.__module__}.{e.__class__.__name__}',
            'exc_message': str(e),
        }

        return task_error_result(self, error_payload)


@router.delete(
    '/{uuid}',
    summary='（批量）删除架构图谱',
    dependencies=[Depends(RequestPermission('sys:schema_graph:del'))],
)
async def delete_schema_graph(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_schema_graph(user_uuid=request.user.uuid, uuid=uuid)
    count = await schema_graph_service.delete(uuid=uuid)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/status',
    summary='更新架构图谱状态',
    dependencies=[Depends(RequestPermission('sys:schema_graph:status'))],
)
async def update_schema_graph_status(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    await ownership_service.require_schema_graph(user_uuid=request.user.uuid, pk=pk)
    count = await schema_graph_service.update_status(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@celery_app.task(bind=True, name='schema_graph.update_schema_graph_suggestion')
async def update_schema_graph_suggestion(self, uuid: str, user_token: str):
    """
    Celery task: Update schema graph suggestion with progress simulation.
    :param self: Celery task instance
    :param uuid: Schema graph UUID
    :param user_token: User JWT token
    """
    try:
        # Initialize task state
        task_progress(self, '准备生成架构修改建议', 8, detail='正在读取当前架构和历史建议')
        # Get user info and schema graph
        api_key, base_url, model = await schema_graph_service.get_user_llm_info(user_token=user_token)
        schema_graph = await schema_graph_service.get_schema_graph(uuid=uuid)

        task_progress(self, '正在分析架构变更', 35, detail='模型正在归纳实体类型和关系类型的调整建议')
        # Execute suggestion update
        suggestion, modify_info = await schema_graph_service.update_suggestion(
            modify_info=schema_graph.modify_info,
            pre_suggestion=schema_graph.modify_suggestion,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        add_count = len(modify_info.get('add_entity', [])) if isinstance(modify_info, dict) else 0
        delete_count = len(modify_info.get('del_entity', [])) if isinstance(modify_info, dict) else 0
        task_progress(
            self,
            '架构修改建议生成完成',
            88,
            detail=f'识别 {add_count} 项新增建议、{delete_count} 项删除建议',
            metrics={'additions': add_count, 'deletions': delete_count},
        )

        # Update schema data
        data = UpdateSchemaGraphBase(
            aim=schema_graph.aim,
            name=schema_graph.name,
            modify_info=json.dumps(modify_info),
            modify_suggestion=suggestion,
        )
        await schema_graph_service.update(uuid=uuid, obj=data)

        # Complete task
        return task_result(
            self,
            '架构修改建议已更新',
            detail=f'已保存 {add_count + delete_count} 项变更建议',
            metrics={'additions': add_count, 'deletions': delete_count},
        )

    # 层级捕获API账户异常

    except Exception as e:
        error_payload = {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e) or '架构修改建议生成失败，请稍后重试',
                'type': e.__class__.__name__,
                'details': {'task_id': self.request.id, 'module': e.__class__.__module__},
            },
            'exc_type': f'{e.__class__.__module__}.{e.__class__.__name__}',
            'exc_message': str(e),
        }
        return task_error_result(self, error_payload)


@router.put(
    '/update/{uuid}',
    summary='更新架构图谱',
    dependencies=[
        Depends(RequestPermission('sys:schema_graph:edit')),
    ],
)
async def update_schema_detail(
    request: Request, uuid: Annotated[str, Path(...)], obj: UpdateSchemaGraphBase
) -> ResponseModel:
    await ownership_service.require_schema_graph(user_uuid=request.user.uuid, uuid=uuid)
    await schema_graph_service.update(uuid=uuid, obj=obj)
    return response_base.success()


def decode_unicode(data):
    if isinstance(data, list):
        # 如果是列表，递归处理每个元素
        return [decode_unicode(item) for item in data]
    elif isinstance(data, str):
        # 如果是字符串，尝试解码
        return data.encode('utf-8').decode('unicode_escape')
    else:
        # 其他数据类型直接返回
        return data
