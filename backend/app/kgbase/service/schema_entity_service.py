#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request

from backend.app.kgbase.crud.crud_schema_entity import schema_entity_dao
from backend.app.kgbase.model import SchemaEntity
from backend.app.kgbase.schema.schema_entity import (
    AddSchemaEntityParam,
    UpdateSchemaEntityParam,
)
from backend.common.exception import errors
from backend.common.security.jwt import superuser_verify
from backend.core.conf import settings
from backend.database.db_mysql import async_db_session
from backend.database.db_redis import redis_client


class SchemaEntityService:
    @staticmethod
    async def add(*, obj: AddSchemaEntityParam) -> str:
        async with async_db_session.begin() as db:
            entity = await schema_entity_dao.get_by_name_and_schema_graph_uuid(db, obj.name, obj.schema_graph_uuid)
            if entity:
                raise errors.ForbiddenError(msg='实体类型名称已存在')
            return await schema_entity_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: UpdateSchemaEntityParam) -> int:
        async with async_db_session.begin() as db:
            schema_entity = await schema_entity_dao.get_by_uuid(db, uuid)
            if not schema_entity:
                raise errors.NotFoundError(msg='该实体类型不存在')

            # 检查更新的名称是否已存在
            update_data = obj.data
            schema_graph_uuid = obj.schema_graph_uuid or schema_entity.schema_graph_uuid
            if update_data.name and update_data.name != schema_entity.name:
                existing_schema_entity = await schema_entity_dao.get_by_name_and_schema_graph_uuid(
                    db, update_data.name, schema_graph_uuid
                )
                if existing_schema_entity:
                    raise errors.ForbiddenError(msg='实体类型名称已存在')

            # 更新图谱库信息
            count = await schema_entity_dao.update_schema_entity(db, schema_entity.id, update_data)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{schema_entity.id}')
            return count

    @staticmethod
    async def get_schema_entity(*, uuid: str = None, name: str = None, schema_graph_uuid: str = None) -> SchemaEntity:
        async with async_db_session() as db:
            schema_entity = await schema_entity_dao.get_with_relation(
                db, uuid=uuid, name=name, schema_graph_uuid=schema_graph_uuid
            )
            if not schema_entity:
                raise errors.NotFoundError(msg='图谱库不存在')
            return schema_entity

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            schema_entity = await schema_entity_dao.get_by_uuid(db, uuid)
            if not schema_entity:
                raise errors.NotFoundError(msg='图谱库不存在')
            count = await schema_entity_dao.delete(db, schema_entity.id)
            return count

    @staticmethod
    async def update_status(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            schema_entity = await schema_entity_dao.get(db, pk)
            if not schema_entity:
                raise errors.NotFoundError(msg='图谱库不存在')
            if pk == request.user.id:
                raise errors.ForbiddenError(msg='非法操作')
            status = await schema_entity_dao.get_status(db, pk)
            count = await schema_entity_dao.set_status(db, pk, False if status else True)
            await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{pk}')
            return count

    @staticmethod
    async def get_all(*, schema_graph_uuid: str, name: str = None) -> list[SchemaEntity]:
        async with async_db_session() as db:
            schema_entities = await schema_entity_dao.get_list(db, schema_graph_uuid=schema_graph_uuid, name=name)
            if not schema_entities:
                return []
            return schema_entities


schema_entity_service = SchemaEntityService()
