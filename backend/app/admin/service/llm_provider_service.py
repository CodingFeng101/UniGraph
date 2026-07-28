from typing import Optional, Sequence

from backend.app.admin.crud.crud_llm_provider import llm_provider_dao
from backend.app.admin.model.llm_provider_model import LlmProvider
from backend.app.admin.schema import CreateLlmProviderParam, UpdateLlmProviderParam
from backend.database.db_mysql import async_db_session


class LlmProviderService:
    @staticmethod
    async def add(*, obj: CreateLlmProviderParam) -> LlmProvider:
        """创建大模型提供商"""
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
    async def update(*, llm_provider_uuid: str, obj: UpdateLlmProviderParam) -> Optional[LlmProvider]:
        """更新提供商信息"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    return await llm_provider_dao.update(db, provider_uuid=llm_provider_uuid, obj=obj)
                except ValueError as e:
                    await db.rollback()
                    raise ValueError(f'提供商不存在: {llm_provider_uuid}') from e
                except Exception as e:
                    await db.rollback()
                    raise RuntimeError(f'更新失败: {str(e)}') from e

    @staticmethod
    async def delete(*, llm_provider_uuid: str) -> bool:
        """删除提供商"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    return await llm_provider_dao.delete(db, llm_provider_uuid)
                except Exception as e:
                    await db.rollback()
                    raise RuntimeError(f'删除失败: {str(e)}') from e

    @staticmethod
    async def get_detail(provider_uuid: str) -> Optional[LlmProvider]:
        """获取包含关联模型的提供商详情"""
        async with async_db_session() as db:
            return await llm_provider_dao.get_with_relation(db, provider_uuid=provider_uuid)

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
