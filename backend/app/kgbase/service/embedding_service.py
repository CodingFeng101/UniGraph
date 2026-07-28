#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from backend.app.kgbase.crud.crud_embedding import embedding_dao
from backend.app.kgbase.model import Embedding
from backend.app.kgbase.schema.embedding import (
    EmbeddingBase,
)
from backend.common.exception import errors
from backend.database.db_mysql import async_db_session


class EmbeddingService:
    _lock = asyncio.Lock()  # 创建一个类级别的异步锁

    @staticmethod
    async def add(*, obj: EmbeddingBase) -> str:
        async with async_db_session.begin() as db:
            embedding = await embedding_dao.get_with_relation(db=db, knowledge_entity_uuid=obj.knowledge_entity_uuid)
            if embedding:
                await embedding_dao.delete(db, embedding.id)
            return await embedding_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: EmbeddingBase) -> int:
        async with async_db_session.begin() as db:
            embedding = await embedding_dao.get_by_uuid(db, uuid)
            if not embedding:
                return 0

            count = await embedding_dao.update_embedding(db, embedding.id, obj)
            return count

    @staticmethod
    async def get_embedding(*, uuid: str = None, name: str = None) -> Embedding:
        async with async_db_session() as db:
            embedding = await embedding_dao.get_with_relation(db, uuid=uuid)
            if not embedding:
                raise errors.NotFoundError(msg='图谱库不存在')
            return embedding

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            embedding = await embedding_dao.get_by_uuid(db, uuid)
            if not embedding:
                raise errors.NotFoundError(msg='图谱库不存在')
            count = await embedding_dao.delete(db, embedding.id)
            return count

    @staticmethod
    async def get_all(*, kg_base_uuid: str, name: str = None) -> list[Embedding]:
        async with async_db_session() as db:
            communities = await embedding_dao.get_list(db, kg_base_uuid=kg_base_uuid, name=name)
            if not communities:
                raise errors.NotFoundError(msg='架构图谱不存在')
            return communities


embedding_service = EmbeddingService()
