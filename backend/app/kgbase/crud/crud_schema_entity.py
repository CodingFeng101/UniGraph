from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.kgbase.model import SchemaEntity
from backend.app.kgbase.schema.schema_entity import AddSchemaEntityParam, SchemaEntityBase, UpdateSchemaEntityParam


class CRUDSchemaEntity(CRUDPlus[SchemaEntity]):
    async def get(self, db: AsyncSession, schema_entity_id: int) -> SchemaEntity | None:
        """
        获取实体类型

        :param db: 异步数据库会话
        :param schema_entity_id: 实体类型 ID
        :return: 返回实体类型对象或者 None
        """
        return await self.select_model(db, schema_entity_id)

    async def get_by_name_and_schema_graph_uuid(
        self, db: AsyncSession, name: str, schema_graph_uuid: str
    ) -> SchemaEntity | None:
        """
        通过名称获取实体类型

        :param db: 异步数据库会话
        :param name: 实体类型名称
        :return: 返回实体类型对象，或者 None
        """
        return await self.select_model_by_column(db, name=name, schema_graph_uuid=schema_graph_uuid)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> SchemaEntity | None:
        """
        通过名称获取实体类型

        :param uuid:
        :param db: 异步数据库会话
        :return: 返回实体类型对象，或者 None
        """
        return await self.select_model_by_column(db, uuid=uuid)

    async def create(self, db: AsyncSession, obj: AddSchemaEntityParam) -> str:
        """
        创建实体类型

        :param db: 异步数据库会话
        :param obj: 实体类型数据对象
        :return: 无返回值
        """
        dict_obj = obj.model_dump()
        dict_obj['source'] = dict_obj.get('source') or 'manual'
        dict_obj['definition'] = dict_obj.get('definition') or ''
        new_schema_entity = self.model(**dict_obj)
        db.add(new_schema_entity)

        return new_schema_entity.uuid

    async def update(self, db: AsyncSession, schema_entity_id: int, obj: UpdateSchemaEntityParam) -> int:
        """
        更新实体类型

        :param db: 异步数据库会话
        :param schema_entity_id: 实体类型 ID
        :param obj: 实体类型更新数据
        :return: 返回受影响的行数
        """
        return await self.update_model(db, schema_entity_id, obj)

    async def delete(self, db: AsyncSession, schema_entity_id: int) -> int:
        """
        删除实体类型

        :param db: 异步数据库会话
        :param schema_entity_id: 实体类型 ID
        :return: 返回受影响的行数
        """
        return await self.delete_model(db, schema_entity_id)

    async def get_list(self, db: AsyncSession, *, schema_graph_uuid: str, name: str = None) -> list[SchemaEntity]:
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

        schema_entity = await db.execute(stmt)

        return schema_entity.scalars().all()

    async def get_with_relation(
        self, db: AsyncSession, *, uuid: str = None, name: str = None, schema_graph_uuid: str = None
    ) -> SchemaEntity | None:
        """
        :param uuid:
        :param schema_graph_uuid:
        :param name:
        :param db:
        :return:
        """
        stmt = select(self.model)
        where_list = []
        if uuid:
            where_list.append(self.model.uuid == uuid)
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if schema_graph_uuid is not None:
            where_list.append(self.model.schema_graph_uuid == schema_graph_uuid)

        if where_list:
            stmt = stmt.where(and_(*where_list))

        schema_entity = await db.execute(stmt)

        return schema_entity.scalars().first()

    async def get_with_user(self, db: AsyncSession, schema_entity_id: int) -> SchemaEntity | None:
        """
        获取实体类型及其关联的用户信息

        :param db: 异步数据库会话
        :param schema_entity_id: 实体类型 ID
        :return: 返回实体类型和用户对象，或者 None
        """
        stmt = select(self.model).options(self.model.user).filter(self.model.id == schema_entity_id)
        schema_entity = await db.execute(stmt)
        return schema_entity.scalars().first()

    async def update_schema_entity(self, db: AsyncSession, pk: int, obj: SchemaEntityBase) -> int:
        """
        更新用户信息

        :param db:
        :param pk:
        :param obj:
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def update_status(self, db: AsyncSession, schema_entity_id: int, status: int) -> int:
        """
        更新实体类型状态

        :param db: 异步数据库会话
        :param schema_entity_id: 实体类型 ID
        :param status: 实体类型状态
        :return: 返回更新的行数
        """
        return await self.update_model(db, schema_entity_id, {'status': status})

    async def update_cover_image(self, db: AsyncSession, schema_entity_id: int, cover_image: str) -> int:
        """
        更新实体类型封面图

        :param db: 异步数据库会话
        :param schema_entity_id: 实体类型 ID
        :param cover_image: 封面图 URL
        :return: 返回更新的行数
        """
        return await self.update_model(db, schema_entity_id, {'cover_image': cover_image})

    async def get_user_schema_entities(self, db: AsyncSession, user_uuid: str) -> list[SchemaEntity]:
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
schema_entity_dao: CRUDSchemaEntity = CRUDSchemaEntity(SchemaEntity)
