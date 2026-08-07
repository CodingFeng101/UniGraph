from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select, and_, desc
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model.llm_provider_model import LlmProvider
from backend.app.admin.schema import CreateLlmProviderParam, UpdateLlmProviderParam


class CRUDLlmProvider(CRUDPlus[LlmProvider]):
    async def get(self, db: AsyncSession, provider_id: int) -> LlmProvider | None:
        """
        通过 id 获取提供商信息
        """
        return await self.select_model(db, provider_id)

    async def get_by_uuid(self, db: AsyncSession, provider_uuid: str) -> LlmProvider | None:
        """
        通过 uuid 获取提供商信息
        """
        stmt = select(self.model).where(self.model.uuid == provider_uuid)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_with_relation(
        self, db: AsyncSession, provider_id: int = None, provider_uuid: str = None
    ) -> LlmProvider | None:
        """
        获取关联模型信息的提供商详情
        """
        stmt = select(self.model).options(selectinload(self.model.models))

        if provider_id:
            stmt = stmt.where(self.model.id == provider_id)
        elif provider_uuid:
            stmt = stmt.where(self.model.uuid == provider_uuid)

        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_all(self, db: AsyncSession, user_uuid: str = None, name: str = None) -> Sequence[LlmProvider]:
        """
        获取所有提供商信息（支持条件筛选）
        """
        stmt = select(self.model).order_by(self.model.sort_order.asc(), self.model.id.asc())
        filters = []

        if user_uuid:
            filters.append(self.model.user_uuid == user_uuid)
        if name:
            filters.append(self.model.name.ilike(f'%{name}%'))

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj: CreateLlmProviderParam) -> LlmProvider:
        """
        创建新的提供商
        """
        provider_data = obj.model_dump()
        new_provider = self.model(**provider_data)
        max_order = await db.scalar(
            select(func.max(self.model.sort_order)).where(self.model.user_uuid == obj.user_uuid)
        )
        new_provider.sort_order = (max_order if max_order is not None else -1) + 1
        db.add(new_provider)
        await db.commit()
        return new_provider

    async def update(self, db: AsyncSession, provider_uuid: str, obj: UpdateLlmProviderParam) -> LlmProvider:
        """
        更新提供商信息
        """
        provider = await self.get_by_uuid(db, provider_uuid)
        if not provider:
            raise ValueError('Provider not found')

        update_data = obj.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(provider, key, value)

        db.add(provider)
        await db.commit()
        return provider

    async def set_status(self, db: AsyncSession, provider_uuid: str, status: int) -> int:
        """
        设置提供商状态
        """
        provider = await self.get_by_uuid(db, provider_uuid)
        if not provider:
            raise ValueError('Provider not found')

        provider.status = status
        db.add(provider)
        await db.commit()
        return 1

    async def get_list(
        self, user_uuid: Optional[str] = None, name: Optional[str] = None, status: Optional[int] = None
    ) -> Select:
        """
        构建复杂查询语句
        """
        stmt = select(self.model).order_by(desc(self.model.updated_time))
        filters = []

        if user_uuid:
            filters.append(self.model.user_uuid == user_uuid)
        if name:
            filters.append(self.model.name.ilike(f'%{name}%'))
        if status is not None:
            filters.append(self.model.status == status)

        if filters:
            stmt = stmt.where(and_(*filters))

        return stmt

    async def delete(self, db: AsyncSession, provider_uuid: str) -> bool:
        """
        删除提供商
        """
        provider = await self.get_by_uuid(db, provider_uuid)
        if provider:
            await db.delete(provider)
            await db.commit()
        return True


llm_provider_dao: CRUDLlmProvider = CRUDLlmProvider(LlmProvider)
