from typing import Optional, Sequence

from backend.app.admin.crud.crud_llm_model import llm_model_dao
from backend.app.admin.model.llm_model import LlmModel
from backend.app.admin.schema import CreateLlmModelParam, UpdateLlmModelParam
from backend.database.db_mysql import async_db_session


class LlmModelService:
    @staticmethod
    async def add(*, obj: CreateLlmModelParam) -> LlmModel:
        """创建大模型模型"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    return await llm_model_dao.create(db, obj)
                except Exception as e:
                    await db.rollback()
                    raise ValueError(f'创建模型失败: {str(e)}') from e

    @staticmethod
    async def get_all(*, llm_provider_uuid: str = None, user_uuid: str | None = None) -> Sequence[LlmModel]:
        """获取所有模型（支持过滤）"""
        async with async_db_session() as db:
            return await llm_model_dao.get_all(
                db,
                provider_uuid=llm_provider_uuid,
                user_uuid=user_uuid,
            )

    @staticmethod
    async def update(*, llm_model_uuid: str, obj: UpdateLlmModelParam) -> Optional[LlmModel]:
        """更新模型信息"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    return await llm_model_dao.update(db, model_uuid=llm_model_uuid, obj=obj)
                except ValueError as e:
                    await db.rollback()
                    raise ValueError(f'模型不存在: {llm_model_uuid}') from e
                except Exception as e:
                    await db.rollback()
                    raise RuntimeError(f'更新失败: {str(e)}') from e

    @staticmethod
    async def delete(*, llm_model_uuid: str) -> bool:
        """删除模型"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    return await llm_model_dao.delete(db, llm_model_uuid)
                except Exception as e:
                    await db.rollback()
                    raise RuntimeError(f'删除失败: {str(e)}') from e

    @staticmethod
    async def get_detail(model_uuid: str) -> Optional[LlmModel]:
        """获取模型详情"""
        async with async_db_session() as db:
            return await llm_model_dao.get_by_uuid(db, model_uuid=model_uuid)

    @staticmethod
    async def set_status(model_uuid: str, status: int) -> bool:
        """设置模型状态"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    result = await llm_model_dao.set_status(db, model_uuid=model_uuid, status=status)
                    return result == 1
                except Exception as e:
                    await db.rollback()
                    raise ValueError(f'状态更新失败: {str(e)}') from e
