#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request

from backend.app.kgbase.crud.crud_knowledge_relationship import knowledge_relationship_dao
from backend.app.kgbase.model import KnowledgeRelationship
from backend.app.kgbase.schema.knowledge_relationship import (
    AddKnowledgeRelationshipParam,
    UpdateKnowledgeRelationshipParam,
)
from backend.common.exception import errors
from backend.common.security.jwt import superuser_verify
from backend.core.conf import settings
from backend.database.db_mysql import async_db_session
from backend.database.db_redis import redis_client


class KnowledgeRelationshipService:
    @staticmethod
    async def add(*, obj: AddKnowledgeRelationshipParam) -> str:
        async with async_db_session.begin() as db:
            knowledge_relationship = await knowledge_relationship_dao.get_with_relation(
                db, name=obj.name, target_entity_uuid=obj.target_entity_uuid, source_entity_uuid=obj.source_entity_uuid
            )
            if knowledge_relationship:
                # 如果关系已存在，则直接返回
                return knowledge_relationship.uuid
            # 创建关系
            return await knowledge_relationship_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: UpdateKnowledgeRelationshipParam) -> int:
        async with async_db_session.begin() as db:
            knowledge_relationship = await knowledge_relationship_dao.get_by_uuid(db, uuid)
            if not knowledge_relationship:
                raise errors.NotFoundError(msg='关系不存在')
            # 更新关系信息
            count = await knowledge_relationship_dao.update_knowledge_relationship(db, knowledge_relationship.id, obj)
            return count

    @staticmethod
    async def add_source_relation(*, knowledge_relationship_uuid: str, source_uuid: str) -> int:
        async with async_db_session.begin() as db:
            await knowledge_relationship_dao.add_source(
                db, knowledge_relationship_uuid=knowledge_relationship_uuid, source_uuid=source_uuid
            )
            return 1

    @staticmethod
    async def get_knowledge_relationship(
        *, uuid: str = None, name: str = None, status: int = None
    ) -> KnowledgeRelationship:
        async with async_db_session() as db:
            knowledge_relationship = await knowledge_relationship_dao.get_with_relation(
                db, uuid=uuid, name=name, status=status
            )
            if not knowledge_relationship:
                raise errors.NotFoundError(msg='关系不存在')
            return knowledge_relationship

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            knowledge_relationship = await knowledge_relationship_dao.get_by_uuid(db, uuid)
            if not knowledge_relationship:
                raise errors.NotFoundError(msg='关系不存在')
            count = await knowledge_relationship_dao.delete(db, knowledge_relationship.id)
            return count

    @staticmethod
    async def update_status(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            knowledge_relationship = await knowledge_relationship_dao.get(db, pk)
            if not knowledge_relationship:
                raise errors.NotFoundError(msg='关系不存在')
            if pk == request.user.id:
                raise errors.ForbiddenError(msg='非法操作')
            status = await knowledge_relationship_dao.get_status(db, pk)
            count = await knowledge_relationship_dao.set_status(db, pk, False if status else True)
            await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{pk}')
            return count

    @staticmethod
    async def get_all(*, knowledge_graph_uuid: str, name: str = None) -> list[KnowledgeRelationship]:
        async with async_db_session() as db:
            knowledge_relationships = await knowledge_relationship_dao.get_list(
                db, knowledge_graph_uuid=knowledge_graph_uuid, name=name
            )
            if not knowledge_relationships:
                pass
            return knowledge_relationships


knowledge_relationship_service = KnowledgeRelationshipService()
