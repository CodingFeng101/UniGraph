from __future__ import annotations

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.kgbase.model import SchemaRelationship
from backend.app.kgbase.schema.schema_relationship import (
    AddSchemaRelationshipParam,
    UpdateSchemaRelationshipParam,
)


class CRUDSchemaRelationship(CRUDPlus[SchemaRelationship]):
    async def get(self, db: AsyncSession, schema_relationship_id: int) -> SchemaRelationship | None:
        """
        获取实体类型

        :param db: 异步数据库会话
        :param schema_relationship_id: 实体类型 ID
        :return: 返回实体类型对象或者 None
        """
        return await self.select_model(db, schema_relationship_id)

    async def get_by_name(self, db: AsyncSession, name: str) -> SchemaRelationship | None:
        """
        通过名称获取实体类型

        :param db: 异步数据库会话
        :param name: 实体类型名称
        :return: 返回实体类型对象，或者 None
        """
        return await self.select_model_by_column(db, name=name)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> SchemaRelationship | None:
        """
        通过名称获取实体类型

        :param uuid:
        :param db: 异步数据库会话
        :return: 返回实体类型对象，或者 None
        """
        return await self.select_model_by_column(db, uuid=uuid)

    async def create(self, db: AsyncSession, obj: AddSchemaRelationshipParam) -> str:
        """
        创建实体类型

        :param db: 异步数据库会话
        :param obj: 实体类型数据对象
        :return: 无返回值
        """
        dict_obj = obj.model_dump()
        new_schema_relationship = self.model(**dict_obj)
        db.add(new_schema_relationship)
        return new_schema_relationship.uuid

    async def update(self, db: AsyncSession, schema_relationship_id: int, obj: UpdateSchemaRelationshipParam) -> int:
        """
        更新实体类型

        :param db: 异步数据库会话
        :param schema_relationship_id: 实体类型 ID
        :param obj: 实体类型更新数据
        :return: 返回受影响的行数
        """
        return await self.update_model(db, schema_relationship_id, obj)

    async def delete(self, db: AsyncSession, schema_relationship_id: int) -> int:
        """
        删除实体类型

        :param db: 异步数据库会话
        :param schema_relationship_id: 实体类型 ID
        :return: 返回受影响的行数
        """
        return await self.delete_model(db, schema_relationship_id)

    async def get_list(self, db: AsyncSession, *, schema_graph_uuid: str, name: str = None) -> list[SchemaRelationship]:
        """
        获取实体类型列表

        :param db:
        :param schema_graph_uuid:
        :param name: 实体类型名称（模糊查询）
        :return: 返回 SQL 查询语句
        """
        stmt = select(self.model).order_by(self.model.created_time)
        where_list = [self.model.schema_graph_uuid == schema_graph_uuid]
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if where_list:
            stmt = stmt.where(and_(*where_list))

        schema_relationship = await db.execute(stmt)

        return schema_relationship.scalars().all()

    async def get_with_relation(
        self, db: AsyncSession, *, user_uuid: str = None, uuid: str = None, name: str = None, status: int = None
    ) -> SchemaRelationship | None:
        """
        :param uuid:
        :param status:
        :param name:
        :param user_uuid:
        :param db:
        :return:
        """
        stmt = select(self.model)
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

        schema_relationship = await db.execute(stmt)

        return schema_relationship.scalars().first()

    async def get_with_user(self, db: AsyncSession, schema_relationship_id: int) -> SchemaRelationship | None:
        """
        获取实体类型及其关联的用户信息

        :param db: 异步数据库会话
        :param schema_relationship_id: 实体类型 ID
        :return: 返回实体类型和用户对象，或者 None
        """
        stmt = select(self.model).options(self.model.user).filter(self.model.id == schema_relationship_id)
        schema_relationship = await db.execute(stmt)
        return schema_relationship.scalars().first()

    async def update_schema_relationship(self, db: AsyncSession, pk: int, obj: UpdateSchemaRelationshipParam) -> int:
        """
        更新用户信息

        :param db:
        :param pk:
        :param obj:
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def update_status(self, db: AsyncSession, schema_relationship_id: int, status: int) -> int:
        """
        更新实体类型状态

        :param db: 异步数据库会话
        :param schema_relationship_id: 实体类型 ID
        :param status: 实体类型状态
        :return: 返回更新的行数
        """
        return await self.update_model(db, schema_relationship_id, {'status': status})

    async def update_cover_image(self, db: AsyncSession, schema_relationship_id: int, cover_image: str) -> int:
        """
        更新实体类型封面图

        :param db: 异步数据库会话
        :param schema_relationship_id: 实体类型 ID
        :param cover_image: 封面图 URL
        :return: 返回更新的行数
        """
        return await self.update_model(db, schema_relationship_id, {'cover_image': cover_image})

    async def get_user_schema_entities(self, db: AsyncSession, user_uuid: str) -> list[SchemaRelationship]:
        """
        获取指定用户的所有实体类型

        :param db: 异步数据库会话
        :param user_uuid: 用户 UUID
        :return: 返回用户关联的所有实体类型
        """
        stmt = select(self.model).filter(self.model.user_uuid == user_uuid)
        result = await db.execute(stmt)
        return result.scalars().all()

    # 在schema_relationship_dao中添加
    async def delete_all(self, db: AsyncSession) -> int:
        result = await db.execute(delete(self.model))
        return result.rowcount


# 实例化 CRUD 对象
schema_relationship_dao: CRUDSchemaRelationship = CRUDSchemaRelationship(SchemaRelationship)
