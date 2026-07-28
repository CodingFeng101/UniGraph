#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import json
import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import Request

from backend.app.kgbase.crud.crud_schema_graph import schema_graph_dao
from backend.app.kgbase.model import SchemaGraph
from backend.app.kgbase.schema import GetSchemaGraphDetail
from backend.app.kgbase.schema.schema_graph import SchemaGraphBase, UpdateSchemaGraphBase
from backend.app.kgbase.service.llm_info_service import get_user_llm_info
from backend.common.core_layer.interface.kgschema_service import (
    create_schema,
    suggestion_generation,
    update_schema,
)
from backend.common.exception import errors
from backend.common.security.jwt import superuser_verify
from backend.core.conf import settings
from backend.core.path_conf import STATIC_DIR, BasePath
from backend.database.db_mysql import async_db_session
from backend.database.db_redis import redis_client

PERMANENT_TEMP_DIR = 'temp_files'
os.makedirs(PERMANENT_TEMP_DIR, exist_ok=True)


def resolve_local_file_path(file_path: str) -> str:
    normalized = file_path[2:] if file_path.startswith('./') else file_path
    normalized_path = Path(os.path.normpath(normalized))

    candidates = [normalized_path, Path(BasePath) / normalized_path]
    if normalized_path.parts and normalized_path.parts[0] == 'static':
        candidates.append(Path(STATIC_DIR) / Path(*normalized_path.parts[1:]))

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return str(candidates[0])


class SchemaGraphService:
    _lock = asyncio.Lock()

    @staticmethod
    async def add(*, obj: SchemaGraphBase) -> str:
        async with async_db_session.begin() as db:
            schema_graph = await schema_graph_dao.get_by_name(db, name=obj.name, kg_base_uuid=obj.kg_base_uuid)
            if schema_graph:
                raise errors.ForbiddenError(msg='知识架构名称已存在')
            return await schema_graph_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: UpdateSchemaGraphBase) -> int:
        async with async_db_session.begin() as db:
            schema_graph = await schema_graph_dao.get_by_uuid(db, uuid)
            if not schema_graph:
                raise errors.NotFoundError(msg='知识架构不存在')

            if obj.name and obj.name != schema_graph.name:
                existing_schema_graph = await schema_graph_dao.get_by_name(
                    db, name=obj.name, kg_base_uuid=schema_graph.kg_base_uuid
                )
                if existing_schema_graph:
                    raise errors.ForbiddenError(msg='知识图谱架构名称已存在')

            return await schema_graph_dao.update(db, schema_graph.id, obj)

    @staticmethod
    async def get_schema_graph(*, uuid: str = None, name: str = None) -> SchemaGraph:
        async with async_db_session() as db:
            schema_graph = await schema_graph_dao.get_with_relation(db, uuid=uuid, name=name)
            if not schema_graph:
                raise errors.NotFoundError(msg='该知识图谱架构不存在')
            return schema_graph

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            schema_graph = await schema_graph_dao.get_by_uuid(db, uuid)
            if not schema_graph:
                raise errors.NotFoundError(msg='知识架构不存在')
            if await schema_graph_dao.search_schema_related_knowledge_graph(db, uuid):
                raise errors.ForbiddenError(msg='知识架构已关联知识图谱，请先删除相关知识图谱')
            return await schema_graph_dao.delete(db, schema_graph.id)

    @staticmethod
    async def update_status(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            schema_graph = await schema_graph_dao.get(db, pk)
            if not schema_graph:
                raise errors.NotFoundError(msg='知识架构不存在')
            if pk == request.user.id:
                raise errors.ForbiddenError(msg='非法操作')
            status = await schema_graph_dao.get_status(db, pk)
            count = await schema_graph_dao.set_status(db, pk, False if status else True)
            await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{pk}')
            return count

    @staticmethod
    async def get_all(*, kg_base_uuid: str, name: str = None) -> list[SchemaGraph]:
        async with async_db_session() as db:
            schema_graphs = await schema_graph_dao.get_list(db, kg_base_uuid=kg_base_uuid, name=name)
            return schema_graphs or []

    @staticmethod
    async def create_schema(
        *,
        file_paths: list[str],
        aim: str = None,
        api_key: str,
        base_url: str,
        model: str,
        progress_callback=None,
    ):
        async with SchemaGraphService._lock:
            file_locations: list[str] = []
            request_temp_dir = os.path.join(PERMANENT_TEMP_DIR, str(uuid4()))
            os.makedirs(request_temp_dir, exist_ok=True)

            try:
                for file_path in file_paths:
                    filename = os.path.basename(file_path)
                    temp_path = os.path.join(request_temp_dir, filename)
                    shutil.copy(resolve_local_file_path(file_path), temp_path)
                    file_locations.append(temp_path)

                schema, definition = await create_schema(
                    file_path_list=file_locations,
                    aim=aim,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    progress_callback=progress_callback,
                )
            finally:
                shutil.rmtree(request_temp_dir, ignore_errors=True)

            return schema, definition

    @staticmethod
    async def update_schema(
        *,
        file_paths: list[str],
        schema: GetSchemaGraphDetail,
        api_key: str,
        base_url: str,
        model: str,
        progress_callback=None,
    ):
        async with SchemaGraphService._lock:
            entities = [
                {
                    'name': entity.name,
                    'attributes': entity.attributes,
                    'definition': entity.definition,
                    'uuid': entity.uuid,
                    'source': entity.source,
                }
                for entity in schema.entities
            ]
            relationships = [
                {
                    'name': relationship.name,
                    'attributes': relationship.attributes,
                    'definition': relationship.definition,
                    'source_entity_uuid': relationship.source_entity_uuid,
                    'target_entity_uuid': relationship.target_entity_uuid,
                    'source': relationship.source,
                }
                for relationship in schema.relationships
            ]

            for entity in entities:
                entity['attributes'] = json.loads(entity['attributes'])

            definition = {}
            for relationship in relationships:
                definition[relationship['name']] = relationship['definition']
            for entity in entities:
                definition[entity['name']] = entity['definition']

            entity_dict = {entity['uuid']: entity for entity in entities}
            triples = []
            for relation in relationships:
                source_entity = entity_dict.get(relation['source_entity_uuid'])
                target_entity = entity_dict.get(relation['target_entity_uuid'])
                if source_entity and target_entity:
                    triples.append((
                        (source_entity['name'], source_entity['attributes']),
                        relation['name'],
                        (target_entity['name'], target_entity['attributes']),
                    ))

            kg_schema = []
            for source, relation, target in triples:
                kg_schema.append({
                    'schema': {
                        'DirectionalEntityType': {'Name': source[0], 'Attributes': source[1]},
                        'RelationType': relation,
                        'DirectedEntityType': {'Name': target[0], 'Attributes': target[1]},
                    },
                    'source': {},
                })

            info = json.loads(schema.modify_info)
            file_locations: list[str] = []
            request_temp_dir = os.path.join(PERMANENT_TEMP_DIR, str(uuid4()))
            os.makedirs(request_temp_dir, exist_ok=True)

            try:
                for path in file_paths:
                    filename = os.path.basename(path)
                    temp_path = os.path.join(request_temp_dir, filename)
                    shutil.copy(resolve_local_file_path(path), temp_path)
                    file_locations.append(temp_path)

                schema_result, definition_result = await update_schema(
                    file_path_list=file_locations,
                    aim=schema.aim,
                    kg_schema=kg_schema,
                    definition=definition,
                    modify_info=info,
                    suggestion=schema.modify_suggestion,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    progress_callback=progress_callback,
                )
            finally:
                shutil.rmtree(request_temp_dir, ignore_errors=True)

            return schema_result, definition_result

    @staticmethod
    async def update_suggestion(
        *,
        modify_info: str = None,
        pre_suggestion: str = None,
        api_key: str,
        base_url: str,
        model: str,
    ):
        async with SchemaGraphService._lock:
            info = json.loads(modify_info)
            return await suggestion_generation(info, pre_suggestion, api_key, base_url, model)

    @staticmethod
    async def get_user_llm_info(user_token: str):
        return await get_user_llm_info(user_token=user_token)


schema_graph_service = SchemaGraphService()
