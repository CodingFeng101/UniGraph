from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.kgbase.model import Embedding
from backend.app.kgbase.schema.embedding import EmbeddingBase, UpdateEmbeddingParam


class CRUDEmbedding(CRUDPlus[Embedding]):
    async def get(self, db: AsyncSession, embedding_id: int) -> Embedding | None:
        """
        获取架构图谱

        :param db: 异步数据库会话
        :param embedding_id: 架构图谱 ID
        :return: 返回架构图谱对象或者 None
        """
        return await self.select_model(db, embedding_id)

    async def get_by_name(self, db: AsyncSession, name: str) -> Embedding | None:
        """
        通过名称获取架构图谱

        :param db: 异步数据库会话
        :param name: 架构图谱名称
        :return: 返回架构图谱对象，或者 None
        """
        return await self.select_model_by_column(db, name=name)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Embedding | None:
        """
        通过名称获取架构图谱

        :param uuid:
        :param db: 异步数据库会话
        :return: 返回架构图谱对象，或者 None
        """
        return await self.select_model_by_column(db, knowledge_entity_uuid=uuid)

    async def create(self, db: AsyncSession, obj: EmbeddingBase) -> str:
        """
        创建实体向量
        :param db: 异步数据库会话
        :param obj: 架构图谱数据对象
        :return: 无返回值
        """
        dict_obj = obj.model_dump()
        new_embedding = self.model(**dict_obj)
        db.add(new_embedding)
        return new_embedding.uuid

    async def update(self, db: AsyncSession, embedding_id: int, obj: UpdateEmbeddingParam) -> int:
        """
        更新架构图谱

        :param db: 异步数据库会话
        :param embedding_id: 架构图谱 ID
        :param obj: 架构图谱更新数据
        :return: 返回受影响的行数
        """
        return await self.update_model(db, embedding_id, obj)

    async def delete(self, db: AsyncSession, embedding_id: int) -> int:
        """
        删除架构图谱

        :param db: 异步数据库会话
        :param embedding_id: 架构图谱 ID
        :return: 返回受影响的行数
        """
        return await self.delete_model(db, embedding_id)

    async def get_list(self, db: AsyncSession, *, knowledge_entity_uuid: str, name: str = None) -> list[Embedding]:
        """
        获取所需向量

        :param db:
        :param knowledge_entity_uuid:
        :param name: 架构图谱名称（模糊查询）
        :return: 返回 SQL 查询语句
        """
        stmt = select(self.model).order_by(self.model.created_time)
        where_list = [self.model.knowledge_entity_uuid == knowledge_entity_uuid]
        if name:
            where_list.append(self.model.knowledge_entity.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        embedding = await db.execute(stmt)

        return embedding.scalars().all()

    async def get_with_relation(
        self, db: AsyncSession, *, uuid: str = None, knowledge_entity_uuid: str = None
    ) -> Embedding | None:
        """
        :param uuid:
        :param knowledge_entity_uuid:
        :param db:
        :return:
        """
        stmt = select(self.model)
        where_list = []
        if uuid:
            where_list.append(self.model.uuid == uuid)
        if knowledge_entity_uuid:
            where_list.append(self.model.knowledge_entity_uuid == knowledge_entity_uuid)
        if where_list:
            stmt = stmt.where(and_(*where_list))

        embedding = await db.execute(stmt)

        return embedding.scalars().first()

    async def update_embedding(self, db: AsyncSession, pk: int, obj: EmbeddingBase) -> int:
        """
        更新用户信息

        :param db:
        :param pk:
        :param obj:
        :return:
        """
        return await self.update_model(db, pk, obj)


# 实例化 CRUD 对象
embedding_dao: CRUDEmbedding = CRUDEmbedding(Embedding)
