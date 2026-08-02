from typing import Optional, Sequence

from sqlalchemy import select

from backend.app.admin.crud.crud_llm_model import llm_model_dao
from backend.app.admin.model.llm_model import LlmModel
from backend.app.admin.model.llm_provider_model import LlmProvider
from backend.app.admin.schema import CreateLlmModelParam, UpdateLlmModelParam
from backend.database.db_mysql import async_db_session


class LlmModelService:
    EMBEDDING_TYPES = {'embedding', 'text-embedding'}

    @staticmethod
    async def _get_owned_model(db, *, model_uuid: str, user_uuid: str) -> LlmModel | None:
        result = await db.execute(
            select(LlmModel)
            .join(LlmProvider, LlmModel.provider_uuid == LlmProvider.uuid)
            .where(LlmModel.uuid == model_uuid, LlmProvider.user_uuid == user_uuid)
        )
        return result.scalars().first()

    @classmethod
    async def _ensure_single_embedding(
        cls,
        db,
        *,
        user_uuid: str,
        exclude_model_uuid: str | None = None,
    ) -> None:
        stmt = (
            select(LlmModel.uuid)
            .join(LlmProvider, LlmModel.provider_uuid == LlmProvider.uuid)
            .where(
                LlmProvider.user_uuid == user_uuid,
                LlmProvider.status == 1,
                LlmModel.type.in_(cls.EMBEDDING_TYPES),
                LlmModel.status == 1,
            )
            .limit(1)
        )
        if exclude_model_uuid:
            stmt = stmt.where(LlmModel.uuid != exclude_model_uuid)
        if (await db.execute(stmt)).scalar_one_or_none() is not None:
            raise ValueError('每个用户只能配置一个嵌入模型')

    @staticmethod
    async def add(*, obj: CreateLlmModelParam, user_uuid: str) -> LlmModel:
        """创建大模型模型"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    provider = (
                        (
                            await db.execute(
                                select(LlmProvider).where(
                                    LlmProvider.uuid == obj.provider_uuid,
                                    LlmProvider.user_uuid == user_uuid,
                                )
                            )
                        )
                        .scalars()
                        .first()
                    )
                    if provider is None:
                        raise ValueError('模型提供商不存在')
                    if obj.type in LlmModelService.EMBEDDING_TYPES and obj.status == 1:
                        await LlmModelService._ensure_single_embedding(db, user_uuid=user_uuid)
                    return await llm_model_dao.create(db, obj)
                except ValueError:
                    await db.rollback()
                    raise
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
    async def update(*, llm_model_uuid: str, obj: UpdateLlmModelParam, user_uuid: str) -> Optional[LlmModel]:
        """更新模型信息"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    model = await LlmModelService._get_owned_model(db, model_uuid=llm_model_uuid, user_uuid=user_uuid)
                    if model is None:
                        raise ValueError('模型不存在')
                    target_type = obj.type if obj.type is not None else model.type
                    target_status = obj.status if obj.status is not None else model.status
                    if target_type in LlmModelService.EMBEDDING_TYPES and target_status == 1:
                        await LlmModelService._ensure_single_embedding(
                            db,
                            user_uuid=user_uuid,
                            exclude_model_uuid=llm_model_uuid,
                        )
                    return await llm_model_dao.update(db, model_uuid=llm_model_uuid, obj=obj)
                except ValueError:
                    await db.rollback()
                    raise
                except Exception as e:
                    await db.rollback()
                    raise RuntimeError(f'更新失败: {str(e)}') from e

    @staticmethod
    async def delete(*, llm_model_uuid: str, user_uuid: str) -> bool:
        """删除模型"""
        async with async_db_session() as db:
            async with db.begin():
                try:
                    model = await LlmModelService._get_owned_model(db, model_uuid=llm_model_uuid, user_uuid=user_uuid)
                    if model is None:
                        return False
                    return await llm_model_dao.delete(db, llm_model_uuid)
                except Exception as e:
                    await db.rollback()
                    raise RuntimeError(f'删除失败: {str(e)}') from e

    @staticmethod
    async def get_detail(model_uuid: str, user_uuid: str) -> Optional[LlmModel]:
        """获取模型详情"""
        async with async_db_session() as db:
            return await LlmModelService._get_owned_model(db, model_uuid=model_uuid, user_uuid=user_uuid)

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
