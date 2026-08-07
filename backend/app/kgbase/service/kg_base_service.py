#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Select

from backend.app.kgbase.crud.crud_kg_base import kg_base_dao
from backend.app.kgbase.model import KgBase
from backend.app.kgbase.schema.kg_base import (
    AddKgBaseParam,
    UpdateKgBaseParam,
)
from backend.common.exception import errors
from backend.core.path_conf import STATIC_DIR
from backend.database.db_mysql import async_db_session

load_dotenv()

DEFAULT_BACKGROUND = 'static/default/kg_base_default.png'


class KgBaseService:
    """
    提供知识库的CRUD操作
    注意:
    确保所挂载的fastapi静态文件目录位于项目根目录下
    """

    @staticmethod
    async def add(*, obj: AddKgBaseParam) -> None:
        async with async_db_session.begin() as db:
            # 检查图谱库名称是否已存在
            if not obj.cover_image:  # 如果背景图片不存在，则使用默认
                obj.cover_image = DEFAULT_BACKGROUND  # 使用默认背景
            kg_base = await kg_base_dao.get_by_name(db, obj.name, obj.user_uuid)
            if kg_base:
                raise errors.ForbiddenError(msg='图谱库名称已存在')  # 这里的名称核查逻辑应该首先由前端执行
            # 默认图谱库描述
            obj.description = obj.description if obj.description else '无描述'  # 默认描述
            # 创建图谱库
            try:
                await kg_base_dao.create(db, obj)
            except Exception:
                raise errors.ServerError(msg='数据库异常, 请稍后再试！')  # 如果基本的创建失败，则说明数据库发生了异常

    @staticmethod
    async def update(*, uuid: str, obj: UpdateKgBaseParam) -> int:
        async with async_db_session.begin() as db:
            kg_base = await kg_base_dao.get_by_uuid(db, uuid)
            if not kg_base:
                raise errors.NotFoundError(msg='知识库不存在！')

            # 检查更新的名称是否已存在
            if obj.name and obj.name != kg_base.name:
                existing_kg_base = await kg_base_dao.get_by_name(db, obj.name, kg_base.user_uuid)
                if existing_kg_base:
                    # 这里的名称核查逻辑应该首先由前端执行
                    raise errors.ForbiddenError(msg='图谱库名称已存在')
            # 更新图谱库信息
            try:
                count = await kg_base_dao.update_kg_base(db, kg_base.id, obj)
                return count
            except Exception:
                raise errors.ServerError(msg='数据库异常, 请稍后再试！')  # 如果基本的更新失败，则说明数据库发生了异常

    @staticmethod
    async def get_kg_base(*, uuid: str = None, name: str = None, status: int = None) -> KgBase:
        """
        :param uuid: 知识库的UUID
        :param name: 知识库名称
        :param status: 知识库状态 1代表正常，0代表禁用
        :return: 返回知识库对象 单个
        """
        async with async_db_session() as db:
            kg_base = await kg_base_dao.get_with_relation(db, uuid=uuid, name=name, status=status)  # 按照名称查询
            if not kg_base:
                raise errors.NotFoundError(msg='知识库不存在')
            return kg_base

    @staticmethod
    async def delete(*, uuid: str) -> int:
        """
        :param uuid: 知识库的UUID
        """
        async with async_db_session.begin() as db:
            kg_base = await kg_base_dao.get_by_uuid(db, uuid)
            if not kg_base:
                raise errors.NotFoundError(msg='知识库不存在！')
            cover_image = kg_base.cover_image or ''
            if cover_image and not cover_image.startswith(DEFAULT_BACKGROUND):
                cover_path = Path(cover_image)
                if cover_path.parts and cover_path.parts[0] == 'static':
                    cover_path = Path(STATIC_DIR) / Path(*cover_path.parts[1:])
                static_root = Path(STATIC_DIR).resolve()
                resolved_cover = cover_path.resolve()
                if resolved_cover.is_file() and resolved_cover.is_relative_to(static_root):
                    shutil.rmtree(resolved_cover.parent)
            count = await kg_base_dao.delete(db, kg_base.id)
            return count

    @staticmethod
    async def get_select(*, user_uuid: str, status: int = None, name: str = None) -> Select:
        """
        :param user_uuid: 用户UUID
        :param status: 知识库状态
        :param name: 知识库名称  1代表正常，0代表禁用
        :return: 返回知识库列表
        """
        return await kg_base_dao.get_list(user_uuid=user_uuid, status=status, name=name)

    @staticmethod
    async def get_all(*, user_uuid: str) -> list[KgBase]:
        """
        :param user_uuid: 用户UUID
        :return: 返回知识库列表
        """
        async with async_db_session() as db:
            return await kg_base_dao.get_user_kg_bases(db, user_uuid=user_uuid)


kg_base_service = KgBaseService()
