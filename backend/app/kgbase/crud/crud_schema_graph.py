from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import User
from backend.app.kgbase.model import SchemaGraph
from backend.app.kgbase.model.kg_base import KgBase
from backend.app.kgbase.model.knowledge_graph import KnowledgeGraph
from backend.app.kgbase.schema.schema_graph import (
    SchemaGraphBase,
    UpdateSchemaGraphBase,
)


class CRUDSchemaGraph(CRUDPlus[SchemaGraph]):
    async def get(self, db: AsyncSession, schema_graph_id: int) -> SchemaGraph | None:
        """
        获取架构图谱

        :param db: 异步数据库会话
        :param schema_graph_id: 架构图谱 ID
        :return: 返回架构图谱对象或者 None
        """
        return await self.select_model(db, schema_graph_id)

    async def get_by_name(self, db: AsyncSession, name: str, kg_base_uuid: str) -> SchemaGraph | None:
        """
        通过名称获取架构图谱

        :param db: 异步数据库会话
        :param name: 架构图谱名称
        :return: 返回架构图谱对象，或者 None
        """
        return await self.select_model_by_column(db, name=name, kg_base_uuid=kg_base_uuid)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> SchemaGraph | None:
        """
        通过名称获取架构图谱

        :param uuid:
        :param db: 异步数据库会话
        :return: 返回架构图谱对象，或者 None
        """
        return await self.select_model_by_column(db, uuid=uuid)

    async def create(self, db: AsyncSession, obj: SchemaGraphBase) -> str:
        """
        创建架构图谱

        :param db: 异步数据库会话
        :param obj: 架构图谱数据对象
        :return: 无返回值
        """
        dict_obj = obj.model_dump()
        new_schema_graph = self.model(**dict_obj)
        db.add(new_schema_graph)
        return new_schema_graph.uuid

    async def update(self, db: AsyncSession, schema_graph_id: int, obj: UpdateSchemaGraphBase) -> int:
        """
        更新架构图谱

        :param db: 异步数据库会话
        :param schema_graph_id: 架构图谱 ID
        :param obj: 架构图谱更新数据
        :return: 返回受影响的行数
        """
        return await self.update_model(db, schema_graph_id, obj)

    async def delete(self, db: AsyncSession, schema_graph_id: int) -> int:
        """
        删除架构图谱

        :param db: 异步数据库会话
        :param schema_graph_id: 架构图谱 ID
        :return: 返回受影响的行数
        """
        try:
            # 尝试删除模型
            return await self.delete_model(db, schema_graph_id)
        except Exception as e:
            raise e  # 继续抛出异常让上层捕获

    async def get_list(self, db: AsyncSession, *, kg_base_uuid: str, name: str = None) -> list[SchemaGraph]:
        """
        获取架构图谱列表

        :param db:
        :param kg_base_uuid:
        :param name: 架构图谱名称（模糊查询）
        :return: 返回 SQL 查询语句
        """
        stmt = select(self.model).order_by(self.model.created_time)
        where_list = [self.model.kg_base_uuid == kg_base_uuid]
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        schema_graph = await db.execute(stmt)

        return schema_graph.scalars().all()

    async def get_with_relation(self, db: AsyncSession, *, uuid: str = None, name: str = None) -> SchemaGraph | None:
        """
        :param uuid:
        :param status:
        :param name:
        :param kg_base_uuid:
        :param db:
        :return:
        """
        stmt = (
            select(self.model)
            .options(selectinload(self.model.knowledge_graphs))
            .options(selectinload(self.model.entities))
            .options(selectinload(self.model.relationships))
        )
        where_list = [self.model.uuid == uuid]
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        schema_graph = await db.execute(stmt)

        return schema_graph.scalars().first()

    async def get_with_user(self, db: AsyncSession, schema_graph_id: int) -> SchemaGraph | None:
        """
        获取架构图谱及其关联的用户信息

        :param db: 异步数据库会话
        :param schema_graph_id: 架构图谱 ID
        :return: 返回架构图谱和用户对象，或者 None
        """
        stmt = select(self.model).options(self.model.user).filter(self.model.id == schema_graph_id)
        schema_graph = await db.execute(stmt)
        return schema_graph.scalars().first()

    async def update_status(self, db: AsyncSession, schema_graph_id: int, status: int) -> int:
        """
        更新架构图谱状态

        :param db: 异步数据库会话
        :param schema_graph_id: 架构图谱 ID
        :param status: 架构图谱状态
        :return: 返回更新的行数
        """
        return await self.update_model(db, schema_graph_id, {'status': status})

    async def update_cover_image(self, db: AsyncSession, schema_graph_id: int, cover_image: str) -> int:
        """
        更新架构图谱封面图

        :param db: 异步数据库会话
        :param schema_graph_id: 架构图谱 ID
        :param cover_image: 封面图 URL
        :return: 返回更新的行数
        """
        return await self.update_model(db, schema_graph_id, {'cover_image': cover_image})

    async def get_user_schema_graphs(self, db: AsyncSession, user_uuid: str) -> list[SchemaGraph]:
        """
        获取指定用户的所有架构图谱

        :param db: 异步数据库会话
        :param user_uuid: 用户 UUID
        :return: 返回用户关联的所有架构图谱
        """
        stmt = select(self.model).filter(self.model.user_uuid == user_uuid)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_key_and_url_by_kg_base_uuid(self, db: AsyncSession, kg_base_uuid: str) -> dict | None:
        # 1. 从 kg_base 表查询 user_uuid
        stmt = select(KgBase.user_uuid).filter(KgBase.uuid == kg_base_uuid)
        result = await db.execute(stmt)
        user_uuid = result.scalar_one_or_none()
        if not user_uuid:
            return None  # 如果 kg_base 表中找不到 user_uuid，直接返回 None

        # 2、 查询 sys_user 表
        stmt = select(User).filter(User.uuid == user_uuid)
        user = await db.execute(stmt)
        user = user.scalar_one_or_none()
        print(f'api_key:{user.api_key}')
        if user:
            return user.api_key, user.base_url
        return None

    async def search_schema_related_knowledge_graph(self, db: AsyncSession, schema_graph_uuid: str) -> bool:
        stmt = select(KnowledgeGraph.uuid).filter(KnowledgeGraph.schema_graph_uuid == schema_graph_uuid)
        result = await db.execute(stmt)
        knowledge_graph_uuid = result.scalar_one_or_none()
        if knowledge_graph_uuid:
            return True
        else:
            return False

    async def get_key_and_url_by_schema_graph_uuid(
        self, db: AsyncSession, schema_graph_uuid: str
    ) -> tuple[str, str] | None:
        # 1. 从 schema_graph 表查询 kg_base_uuid
        stmt = select(SchemaGraph.kg_base_uuid).filter(SchemaGraph.uuid == schema_graph_uuid)
        result = await db.execute(stmt)
        kg_base_uuid = result.scalar_one_or_none()

        if not kg_base_uuid:
            return None  # 如果 schema_graph 中找不到对应的 kg_base_uuid，直接返回 None

        # 2. 从 kg_base 表查询 user_uuid
        stmt = select(KgBase.user_uuid).filter(KgBase.uuid == kg_base_uuid)
        result = await db.execute(stmt)
        user_uuid = result.scalar_one_or_none()

        if not user_uuid:
            return None  # 如果 kg_base 表中找不到 user_uuid，直接返回 None

        # 3、 查询 sys_user 表
        stmt = select(User).filter(User.uuid == user_uuid)
        user = await db.execute(stmt)
        user = user.scalar_one_or_none()

        if user:
            return user.api_key, user.base_url
        return None

    async def get_related_knowledge_graphs(self, db: AsyncSession, schema_graph_uuid: str) -> list[int]:
        stmt = select(KnowledgeGraph.id).filter(KnowledgeGraph.schema_graph_uuid == schema_graph_uuid)
        result = await db.execute(stmt)
        ids = result.scalars().all()  # 提取所有 uuid
        knowledge_graph_ids = list(ids)
        return knowledge_graph_ids


# 实例化 CRUD 对象
schema_graph_dao: CRUDSchemaGraph = CRUDSchemaGraph(SchemaGraph)
