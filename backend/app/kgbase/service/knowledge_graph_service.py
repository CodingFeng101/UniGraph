#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import List
from uuid import uuid4

import pandas as pd
from celery import Task
from fastapi import HTTPException, Request
from sqlalchemy import func, or_, select
from sqlalchemy.orm import aliased

from backend.app.kgbase.crud.crud_knowledge_graph import knowledge_graph_dao
from backend.app.kgbase.model import KnowledgeEntity, KnowledgeGraph, KnowledgeRelationship
from backend.app.kgbase.schema import GetIndexDetail, GetKnowledgeGraphDetail, GetSchemaGraphDetail
from backend.app.kgbase.schema.knowledge_graph import (
    KnowledgeGraphBase,
    UpdateKnowledgeGraphParam,
)
from backend.app.kgbase.service.llm_info_service import get_user_embedding_info, get_user_llm_info
from backend.common.core_layer.interface.kg_services import create_infer_kg, create_kg
from backend.common.core_layer.interface.query_service import build_index, query_kg
from backend.common.core_layer.unigraph.module.sapperrag.model.model_load import (
    load_community,
    load_entities,
    load_relationships,
)
from backend.common.core_layer.unigraph.module.sapperrag.utils import parse_json
from backend.common.exception import errors
from backend.common.security.jwt import superuser_verify
from backend.core.conf import settings
from backend.core.path_conf import FILES_DIR, STATIC_DIR, TEMP_DIR
from backend.database.db_mysql import async_db_session
from backend.database.db_redis import redis_client
from backend.scripts.init_data import logger

PERMANENT_TEMP_DIR = TEMP_DIR
os.makedirs(PERMANENT_TEMP_DIR, exist_ok=True)


def resolve_local_file_path(file_path: str) -> str:
    normalized = Path(file_path[2:] if file_path.startswith('./') else file_path)
    if normalized.is_absolute():
        candidate = normalized
    elif normalized.parts and normalized.parts[0] == 'static':
        candidate = Path(STATIC_DIR) / Path(*normalized.parts[1:])
    elif normalized.parts and normalized.parts[0] == 'files':
        candidate = Path(FILES_DIR) / Path(*normalized.parts[1:])
    else:
        raise FileNotFoundError('Uploaded file path is invalid')
    resolved = candidate.resolve()
    allowed_roots = (Path(STATIC_DIR).resolve(), Path(FILES_DIR).resolve())
    if not any(resolved == root or root in resolved.parents for root in allowed_roots):
        raise FileNotFoundError('Uploaded file is outside the managed upload directory')
    if not resolved.is_file():
        raise FileNotFoundError('Uploaded file does not exist')
    return str(resolved)


class KnowledgeGraphService:
    @staticmethod
    async def get_exploration_overview(*, uuid: str) -> dict:
        async with async_db_session() as db:
            rows = (
                await db.execute(
                    select(KnowledgeEntity.type, func.count(KnowledgeEntity.id))
                    .where(KnowledgeEntity.knowledge_graph_uuid == uuid)
                    .group_by(KnowledgeEntity.type)
                    .order_by(func.count(KnowledgeEntity.id).desc())
                )
            ).all()
            source_entity = aliased(KnowledgeEntity)
            target_entity = aliased(KnowledgeEntity)
            relationship_rows = (
                await db.execute(
                    select(
                        source_entity.type,
                        target_entity.type,
                        func.count(KnowledgeRelationship.id),
                    )
                    .join(
                        source_entity,
                        source_entity.uuid == KnowledgeRelationship.source_entity_uuid,
                    )
                    .join(
                        target_entity,
                        target_entity.uuid == KnowledgeRelationship.target_entity_uuid,
                    )
                    .where(KnowledgeRelationship.knowledge_graph_uuid == uuid)
                    .group_by(source_entity.type, target_entity.type)
                )
            ).all()
            return {
                'clusters': [{'type': entity_type or '未分类', 'count': count} for entity_type, count in rows],
                'entity_count': sum(count for _, count in rows),
                'relationships': [
                    {
                        'source_type': source_type or '未分类',
                        'target_type': target_type or '未分类',
                        'count': count,
                    }
                    for source_type, target_type, count in relationship_rows
                    if source_type != target_type
                ],
            }

    @staticmethod
    async def get_exploration_type(*, uuid: str, entity_type: str, limit: int) -> dict:
        async with async_db_session() as db:
            entities = (
                (
                    await db.execute(
                        select(KnowledgeEntity)
                        .where(
                            KnowledgeEntity.knowledge_graph_uuid == uuid,
                            KnowledgeEntity.type == entity_type,
                        )
                        .order_by(KnowledgeEntity.id)
                        .limit(limit)
                    )
                )
                .scalars()
                .all()
            )
            ids = [entity.uuid for entity in entities]
            relationships = []
            if ids:
                relationships = (
                    (
                        await db.execute(
                            select(KnowledgeRelationship)
                            .where(
                                KnowledgeRelationship.knowledge_graph_uuid == uuid,
                                or_(
                                    KnowledgeRelationship.source_entity_uuid.in_(ids),
                                    KnowledgeRelationship.target_entity_uuid.in_(ids),
                                ),
                            )
                            .limit(limit * 4)
                        )
                    )
                    .scalars()
                    .all()
                )
                connected_ids = {
                    endpoint
                    for relationship in relationships
                    for endpoint in (
                        relationship.source_entity_uuid,
                        relationship.target_entity_uuid,
                    )
                }
                missing_ids = connected_ids.difference(ids)
                if missing_ids:
                    connected_entities = (
                        (
                            await db.execute(
                                select(KnowledgeEntity).where(
                                    KnowledgeEntity.knowledge_graph_uuid == uuid,
                                    KnowledgeEntity.uuid.in_(missing_ids),
                                )
                            )
                        )
                        .scalars()
                        .all()
                    )
                    entities.extend(connected_entities)
            return {'entities': entities, 'relationships': relationships}

    @staticmethod
    async def get_exploration_neighbors(*, uuid: str, entity_uuid: str, depth: int, limit: int) -> dict:
        async with async_db_session() as db:
            ids = {entity_uuid}
            frontier = {entity_uuid}
            relationships = []
            relationship_ids = set()
            for _ in range(depth):
                if not frontier or len(relationships) >= limit:
                    break
                relationship_query = select(KnowledgeRelationship).where(
                    KnowledgeRelationship.knowledge_graph_uuid == uuid,
                    or_(
                        KnowledgeRelationship.source_entity_uuid.in_(frontier),
                        KnowledgeRelationship.target_entity_uuid.in_(frontier),
                    ),
                )
                if relationship_ids:
                    relationship_query = relationship_query.where(KnowledgeRelationship.uuid.notin_(relationship_ids))
                layer = (await db.execute(relationship_query.limit(limit - len(relationships)))).scalars().all()
                next_frontier = set()
                for item in layer:
                    if item.uuid in relationship_ids:
                        continue
                    relationship_ids.add(item.uuid)
                    relationships.append(item)
                    next_frontier.update((item.source_entity_uuid, item.target_entity_uuid))
                next_frontier -= ids
                ids.update(next_frontier)
                frontier = next_frontier
            entities = (
                (
                    await db.execute(
                        select(KnowledgeEntity).where(
                            KnowledgeEntity.knowledge_graph_uuid == uuid,
                            KnowledgeEntity.uuid.in_(ids),
                        )
                    )
                )
                .scalars()
                .all()
            )
            return {'entities': entities, 'relationships': relationships}

    _llm_slots = asyncio.Semaphore(settings.LLM_MAX_CONCURRENCY)

    @staticmethod
    async def add(*, obj: KnowledgeGraphBase) -> str:
        async with async_db_session.begin() as db:
            # 检查图谱库名称是否已存在
            knowledge_graph = await knowledge_graph_dao.get_by_name(db, name=obj.name, kg_base_uuid=obj.kg_base_uuid)
            if knowledge_graph:
                raise errors.ForbiddenError(msg='图谱库名称已存在')
            # 创建图谱库
            return await knowledge_graph_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: UpdateKnowledgeGraphParam) -> int:
        async with async_db_session.begin() as db:
            knowledge_graph = await knowledge_graph_dao.get_by_uuid(db, uuid)
            if not knowledge_graph:
                raise errors.NotFoundError(msg='图谱库不存在')

            # 检查更新的名称是否已存在
            if obj.name and obj.name != knowledge_graph.name:
                existing_knowledge_graph = await knowledge_graph_dao.get_by_name(
                    db, name=obj.name, kg_base_uuid=obj.kg_base_uuid
                )
                if existing_knowledge_graph:
                    raise errors.ForbiddenError(msg='图谱库名称已存在')

            # 更新图谱库信息
            count = await knowledge_graph_dao.update_knowledge_graph(db, knowledge_graph.id, obj)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{knowledge_graph.id}')
            return count

    @staticmethod
    async def get_knowledge_graph(*, uuid: str = None, name: str = None) -> KnowledgeGraph:
        async with async_db_session() as db:
            knowledge_graph = await knowledge_graph_dao.get_with_relation(db, uuid=uuid, name=name)
            if not knowledge_graph:
                raise errors.NotFoundError(msg='图谱库不存在')
            return knowledge_graph

    @staticmethod
    async def get_depth(*, uuid: str = None) -> int:
        async with async_db_session() as db:
            depth = await knowledge_graph_dao.get_depth(db, uuid=uuid)
            if not depth:
                raise errors.NotFoundError(msg='图谱库不存在')
            return depth

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            knowledge_graph = await knowledge_graph_dao.get_by_uuid(db, uuid=uuid)
            if not knowledge_graph:
                raise errors.NotFoundError(msg='图谱库不存在')
            count = await knowledge_graph_dao.delete(db, knowledge_graph.id)
            return count

    @staticmethod
    async def update_status(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            knowledge_graph = await knowledge_graph_dao.get(db, pk)
            if not knowledge_graph:
                raise errors.NotFoundError(msg='图谱库不存在')
            if pk == request.user.id:
                raise errors.ForbiddenError(msg='非法操作')
            status = await knowledge_graph_dao.get_status(db, pk)
            count = await knowledge_graph_dao.set_status(db, pk, False if status else True)
            await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{pk}')
            return count

    @staticmethod
    async def get_all(*, kg_base_uuid: str, name: str = None) -> list[KnowledgeGraph]:
        async with async_db_session() as db:
            knowledge_graphs = await knowledge_graph_dao.get_list(db, kg_base_uuid=kg_base_uuid, name=name)
            if not knowledge_graphs:
                return []
            return knowledge_graphs

    @staticmethod
    async def extract(
        *,
        file_paths: list[str],
        schema: GetSchemaGraphDetail,
        api_key: str,
        base_url: str,
        model: str,
        task_client: Task,
    ) -> List[KnowledgeGraph]:
        async with KnowledgeGraphService._llm_slots:
            entities = schema.entities
            relationships = schema.relationships
            entity_map = {entity.uuid: entity for entity in entities}

            formed_schema = []
            formed_schema_definition = {}

            for relationship in relationships:
                source_entity = entity_map.get(relationship.source_entity_uuid)
                target_entity = entity_map.get(relationship.target_entity_uuid)

                if not source_entity or not target_entity:
                    continue

                schema_entry = {
                    'schema': {
                        'DirectionalEntityType': {'Name': source_entity.name, 'Attributes': source_entity.attributes},
                        'RelationType': relationship.name,
                        'DirectedEntityType': {'Name': target_entity.name, 'Attributes': target_entity.attributes},
                    }
                }

                formed_schema_definition[relationship.name] = relationship.definition
                formed_schema_definition[source_entity.name] = source_entity.definition
                formed_schema_definition[target_entity.name] = target_entity.definition
                formed_schema.append(schema_entry)

            # 创建临时目录
            request_temp_dir = os.path.join(PERMANENT_TEMP_DIR, str(uuid4()))
            os.makedirs(request_temp_dir, exist_ok=True)

            # 拷贝文件到临时目录
            try:
                for file_path in file_paths:
                    filename = os.path.basename(file_path)
                    temp_path = os.path.join(request_temp_dir, filename)
                    shutil.copy(resolve_local_file_path(file_path), temp_path)

                # 调用内部服务函数
                api_result = await create_kg(
                    kg_schema=formed_schema,
                    documents_dir_path=request_temp_dir,
                    schema_definition=formed_schema_definition,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    task_client=task_client,
                )
            finally:
                shutil.rmtree(request_temp_dir)

            return api_result

    @staticmethod
    async def infer(
        *, knowledge_graph: GetKnowledgeGraphDetail, api_key: str, base_url: str, model: str, task_client: Task
    ) -> List[KnowledgeGraph]:
        async with KnowledgeGraphService._llm_slots:
            entities = knowledge_graph.entities
            relationships = knowledge_graph.relationships
            # 创建实体映射表以便快速查找
            entity_map = {entity.uuid: entity for entity in entities}

            # 构造 formed_schema
            formed_kg = []
            for relationship in relationships:
                source_entity = entity_map.get(relationship.source_entity_uuid)
                target_entity = entity_map.get(relationship.target_entity_uuid)

                if not source_entity or not target_entity:
                    continue  # 跳过没有找到实体的关系

                # 格式化单个关系
                schema_entry = {
                    'DirectionalEntity': {
                        'Name': source_entity.name,
                        'Type': source_entity.name,
                        'Attributes': json.loads(source_entity.attributes),
                        # 假设 attributes 是列表
                    },
                    'Relation': {
                        'Name': relationship.name,
                        'Type': relationship.name,
                        'Attributes': {},
                    },  # 假设关系有 type 属性
                    'DirectedEntity': {
                        'Name': target_entity.name,
                        'Type': target_entity.name,
                        'Attributes': json.loads(target_entity.attributes),
                        # 假设 attributes 是列表
                    },
                }

                formed_kg.append(schema_entry)
            try:
                api_result = await create_infer_kg(
                    kg=formed_kg, api_key=api_key, base_url=base_url, model=model, task_client=task_client
                )
            finally:
                pass
            return api_result

    @staticmethod
    async def build_index(
        *,
        knowledge_graph: GetIndexDetail,
        level: int,
        api_key: str,
        base_url: str,
        model: str,
        embedding_api_key: str,
        embedding_base_url: str,
        embedding_model: str,
        progress_callback=None,
    ):
        entities = [entity.to_dict() for entity in knowledge_graph.entities]
        relationships = [relationship.to_dict() for relationship in knowledge_graph.relationships]

        try:
            entities, community_reports = await build_index(
                entities=entities,
                relationships=relationships,
                level=level - 1,
                api_key=api_key,
                base_url=base_url,
                model=model,
                embedding_api_key=embedding_api_key,
                embedding_base_url=embedding_base_url,
                embedding_model=embedding_model,
                progress_callback=progress_callback,
            )
            return {'entities': entities, 'community_reports': community_reports}

        except Exception as e:
            logger.error(f'An error occurred: {str(e)}', exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def query(
        *,
        knowledge_graph: GetIndexDetail,
        query: str,
        infer: bool = False,
        depth: int = 0,
        api_key: str,
        base_url: str,
        model: str,
        embedding_api_key: str,
        embedding_base_url: str,
        embedding_model: str,
        context_provider=None,
        token_callback=None,
        progress_callback=None,
    ):
        entities = [entity.to_dict() for entity in knowledge_graph.entities]
        relationships = [relationship.to_dict() for relationship in knowledge_graph.relationships]
        communities = [relationship.to_dict() for relationship in knowledge_graph.communities]
        try:
            # 从数据库导出的数据进行解析
            entity_mapping = {
                'uuid': 'id',
                'name': 'name',
                'type': 'type',
                'attributes': 'attributes',
                'embeddings': 'attributes_embedding',
                'sources': 'source_ids',
                'communities': 'community_ids',
            }
            relationship_mapping = {
                'uuid': 'id',
                'source_entity_uuid': 'source',
                'target_entity_uuid': 'target',
                'type': 'type',
                'name': 'name',
                'attributes': 'attributes',
                'source': 'triple_source',
            }
            community_report_mapping = {
                'uuid': 'id',
                'title': 'title',
                'level': 'level',
                'content': 'full_content',
                'rating': 'rating',
                'attributes': 'attributes',
            }

            entities = parse_json(json.dumps(entities), entity_mapping)
            relationships = parse_json(json.dumps(relationships), relationship_mapping)
            community_reports = parse_json(json.dumps(communities), community_report_mapping)
            logger.info('Data parsing completed')

            results, context_text, context_data = await query_kg(
                query=query,
                entities=load_entities(df=pd.DataFrame(entities)),
                relationships=load_relationships(df=pd.DataFrame(relationships)),
                community_reports=load_community(df=pd.DataFrame(community_reports)),
                level=int(depth) - 1,
                infer=infer,
                api_key=api_key,
                base_url=base_url,
                model=model,
                embedding_api_key=embedding_api_key,
                embedding_base_url=embedding_base_url,
                embedding_model=embedding_model,
                context_provider=context_provider,
                token_callback=token_callback,
                progress_callback=progress_callback,
            )
            return {'results': results, 'context_text': context_text, 'context_data': context_data}

        except Exception as e:
            logger.error(f'An error occurred: {str(e)}', exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_index_status(*, uuid: str, index_status: int) -> int:
        async with async_db_session.begin() as db:
            knowledge_graph = await knowledge_graph_dao.get_by_uuid(db, uuid)
            if not knowledge_graph:
                raise errors.NotFoundError(msg='图谱库不存在')

            # 更新图谱库信息
            count = await knowledge_graph_dao.update_status(db, knowledge_graph.id, index_status)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{knowledge_graph.id}')
            return count

    @staticmethod
    async def update_depth(*, uuid: str, depth: int) -> int:
        async with async_db_session.begin() as db:
            knowledge_graph = await knowledge_graph_dao.get_by_uuid(db, uuid)
            if not knowledge_graph:
                raise errors.NotFoundError(msg='图谱库不存在')

            # 更新图谱库信息
            count = await knowledge_graph_dao.update_depth(db, knowledge_graph.id, depth)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{knowledge_graph.id}')
            return count

    @staticmethod
    async def get_user_llm_info(user_token: str, model_uuid: str | None = None):
        """
        通过 user_token 查询用户的 api-key
        :param user_token: 用户 user_token
        :return: api-key 或 None
        """
        return await get_user_llm_info(user_token=user_token, model_uuid=model_uuid)

    @staticmethod
    async def get_user_embedding_info(user_token: str):
        return await get_user_embedding_info(user_token=user_token)


knowledge_graph_service = KnowledgeGraphService()
