from __future__ import annotations

from sqlalchemy import Select, and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.kgbase.model import KgBase
from backend.app.kgbase.schema.kg_base import AddKgBaseParam, UpdateKgBaseParam


class CRUDKgBase(CRUDPlus[KgBase]):
    async def get(self, db: AsyncSession, kg_base_id: int) -> KgBase | None:
        """
        获取图谱库

        :param db: 异步数据库会话
        :param kg_base_id: 图谱库 ID
        :return: 返回图谱库对象或者 None
        """
        return await self.select_model(db, kg_base_id)

    async def get_by_name(self, db: AsyncSession, name: str, user_uuid: str) -> KgBase | None:
        """
        通过名称获取图谱库

        :param db: 异步数据库会话
        :param name: 图谱库名称
        :param user_uuid: 用户 UUID
        :return: 返回图谱库对象，或者 None
        """
        return await self.select_model_by_column(db, name=name, user_uuid=user_uuid)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> KgBase | None:
        """
        通过名称获取图谱库

        :param uuid:
        :param db: 异步数据库会话
        :return: 返回图谱库对象，或者 None
        """
        return await self.select_model_by_column(db, uuid=uuid)

    async def create(self, db: AsyncSession, obj: AddKgBaseParam) -> None:
        """
        创建图谱库

        :param db: 异步数据库会话
        :param obj: 图谱库数据对象
        :return: 无返回值
        """
        dict_obj = obj.model_dump()
        new_kg_base = self.model(**dict_obj)
        db.add(new_kg_base)

    async def update(self, db: AsyncSession, kg_base_id: int, obj: UpdateKgBaseParam) -> int:
        """
        更新图谱库

        :param db: 异步数据库会话
        :param kg_base_id: 图谱库 ID
        :param obj: 图谱库更新数据
        :return: 返回受影响的行数
        """
        return await self.update_model(db, kg_base_id, obj)

    async def delete(self, db: AsyncSession, kg_base_id: int) -> int:
        """
        删除图谱库

        :param db: 异步数据库会话
        :param kg_base_id: 图谱库 ID
        :return: 返回受影响的行数
        """
        return await self.delete_model(db, kg_base_id)

    async def get_list(self, user_uuid: str, name: str = None, status: int = None) -> Select:
        """
        获取图谱库列表

        :param user_uuid:
        :param name: 图谱库名称（模糊查询）
        :param status: 图谱库状态（1：正常，0：禁用）
        :return: 返回 SQL 查询语句
        """
        stmt = select(self.model).order_by(desc(self.model.created_time))
        where_list = [self.model.user_uuid == user_uuid]
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if status is not None:
            where_list.append(self.model.status == status)

        if where_list:
            stmt = stmt.where(and_(*where_list))

        return stmt

    async def get_with_relation(
        self, db: AsyncSession, *, user_uuid: str = None, uuid: str = None, name: str = None, status: int = None
    ) -> KgBase | None:
        """
        :param uuid:
        :param status:
        :param name:
        :param user_uuid:
        :param db:
        :return:
        """
        stmt = (
            select(self.model)
            .options(selectinload(self.model.knowledge_graphs))
            .options(selectinload(self.model.schema_graphs))
        )
        where_list = []
        if user_uuid:
            where_list.append(self.model.user_uuid == user_uuid)
        if uuid:
            where_list.append(self.model.uuid == uuid)
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if status is not None:
            where_list.append(self.model.status == status)

        if where_list:
            stmt = stmt.where(and_(*where_list))

        kg_base = await db.execute(stmt)

        return kg_base.scalars().first()

    async def get_with_user(self, db: AsyncSession, kg_base_id: int) -> KgBase | None:
        """
        获取图谱库及其关联的用户信息

        :param db: 异步数据库会话
        :param kg_base_id: 图谱库 ID
        :return: 返回图谱库和用户对象，或者 None
        """
        stmt = select(self.model).options(self.model.user).filter(self.model.id == kg_base_id)
        kg_base = await db.execute(stmt)
        return kg_base.scalars().first()

    async def update_kg_base(self, db: AsyncSession, pk: int, obj: UpdateKgBaseParam) -> int:
        """
        更新用户信息

        :param db:
        :param pk:
        :param obj:
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def update_status(self, db: AsyncSession, kg_base_id: int, status: int) -> int:
        """
        更新图谱库状态

        :param db: 异步数据库会话
        :param kg_base_id: 图谱库 ID
        :param status: 图谱库状态
        :return: 返回更新的行数
        """
        return await self.update_model(db, kg_base_id, {'status': status})

    async def update_cover_image(self, db: AsyncSession, kg_base_id: int, cover_image: str) -> int:
        """
        更新图谱库封面图

        :param db: 异步数据库会话
        :param kg_base_id: 图谱库 ID
        :param cover_image: 封面图 URL
        :return: 返回更新的行数
        """
        return await self.update_model(db, kg_base_id, {'cover_image': cover_image})

    async def get_user_kg_bases(self, db: AsyncSession, user_uuid: str) -> list[KgBase]:
        """
        获取指定用户的所有图谱库

        :param db: 异步数据库会话
        :param user_uuid: 用户 UUID
        :return: 返回用户关联的所有图谱库
        """
        stmt = select(self.model).filter(self.model.user_uuid == user_uuid)
        result = await db.execute(stmt)
        return result.scalars().all()


# 实例化 CRUD 对象
kg_base_dao: CRUDKgBase = CRUDKgBase(KgBase)
