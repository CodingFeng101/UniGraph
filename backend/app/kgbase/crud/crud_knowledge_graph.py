from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.kgbase.model import KnowledgeEntity, KnowledgeGraph
from backend.app.kgbase.schema.knowledge_graph import (
    KnowledgeGraphBase,
    UpdateKnowledgeGraphParam,
)


class CRUDKnowledgeGraph(CRUDPlus[KnowledgeGraph]):
    async def get(self, db: AsyncSession, knowledge_graph_id: int) -> KnowledgeGraph | None:
        """
        获取架构图谱

        :param db: 异步数据库会话
        :param knowledge_graph_id: 架构图谱 ID
        :return: 返回架构图谱对象或者 None
        """
        return await self.select_model(db, knowledge_graph_id)

    async def get_by_name(self, db: AsyncSession, name: str, kg_base_uuid: str) -> KnowledgeGraph | None:
        """
        通过名称获取架构图谱
        :param db: 异步数据库会话
        :param name: 架构图谱名称
        :param kg_base_uuid: 知识图谱基础 UUID
        :return: 返回架构图谱对象，或者 None
        """
        # 添加一个筛选条件，即kg_base_uuid
        return await self.select_model_by_column(db, name=name, kg_base_uuid=kg_base_uuid)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> KnowledgeGraph | None:
        """
        通过名称获取架构图谱

        :param uuid:
        :param db: 异步数据库会话
        :return: 返回架构图谱对象，或者 None
        """
        return await self.select_model_by_column(db, uuid=uuid)

    async def create(self, db: AsyncSession, obj: KnowledgeGraphBase) -> str:
        """
        创建架构图谱

        :param db: 异步数据库会话
        :param obj: 架构图谱数据对象
        :return: 无返回值
        """
        dict_obj = obj.model_dump()
        new_knowledge_graph = self.model(**dict_obj)
        db.add(new_knowledge_graph)
        return new_knowledge_graph.uuid

    async def update(self, db: AsyncSession, knowledge_graph_id: int, obj: UpdateKnowledgeGraphParam) -> int:
        """
        更新架构图谱

        :param db: 异步数据库会话
        :param knowledge_graph_id: 架构图谱 ID
        :param obj: 架构图谱更新数据
        :return: 返回受影响的行数
        """
        return await self.update_model(db, knowledge_graph_id, obj)

    async def delete(self, db: AsyncSession, knowledge_graph_id: int) -> int:
        """
        删除架构图谱

        :param db: 异步数据库会话
        :param knowledge_graph_id: 架构图谱 ID
        :return: 返回受影响的行数
        """
        return await self.delete_model(db, knowledge_graph_id)

    async def get_list(self, db: AsyncSession, *, kg_base_uuid: str, name: str = None) -> list[KnowledgeGraph]:
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

        knowledge_graph = await db.execute(stmt)

        return knowledge_graph.scalars().all()

    async def get_with_relation(self, db: AsyncSession, *, uuid: str = None, name: str = None) -> KnowledgeGraph | None:
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
            .options(selectinload(self.model.schema_graph))  # 继续使用 selectinload 加载 schema_graph
            .options(
                selectinload(self.model.entities)
                .options(selectinload(KnowledgeEntity.embeddings))
                .options(selectinload(KnowledgeEntity.communities))
            )
            .options(selectinload(self.model.relationships))  # 使用 selectinload 加载 relationships
            .options(selectinload(self.model.communities))  # 使用 selectinload 加载 communities
        )

        where_list = [self.model.uuid == uuid]
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        knowledge_graph = await db.execute(stmt)

        return knowledge_graph.scalars().first()

    async def get_with_user(self, db: AsyncSession, knowledge_graph_id: int) -> KnowledgeGraph | None:
        """
        获取架构图谱及其关联的用户信息

        :param db: 异步数据库会话
        :param knowledge_graph_id: 架构图谱 ID
        :return: 返回架构图谱和用户对象，或者 None
        """
        stmt = select(self.model).options(self.model.user).filter(self.model.id == knowledge_graph_id)
        knowledge_graph = await db.execute(stmt)
        return knowledge_graph.scalars().first()

    async def get_depth(self, db: AsyncSession, uuid: str) -> int:
        """
        获取架构图谱及其关联的用户信息

        :param db: 异步数据库会话
        :param uuid: 架构图谱 ID
        :return: 返回架构图谱和用户对象，或者 None
        """
        stmt = select(self.model.depth).filter(self.model.uuid == uuid)
        knowledge_graph = await db.execute(stmt)
        return knowledge_graph.scalars().first()

    async def update_knowledge_graph(self, db: AsyncSession, pk: int, obj: UpdateKnowledgeGraphParam) -> int:
        """
        更新用户信息

        :param db:
        :param pk:
        :param obj:
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def update_status(self, db: AsyncSession, knowledge_graph_id: int, index_status: int) -> int:
        """
        更新架构图谱状态

        :param db: 异步数据库会话
        :param knowledge_graph_id: 架构图谱 ID
        :param index_status: 架构图谱状态
        :return: 返回更新的行数
        """
        return await self.update_model(db, knowledge_graph_id, {'index_status': index_status})

    async def update_depth(self, db: AsyncSession, knowledge_graph_id: int, depth: int) -> int:
        """
        更新架构图谱深度
        :param db:
        :param knowledge_graph_id:
        :param depth:
        :return:
        """
        return await self.update_model(db, knowledge_graph_id, {'depth': depth})

    async def update_cover_image(self, db: AsyncSession, knowledge_graph_id: int, cover_image: str) -> int:
        """
        更新架构图谱封面图

        :param db: 异步数据库会话
        :param knowledge_graph_id: 架构图谱 ID
        :param cover_image: 封面图 URL
        :return: 返回更新的行数
        """
        return await self.update_model(db, knowledge_graph_id, {'cover_image': cover_image})

    async def get_user_knowledge_graphs(self, db: AsyncSession, user_uuid: str) -> list[KnowledgeGraph]:
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
knowledge_graph_dao: CRUDKnowledgeGraph = CRUDKnowledgeGraph(KnowledgeGraph)
