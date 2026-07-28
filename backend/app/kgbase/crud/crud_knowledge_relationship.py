from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.kgbase.model import KnowledgeRelationship
from backend.app.kgbase.schema.knowledge_relationship import (
    AddKnowledgeRelationshipParam,
    UpdateKnowledgeRelationshipParam,
)


class CRUDKnowledgeRelationship(CRUDPlus[KnowledgeRelationship]):
    async def get(self, db: AsyncSession, knowledge_relationship_id: int) -> KnowledgeRelationship | None:
        """
        获取实体类型

        :param db: 异步数据库会话
        :param knowledge_relationship_id: 实体类型 ID
        :return: 返回实体类型对象或者 None
        """
        return await self.select_model(db, knowledge_relationship_id)

    async def get_by_name(self, db: AsyncSession, name: str) -> KnowledgeRelationship | None:
        """
        通过名称获取实体类型

        :param db: 异步数据库会话
        :param name: 实体类型名称
        :return: 返回实体类型对象，或者 None
        """
        return await self.select_model_by_column(db, name=name)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> KnowledgeRelationship | None:
        """
        通过名称获取实体类型

        :param uuid:
        :param db: 异步数据库会话
        :return: 返回实体类型对象，或者 None
        """
        return await self.select_model_by_column(db, uuid=uuid)

    async def get_by_knowledge_graph_id(self, db: AsyncSession, knowledge_graph_id: str) -> list[KnowledgeRelationship]:
        """
        通过图谱ID获取关系
        :param db:
        :param knowledge_graph_id:
        :return: 返回关系列表
        """
        # 通过 knowledge_graph_id 检索关系
        query = select(KnowledgeRelationship).where(KnowledgeRelationship.knowledge_graph_id == knowledge_graph_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj: AddKnowledgeRelationshipParam) -> str:
        """
        创建实体类型

        :param db: 异步数据库会话
        :param obj: 实体类型数据对象
        :return: 无返回值
        """
        dict_obj = obj.model_dump()
        new_knowledge_relationship = self.model(**dict_obj)
        db.add(new_knowledge_relationship)
        return new_knowledge_relationship.uuid

    async def update(
        self, db: AsyncSession, knowledge_relationship_id: int, obj: UpdateKnowledgeRelationshipParam
    ) -> int:
        """
        更新实体类型

        :param db: 异步数据库会话
        :param knowledge_relationship_id: 实体类型 ID
        :param obj: 实体类型更新数据
        :return: 返回受影响的行数
        """
        return await self.update_model(db, knowledge_relationship_id, obj)

    async def delete(self, db: AsyncSession, knowledge_relationship_id: int) -> int:
        """
        删除实体类型

        :param db: 异步数据库会话
        :param knowledge_relationship_id: 实体类型 ID
        :return: 返回受影响的行数
        """
        return await self.delete_model(db, knowledge_relationship_id)

    async def get_list(
        self, db: AsyncSession, *, knowledge_graph_uuid: str, name: str = None
    ) -> list[KnowledgeRelationship]:
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

        knowledge_relationship = await db.execute(stmt)

        return knowledge_relationship.scalars().all()

    async def get_with_relation(
        self,
        db: AsyncSession,
        *,
        uuid: str = None,
        name: str = None,
        source_entity_uuid: str = None,
        target_entity_uuid: str = None,
        status: int = None,
    ) -> KnowledgeRelationship | None:
        """
        :param source_entity_uuid:
        :param target_entity_uuid:
        :param uuid:
        :param name:
        :param db:
        :return:
        """
        stmt = select(self.model)
        where_list = []
        if source_entity_uuid:
            where_list.append(self.model.source_entity_uuid == source_entity_uuid)
        if target_entity_uuid:
            where_list.append(self.model.target_entity_uuid == target_entity_uuid)
        if uuid:
            where_list.append(self.model.uuid == uuid)
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if status is not None:
            where_list.append(self.model.status == status)

        if where_list:
            stmt = stmt.where(and_(*where_list))

        knowledge_relationship = await db.execute(stmt)

        return knowledge_relationship.scalars().first()

    async def get_with_user(self, db: AsyncSession, knowledge_relationship_id: int) -> KnowledgeRelationship | None:
        """
        获取实体类型及其关联的用户信息

        :param db: 异步数据库会话
        :param knowledge_relationship_id: 实体类型 ID
        :return: 返回实体类型和用户对象，或者 None
        """
        stmt = select(self.model).options(self.model.user).filter(self.model.id == knowledge_relationship_id)
        knowledge_relationship = await db.execute(stmt)
        return knowledge_relationship.scalars().first()

    # async def add_source(self, db: AsyncSession, knowledge_relationship_uuid: str, source_uuid: str) -> int:
    #     """
    #     将一个 source 添加到指定的 knowledge_graph
    #
    #     :param db: 异步数据库会话
    #     :param knowledge_relationship_uuid: 知识图谱的 ID
    #     :param source_uuid: 需要添加的 source ID
    #     :return: 返回受影响的行数
    #     """
    #     # 1. 获取 KnowledgeEntity 对象
    #     stmt = select(self.model).options(selectinload(self.model.sources)).where(
    #         self.model.uuid == knowledge_relationship_uuid)
    #     result = await db.execute(stmt)
    #     knowledge_relationship = result.scalars().first()
    #
    #     if not knowledge_relationship:
    #         raise ValueError(f"KnowledgeEntity {knowledge_relationship_uuid} 不存在")
    #
    #     # 2. 获取 Source 对象
    #     stmt = select(Source).where(Source.uuid == source_uuid)
    #     result = await db.execute(stmt)
    #     source = result.scalars().first()
    #
    #     knowledge_relationship.sources.append(source)
    #
    #     try:
    #         await db.commit()
    #         return 1  # 返回受影响的行数
    #     except IntegrityError as e:
    #         await db.rollback()
    #         raise Exception("添加失败，可能存在约束冲突") from e

    async def update_knowledge_relationship(
        self, db: AsyncSession, pk: int, obj: UpdateKnowledgeRelationshipParam
    ) -> int:
        """
        更新用户信息

        :param db:
        :param pk:
        :param obj:
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def update_status(self, db: AsyncSession, knowledge_relationship_id: int, status: int) -> int:
        """
        更新实体类型状态

        :param db: 异步数据库会话
        :param knowledge_relationship_id: 实体类型 ID
        :param status: 实体类型状态
        :return: 返回更新的行数
        """
        return await self.update_model(db, knowledge_relationship_id, {'status': status})

    async def update_cover_image(self, db: AsyncSession, knowledge_relationship_id: int, cover_image: str) -> int:
        """
        更新实体类型封面图

        :param db: 异步数据库会话
        :param knowledge_relationship_id: 实体类型 ID
        :param cover_image: 封面图 URL
        :return: 返回更新的行数
        """
        return await self.update_model(db, knowledge_relationship_id, {'cover_image': cover_image})

    async def get_user_schema_entities(self, db: AsyncSession, user_uuid: str) -> list[KnowledgeRelationship]:
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
knowledge_relationship_dao: CRUDKnowledgeRelationship = CRUDKnowledgeRelationship(KnowledgeRelationship)
