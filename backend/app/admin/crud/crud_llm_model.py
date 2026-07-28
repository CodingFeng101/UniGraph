from typing import Optional, Sequence

from sqlalchemy import Row, RowMapping, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, and_, desc
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model.llm_model import LlmModel
from backend.app.admin.model.llm_provider_model import LlmProvider
from backend.app.admin.schema import CreateLlmModelParam, UpdateLlmModelParam


class CRUDLlmModel(CRUDPlus[LlmModel]):
    async def get(self, db: AsyncSession, model_id: int) -> LlmModel | None:
        """
        通过 id 获取大模型信息
        """
        return await self.select_model(db, model_id)

    async def get_by_uuid(self, db: AsyncSession, model_uuid: str) -> LlmModel | None:
        """
        通过 uuid 获取大模型信息
        """
        stmt = select(self.model).where(self.model.uuid == model_uuid)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_all(
        self, db: AsyncSession, provider_uuid: str, user_uuid: str | None = None
    ) -> Sequence[Row[LlmModel] | RowMapping | LlmModel]:
        """
        获取所有大模型信息（支持条件筛选）
        """
        stmt = select(self.model).order_by(desc(self.model.created_time))
        filters = []

        if provider_uuid:
            filters.append(self.model.provider_uuid == provider_uuid)
        if user_uuid:
            stmt = stmt.join(LlmProvider, self.model.provider_uuid == LlmProvider.uuid)
            filters.append(LlmProvider.user_uuid == user_uuid)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj: CreateLlmModelParam) -> LlmModel:
        """
        创建新的大模型
        """
        model_data = obj.model_dump()
        new_model = self.model(**model_data)
        db.add(new_model)
        await db.commit()
        return new_model

    async def update(self, db: AsyncSession, model_uuid: str, obj: UpdateLlmModelParam) -> LlmModel:
        """
        更新大模型信息
        """
        model = await self.get_by_uuid(db, model_uuid)
        if not model:
            raise ValueError('Model not found')

        update_data = obj.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(model, key, value)

        db.add(model)
        await db.commit()
        return model

    async def set_status(self, db: AsyncSession, model_uuid: str, status: int) -> int:
        """
        设置大模型状态
        """
        model = await self.get_by_uuid(db, model_uuid)
        if not model:
            raise ValueError('Model not found')

        model.status = status
        db.add(model)
        await db.commit()
        return 1

    async def get_list(self, status: Optional[int] = None) -> Select:
        """
        构建复杂查询语句
        """
        stmt = select(self.model).order_by(desc(self.model.updated_time))
        filters = []

        if status is not None:
            filters.append(self.model.status == status)

        if filters:
            stmt = stmt.where(and_(*filters))

        return stmt

    async def delete(self, db: AsyncSession, model_uuid: str) -> bool:
        """
        删除大模型
        """
        model = await self.get_by_uuid(db, model_uuid)
        if model:
            await db.delete(model)
            await db.commit()
        return True


llm_model_dao: CRUDLlmModel = CRUDLlmModel(LlmModel)
