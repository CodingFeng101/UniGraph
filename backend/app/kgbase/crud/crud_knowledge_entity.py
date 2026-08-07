from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.kgbase.model import Community, KnowledgeEntity
from backend.app.kgbase.schema.knowledge_entity import (
    AddKnowledgeEntityParam,
    UpdateKnowledgeEntityParam,
)


class CRUDKnowledgeEntity(CRUDPlus[KnowledgeEntity]):
    async def get(self, db: AsyncSession, knowledge_entity_id: int) -> KnowledgeEntity | None:
        """
        获取实体类型

        :param db: 异步数据库会话
        :param knowledge_entity_id: 实体类型 ID
        :return: 返回实体类型对象或者 None
        """
        return await self.select_model(db, knowledge_entity_id)

    async def get_by_name(self, db: AsyncSession, name: str) -> KnowledgeEntity | None:
        """
        通过名称获取实体类型

        :param db: 异步数据库会话
        :param name: 实体类型名称
        :return: 返回实体类型对象，或者 None
        """
        return await self.select_model_by_column(db, name=name)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> KnowledgeEntity | None:
        """
        通过名称获取实体类型

        :param uuid:
        :param db: 异步数据库会话
        :return: 返回实体类型对象，或者 None
        """
        return await self.select_model_by_column(db, uuid=uuid)

    async def get_by_knowledge_graph_id(self, db: AsyncSession, knowledge_graph_id: str) -> list[KnowledgeEntity]:
        """
        通过图谱 ID 获取实体类型
        :param db:
        :param knowledge_graph_id:
        :return: 返回实体列表
        """
        # 通过 knowledge_graph_id 检索实体
        query = select(KnowledgeEntity).where(KnowledgeEntity.knowledge_graph_id == knowledge_graph_id)
        result = await db.execute(query)
        entities = result.scalars().all()
        return entities

    async def create(self, db: AsyncSession, obj: AddKnowledgeEntityParam) -> str:
        """
        创建实体类型

        :param db: 异步数据库会话
        :param obj: 实体类型数据对象
        :return: 无返回值
        """
        dict_obj = obj.model_dump()
        new_knowledge_entity = self.model(**dict_obj)
        db.add(new_knowledge_entity)

        return new_knowledge_entity.uuid

    async def update(self, db: AsyncSession, knowledge_entity_id: int, obj: UpdateKnowledgeEntityParam) -> int:
        """
        更新实体类型

        :param db: 异步数据库会话
        :param knowledge_entity_id: 实体类型 ID
        :param obj: 实体类型更新数据
        :return: 返回受影响的行数
        """
        return await self.update_model(db, knowledge_entity_id, obj)

    async def delete(self, db: AsyncSession, knowledge_entity_id: int) -> int:
        """
        删除实体类型

        :param db: 异步数据库会话
        :param knowledge_entity_id: 实体类型 ID
        :return: 返回受影响的行数
        """
        return await self.delete_model(db, knowledge_entity_id)

    async def get_list(self, db: AsyncSession, *, knowledge_graph_uuid: str, name: str = None) -> list[KnowledgeEntity]:
        """
        获取实体类型列表

        :param db:
        :param knowledge_graph_uuid:
        :param name: 实体类型名称（模糊查询）
        :return: 返回 SQL 查询语句
        """
        stmt = select(self.model).order_by(self.model.created_time)
        where_list = [self.model.knowledge_graph_uuid == knowledge_graph_uuid]
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        knowledge_entity = await db.execute(stmt)

        return knowledge_entity.scalars().all()

    async def get_with_relation(
        self,
        db: AsyncSession,
        *,
        uuid: str = None,
        name: str = None,
        status: int = None,
        knowledge_graph_uuid: str = None,
        type: str = None,
    ) -> KnowledgeEntity | None:
        """
        :param uuid:
        :param status:
        :param name:
        :param db:
        :param knowledge_graph_uuid:
        :return:
        """
        stmt = select(self.model).options(
            selectinload(self.model.embeddings),
            selectinload(self.model.communities),
        )
        where_list = []
        if uuid:
            where_list.append(self.model.uuid == uuid)
        if knowledge_graph_uuid:
            where_list.append(self.model.knowledge_graph_uuid == knowledge_graph_uuid)
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if type:
            where_list.append(self.model.type == type)

        if where_list:
            stmt = stmt.where(and_(*where_list))

        knowledge_entity = await db.execute(stmt)

        return knowledge_entity.scalars().first()

    async def get_with_user(self, db: AsyncSession, knowledge_entity_id: int) -> KnowledgeEntity | None:
        """
        获取实体类型及其关联的用户信息

        :param db: 异步数据库会话
        :param knowledge_entity_id: 实体类型 ID
        :return: 返回实体类型和用户对象，或者 None
        """
        stmt = select(self.model).options(self.model.user).filter(self.model.id == knowledge_entity_id)
        knowledge_entity = await db.execute(stmt)
        return knowledge_entity.scalars().first()

    async def update_knowledge_entity(self, db: AsyncSession, pk: int, obj: UpdateKnowledgeEntityParam) -> int:
        """
        更新用户信息

        :param db:
        :param pk:
        :param obj:
        :return:
        """
        return await self.update_model(db, pk, obj)

    # async def add_source(self, db: AsyncSession, knowledge_entity_uuid: str, source_uuid: str) -> int:
    #     """
    #     将一个 source 添加到指定的 knowledge_graph
    #
    #     :param db: 异步数据库会话
    #     :param knowledge_entity_uuid: 知识图谱的 ID
    #     :param source_uuid: 需要添加的 source ID
    #     :return: 返回受影响的行数
    #     """
    #     # 1. 获取 KnowledgeEntity 对象
    #     stmt = select(KnowledgeEntity).options(selectinload(KnowledgeEntity.sources)).where(
    #         KnowledgeEntity.uuid == knowledge_entity_uuid)
    #     result = await db.execute(stmt)
    #     knowledge_entity = result.scalars().first()
    #
    #     if not knowledge_entity:
    #         raise ValueError(f"KnowledgeEntity {knowledge_entity_uuid} 不存在")
    #
    #     # 2. 获取 Source 对象
    #     stmt = select(Source).where(Source.uuid == source_uuid)
    #     result = await db.execute(stmt)
    #     source = result.scalars().first()
    #
    #     knowledge_entity.sources.append(source)
    #
    #     try:
    #         await db.commit()
    #         return 1  # 返回受影响的行数
    #     except IntegrityError as e:
    #         await db.rollback()
    #         raise Exception("添加失败，可能存在约束冲突") from e

    async def add_community(self, db: AsyncSession, knowledge_entity_uuid: str, community_uuid: str) -> int:
        """
        将一个 source 添加到指定的 knowledge_graph

        :param db: 异步数据库会话
        :param knowledge_entity_uuid: 知识图谱的 ID
        :param community_uuid: 需要添加的 source ID
        :return: 返回受影响的行数
        """
        # 1. 获取 KnowledgeEntity 对象
        stmt = (
            select(self.model)
            .options(selectinload(self.model.communities))
            .where(self.model.uuid == knowledge_entity_uuid)
        )
        result = await db.execute(stmt)
        knowledge_entity = result.scalars().first()

        if not knowledge_entity:
            raise ValueError(f'KnowledgeEntity {knowledge_entity_uuid} 不存在')

        # 2. 获取 Community 对象
        stmt = select(Community).where(Community.uuid == community_uuid)
        result = await db.execute(stmt)
        community = result.scalars().first()

        knowledge_entity.communities.append(community)

        try:
            await db.commit()
            return 1  # 返回受影响的行数
        except IntegrityError as e:
            await db.rollback()
            raise Exception('添加失败，可能存在约束冲突') from e

    async def update_status(self, db: AsyncSession, knowledge_entity_id: int, status: int) -> int:
        """
        更新实体类型状态

        :param db: 异步数据库会话
        :param knowledge_entity_id: 实体类型 ID
        :param status: 实体类型状态
        :return: 返回更新的行数
        """
        return await self.update_model(db, knowledge_entity_id, {'status': status})

    async def update_cover_image(self, db: AsyncSession, knowledge_entity_id: int, cover_image: str) -> int:
        """
        更新实体类型封面图

        :param db: 异步数据库会话
        :param knowledge_entity_id: 实体类型 ID
        :param cover_image: 封面图 URL
        :return: 返回更新的行数
        """
        return await self.update_model(db, knowledge_entity_id, {'cover_image': cover_image})

    async def get_user_knowledge_entities(self, db: AsyncSession, user_uuid: str) -> list[KnowledgeEntity]:
        """
        获取指定用户的所有实体类型

        :param db: 异步数据库会话
        :param user_uuid: 用户 UUID
        :return: 返回用户关联的所有实体类型
        """
        stmt = select(self.model).filter(self.model.user_uuid == user_uuid)
        result = await db.execute(stmt)
        return result.scalars().all()


# 实例化 CRUD 对象
knowledge_entity_dao: CRUDKnowledgeEntity = CRUDKnowledgeEntity(KnowledgeEntity)
