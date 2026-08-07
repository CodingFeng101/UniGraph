from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.kgbase.model.chat_library import ChatLibrary
from backend.app.kgbase.schema.chat_library import LibraryBase, LibraryDetail
from backend.app.kgbase.schema.source import UpdateSourceParam


class CRUDLibrary(CRUDPlus[ChatLibrary]):
    async def get(self, db: AsyncSession, source_id: int) -> ChatLibrary | None:
        """
        获取架构图谱

        :param db: 异步数据库会话
        :param source_id: 架构图谱 ID
        :return: 返回架构图谱对象或者 None
        """
        return await self.select_model(db, source_id)

    async def get_by_name(self, db: AsyncSession, name: str) -> ChatLibrary | None:
        """
        通过名称获取架构图谱

        :param db: 异步数据库会话
        :param name: 架构图谱名称
        :return: 返回架构图谱对象，或者 None
        """
        return await self.select_model_by_column(db, name=name)

    async def get_by_uuid(self, db: AsyncSession, chat_library_uuid: str) -> ChatLibrary | None:
        """
        通过名称获取架构图谱

        :param chat_library_uuid:
        :param db: 异步数据库会话
        :return: 返回架构图谱对象，或者 None
        """
        return await self.select_model_by_column(db, uuid=chat_library_uuid)

    # async def get_by_knowledge_graph_id(self, db: AsyncSession, knowledge_graph_id: str) -> list[ChatLibrary]:
    #     """
    #     通过图谱ID获取三元组信息源
    #     :param db:
    #     :param kg_base_uuid:
    #     :return: 返回三元组信息源列表
    #     """
    #     # 通过 knowledge_graph_id 检索信息源
    #     query = select(Source).where(Source.knowledge_graph_id == knowledge_graph_id)
    #     result = await db.execute(query)
    #     return result.scalars().all()

    async def create(self, db: AsyncSession, obj: LibraryBase, *, user_uuid: str) -> str:
        """
        创建架构图谱

        :param db: 异步数据库会话
        :param obj: 架构图谱数据对象
        :return: 无返回值
        """
        dict_obj = obj.model_dump()
        new_library = self.model(**dict_obj, user_uuid=user_uuid)
        db.add(new_library)
        return new_library.uuid

    async def update(self, db: AsyncSession, source_id: int, obj: UpdateSourceParam) -> int:
        """
        更新架构图谱

        :param db: 异步数据库会话
        :param source_id: 架构图谱 ID
        :param obj: 架构图谱更新数据
        :return: 返回受影响的行数
        """
        return await self.update_model(db, source_id, obj)

    async def delete(self, db: AsyncSession, uuid: int) -> int:
        """
        删除架构图谱

        :param db: 异步数据库会话
        :param uuid: 架构图谱 ID
        :return: 返回受影响的行数
        """
        return await self.delete_model(db, uuid)

    async def get_list(self, db: AsyncSession, *, kg_base_uuid: str, name: str = None) -> list[ChatLibrary]:
        """
        获取架构图谱列表

        :param db:
        :param kg_base_uuid:
        :param name: 架构图谱名称（模糊查询）
        :return: 返回 SQL 查询语句
        """
        stmt = select(self.model).order_by(self.model.created_time)
        where_list = [self.model.kg_base_uuid == kg_base_uuid]
        # if name:
        #     where_list.append(self.model.entities.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        library = await db.execute(stmt)

        return library.scalars().all()

    async def get_with_relation(self, db: AsyncSession, *, uuid: str = None, name: str = None) -> ChatLibrary | None:
        """
        :param uuid:
        :param status:
        :param name:
        :param kg_base_uuid:
        :param db:
        :return:
        """
        stmt = select(self.model)
        where_list = [self.model.uuid == uuid]
        if where_list:
            stmt = stmt.where(and_(*where_list))

        source = await db.execute(stmt)

        return source.scalars().first()

    async def get_with_user(self, db: AsyncSession, source_id: int) -> ChatLibrary | None:
        """
        获取架构图谱及其关联的用户信息

        :param db: 异步数据库会话
        :param source_id: 架构图谱 ID
        :return: 返回架构图谱和用户对象，或者 None
        """
        stmt = select(self.model).options(self.model.user).filter(self.model.id == source_id)
        source = await db.execute(stmt)
        return source.scalars().first()

    async def update_library(self, db: AsyncSession, pk: int, obj: LibraryDetail) -> int:
        """
        更新用户信息

        :param db:
        :param pk:
        :param obj:
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def update_status(self, db: AsyncSession, source_id: int, status: int) -> int:
        """
        更新架构图谱状态

        :param db: 异步数据库会话
        :param source_id: 架构图谱 ID
        :param status: 架构图谱状态
        :return: 返回更新的行数
        """
        return await self.update_model(db, source_id, {'status': status})

    async def update_cover_image(self, db: AsyncSession, source_id: int, cover_image: str) -> int:
        """
        更新架构图谱封面图

        :param db: 异步数据库会话
        :param source_id: 架构图谱 ID
        :param cover_image: 封面图 URL
        :return: 返回更新的行数
        """
        return await self.update_model(db, source_id, {'cover_image': cover_image})

    async def get_user_sources(self, db: AsyncSession, user_uuid: str) -> list[ChatLibrary]:
        """
        获取指定用户的所有架构图谱

        :param db: 异步数据库会话
        :param user_uuid: 用户 UUID
        :return: 返回用户关联的所有架构图谱
        """
        stmt = select(self.model).filter(self.model.user_uuid == user_uuid)
        result = await db.execute(stmt)
        return result.scalars().all()


# 实例化 CRUD 对象
library_dao: CRUDLibrary = CRUDLibrary(ChatLibrary)
