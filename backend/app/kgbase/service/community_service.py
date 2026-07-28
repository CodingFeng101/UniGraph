#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

from fastapi import Request

from backend.app.kgbase.crud.crud_community import community_dao
from backend.app.kgbase.model import Community
from backend.app.kgbase.schema.community import (
    CommunityBase,
    UpdateCommunityParam,
)
from backend.common.exception import errors
from backend.common.security.jwt import superuser_verify
from backend.core.conf import settings
from backend.database.db_mysql import async_db_session
from backend.database.db_redis import redis_client


class CommunityService:
    _lock = asyncio.Lock()  # 创建一个类级别的异步锁

    @staticmethod
    async def add(*, obj: CommunityBase) -> str:
        async with async_db_session.begin() as db:
            # 创建图谱库
            return await community_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: UpdateCommunityParam) -> int:
        async with async_db_session.begin() as db:
            community = await community_dao.get_by_uuid(db, uuid)
            if not community:
                return 0

            # 检查更新的名称是否已存在
            if obj.title == community.title and obj.content == community.content and obj.rating == community.rating:
                return 0

            count = await community_dao.update_community(db, community.id, obj)
            return count

    @staticmethod
    async def get_community(*, uuid: str = None, name: str = None) -> Community:
        async with async_db_session() as db:
            community = await community_dao.get_with_relation(db, uuid=uuid, name=name)
            if not community:
                raise errors.NotFoundError(msg='图谱库不存在')
            return community

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            community = await community_dao.get_by_uuid(db, uuid)
            if not community:
                raise errors.NotFoundError(msg='图谱库不存在')
            count = await community_dao.delete(db, community.id)

            # # 删除缓存
            # key_prefix = [
            #     f'{settings.KG_BASE_REDIS_PREFIX}:{community.id}',
            #     f'{settings.TOKEN_REDIS_PREFIX}:{community.id}',
            #     f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{community.id}'
            # ]
            # for key in key_prefix:
            #     await redis_client.delete_prefix(key)
            return count

    @staticmethod
    async def delete_all(*, knowledge_graph_uuid: str) -> int:
        async with async_db_session.begin() as db:
            communities = await community_dao.get_list(db=db, knowledge_graph_uuid=knowledge_graph_uuid)
            if not communities:
                return 0
            for community in communities:
                count = await community_dao.delete(db, community.id)

            # # 删除缓存
            # key_prefix = [
            #     f'{settings.KG_BASE_REDIS_PREFIX}:{community.id}',
            #     f'{settings.TOKEN_REDIS_PREFIX}:{community.id}',
            #     f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{community.id}'
            # ]
            # for key in key_prefix:
            #     await redis_client.delete_prefix(key)
            return count

    @staticmethod
    async def update_status(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            community = await community_dao.get(db, pk)
            if not community:
                raise errors.NotFoundError(msg='图谱库不存在')
            if pk == request.user.id:
                raise errors.ForbiddenError(msg='非法操作')
            status = await community_dao.get_status(db, pk)
            count = await community_dao.set_status(db, pk, False if status else True)
            await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{pk}')
            return count

    @staticmethod
    async def get_all(*, kg_base_uuid: str, name: str = None) -> list[Community]:
        async with async_db_session() as db:
            communities = await community_dao.get_list(db, kg_base_uuid=kg_base_uuid, name=name)
            if not communities:
                raise errors.NotFoundError(msg='架构图谱不存在')
            return communities


community_service = CommunityService()
