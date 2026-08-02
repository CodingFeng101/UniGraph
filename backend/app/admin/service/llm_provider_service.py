from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.admin.crud.crud_llm_provider import llm_provider_dao
from backend.app.admin.model.llm_provider_model import LlmProvider
from backend.app.admin.schema import CreateLlmProviderParam, UpdateLlmProviderParam
from backend.common.security.secret_store import encrypt_secret
from backend.database.db_mysql import async_db_session


class LlmProviderService:
    @staticmethod
    async def _get_owned_provider(db, *, provider_uuid: str, user_uuid: str, with_models: bool = False):
        statement = select(LlmProvider).where(
            LlmProvider.uuid == provider_uuid,
            LlmProvider.user_uuid == user_uuid,
        )
        if with_models:
            statement = statement.options(selectinload(LlmProvider.models))
        return (await db.execute(statement)).scalars().first()

    @staticmethod
    async def add(*, obj: CreateLlmProviderParam) -> LlmProvider:
        """创建大模型提供商"""
        obj.api_key = encrypt_secret(obj.api_key or '')
        async with async_db_session() as db:
            async with db.begin():
                try:
                    return await llm_provider_dao.create(db, obj)
                except Exception as e:
                    await db.rollback()
                    raise ValueError(f'创建提供商失败: {str(e)}') from e

    @staticmethod
    async def get_all(*, user_uuid: str = None, name: str = None) -> Sequence[LlmProvider]:
        """获取所有提供商（支持过滤）"""
        async with async_db_session() as db:
            return await llm_provider_dao.get_all(db, user_uuid=user_uuid, name=name)

    @staticmethod
    async def update(*, llm_provider_uuid: str, obj: UpdateLlmProviderParam, user_uuid: str) -> Optional[LlmProvider]:
        """更新提供商信息"""
        if obj.api_key is not None:
            obj.api_key = encrypt_secret(obj.api_key)
        async with async_db_session() as db:
            async with db.begin():
                try:
                    if (
                        await LlmProviderService._get_owned_provider(
                            db, provider_uuid=llm_provider_uuid, user_uuid=user_uuid
                        )
                        is None
                    ):
                        return None
                    return await llm_provider_dao.update(db, provider_uuid=llm_provider_uuid, obj=obj)
                except ValueError as e:
                    await db.rollback()
                    raise ValueError(f'提供商不存在: {llm_provider_uuid}') from e
                except Exception as e:
                    await db.rollback()
                    raise RuntimeError(f'更新失败: {str(e)}') from e

    @staticmethod
    async def delete(*, llm_provider_uuid: str, user_uuid: str) -> bool:
        """删除提供商"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    if (
                        await LlmProviderService._get_owned_provider(
                            db, provider_uuid=llm_provider_uuid, user_uuid=user_uuid
                        )
                        is None
                    ):
                        return False
                    return await llm_provider_dao.delete(db, llm_provider_uuid)
                except Exception as e:
                    await db.rollback()
                    raise RuntimeError(f'删除失败: {str(e)}') from e

    @staticmethod
    async def get_detail(provider_uuid: str, user_uuid: str) -> Optional[LlmProvider]:
        """获取包含关联模型的提供商详情"""
        async with async_db_session() as db:
            return await LlmProviderService._get_owned_provider(
                db, provider_uuid=provider_uuid, user_uuid=user_uuid, with_models=True
            )

    @staticmethod
    async def set_status(provider_uuid: str, status: int) -> bool:
        """设置提供商状态"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    result = await llm_provider_dao.set_status(db, provider_uuid=provider_uuid, status=status)
                    return result == 1
                except Exception as e:
                    await db.rollback()
                    raise ValueError(f'状态更新失败: {str(e)}') from e
