#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dotenv import load_dotenv
from fastapi import Request
from sqlalchemy import Select

from app.kgbase.crud.crud_kg_base import kg_base_dao
from app.kgbase.model import KgBase
from app.kgbase.schema.kg_base import (
    AddKgBaseParam,
    UpdateKgBaseParam,
)
from common.exception import errors
from common.security.jwt import superuser_verify
from core.conf import settings
from database.db_mysql import async_db_session
from database.db_redis import redis_client

load_dotenv()


class KgBaseService:
    @staticmethod
    async def add(*, request: Request, obj: AddKgBaseParam) -> None:
        async with async_db_session.begin() as db:
            # 检查图谱库名称是否已存在
            kg_base = await kg_base_dao.get_by_name(db, obj.name)
            if kg_base:
                raise errors.ForbiddenError(msg='图谱库名称已存在')

            # 默认图谱库描述
            obj.description = obj.description if obj.description else '无描述'
            obj.user_uuid = request.user.uuid
            # 创建图谱库
            await kg_base_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: UpdateKgBaseParam) -> int:
        async with async_db_session.begin() as db:
            kg_base = await kg_base_dao.get_by_uuid(db, uuid)
            if not kg_base:
                raise errors.NotFoundError(msg='图谱库不存在')

            # 检查更新的名称是否已存在
            if obj.name and obj.name != kg_base.name:
                existing_kg_base = await kg_base_dao.get_by_name(db, obj.name)
                if existing_kg_base:
                    raise errors.ForbiddenError(msg='图谱库名称已存在')

            # 更新图谱库信息
            count = await kg_base_dao.update_kg_base(db, kg_base.id, obj)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{kg_base.id}')
            return count

    @staticmethod
    async def get_kg_base(*, uuid: str = None, name: str = None, status: int = None) -> KgBase:
        async with async_db_session() as db:
            kg_base = await kg_base_dao.get_with_relation(db, uuid=uuid, name=name, status=status)
            if not kg_base:
                raise errors.NotFoundError(msg='图谱库不存在')
            return kg_base

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            kg_base = await kg_base_dao.get_by_uuid(db, uuid)
            if not kg_base:
                raise errors.NotFoundError(msg='图谱库不存在')
            count = await kg_base_dao.delete(db, kg_base.id)

            # # 删除缓存
            # key_prefix = [
            #     f'{settings.KG_BASE_REDIS_PREFIX}:{kg_base.id}',
            #     f'{settings.TOKEN_REDIS_PREFIX}:{kg_base.id}',
            #     f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{kg_base.id}'
            # ]
            # for key in key_prefix:
            #     await redis_client.delete_prefix(key)
            return count

    @staticmethod
    async def update_status(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            kg_base = await kg_base_dao.get(db, pk)
            if not kg_base:
                raise errors.NotFoundError(msg='图谱库不存在')
            if pk == request.user.id:
                raise errors.ForbiddenError(msg='非法操作')
            status = await kg_base_dao.get_status(db, pk)
            count = await kg_base_dao.set_status(db, pk, False if status else True)
            await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{pk}')
            return count

    @staticmethod
    async def get_select(*, user_uuid: str, status: int = None, name: str = None) -> Select:
        return await kg_base_dao.get_list(user_uuid=user_uuid, status=status, name=name)


kg_base_service = KgBaseService()
