from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.kgbase.model import Community
from backend.app.kgbase.schema.community import CommunityBase, UpdateCommunityParam


class CRUDCommunity(CRUDPlus[Community]):
    async def get(self, db: AsyncSession, community_id: int) -> Community | None:
        """
        获取社区报告

        :param db: 异步数据库会话
        :param community_id: 社区报告 ID
        :return: 返回社区报告对象或者 None
        """
        return await self.select_model(db, community_id)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Community | None:
        """
        通过名称获取社区报告

        :param uuid:
        :param db: 异步数据库会话
        :return: 返回社区报告对象，或者 None
        """
        return await self.select_model_by_column(db, uuid=uuid)

    async def create(self, db: AsyncSession, obj: CommunityBase) -> str:
        """
        创建社区报告

        :param db: 异步数据库会话
        :param obj: 社区报告数据对象
        :return: 无返回值
        """
        dict_obj = obj.model_dump()
        new_community = self.model(**dict_obj)
        db.add(new_community)
        return new_community.uuid

    async def update(self, db: AsyncSession, community_id: int, obj: UpdateCommunityParam) -> int:
        """
        更新社区报告

        :param db: 异步数据库会话
        :param community_id: 社区报告 ID
        :param obj: 社区报告更新数据
        :return: 返回受影响的行数
        """
        return await self.update_model(db, community_id, obj)

    async def delete(self, db: AsyncSession, community_id: int) -> int:
        """
        删除社区报告

        :param db: 异步数据库会话
        :param community_id: 社区报告 ID
        :return: 返回受影响的行数
        """
        return await self.delete_model(db, community_id)

    async def get_list(self, db: AsyncSession, *, knowledge_graph_uuid: str, name: str = None) -> list[Community]:
        """
        获取社区报告列表

        :param db:
        :param knowledge_graph_uuid:
        :param name: 社区报告名称（模糊查询）
        :return: 目标社区
        """
        stmt = select(self.model).order_by(self.model.created_time)
        where_list = [self.model.knowledge_graph_uuid == knowledge_graph_uuid]
        if name:
            where_list.append(self.model.title.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        community = await db.execute(stmt)

        return community.scalars().all()

    async def get_with_relation(self, db: AsyncSession, *, uuid: str = None, name: str = None) -> Community | None:
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

        community = await db.execute(stmt)

        return community.scalars().first()

    async def update_community(self, db: AsyncSession, pk: int, obj: UpdateCommunityParam) -> int:
        """
        更新用户信息

        :param db:
        :param pk:
        :param obj:
        :return:
        """
        return await self.update_model(db, pk, obj)


# 实例化 CRUD 对象
community_dao: CRUDCommunity = CRUDCommunity(Community)
