from fastapi import HTTPException
from sqlalchemy import select

from backend.app.admin.model import LlmModel, LlmProvider, User
from backend.common.security.jwt import jwt_decode
from backend.common.security.outbound_url import validate_outbound_http_url
from backend.common.security.secret_store import decrypt_secret, encrypt_secret
from backend.database.db_mysql import async_db_session


async def get_user_llm_info(user_token: str, model_uuid: str | None = None) -> tuple[str, str, str]:
    """Return the first active LLM configured by the task owner."""
    user_id = jwt_decode(user_token)

    async with async_db_session() as db:
        user = await db.get(User, user_id)
        if user is None or not user.status:
            raise HTTPException(status_code=401, detail='用户不存在或已停用')

        stmt = (
            select(LlmProvider, LlmModel.name.label('model_name'))
            .join(LlmModel, LlmModel.provider_uuid == LlmProvider.uuid)
            .where(
                LlmProvider.user_uuid == user.uuid,
                LlmProvider.status == 1,
                LlmProvider.api_key != '',
                LlmProvider.api_url != '',
                LlmModel.type == 'llm',
                LlmModel.status == 1,
            )
            .order_by(LlmProvider.id.asc(), LlmModel.id.asc())
        )
        if model_uuid is not None:
            stmt = stmt.where(LlmModel.uuid == model_uuid)
        configured_model = (await db.execute(stmt.limit(1))).first()
        if configured_model is not None:
            provider, model_name = configured_model
            await validate_outbound_http_url(provider.api_url)
            api_key = decrypt_secret(provider.api_key)
            encrypted_api_key = encrypt_secret(api_key)
            if encrypted_api_key != provider.api_key:
                provider.api_key = encrypted_api_key
                await db.commit()
            return api_key, provider.api_url, model_name

        if model_uuid is not None:
            raise HTTPException(status_code=400, detail='所选语言模型不存在或已停用')

        if user.api_key and user.base_url and user.model:
            await validate_outbound_http_url(user.base_url)
            api_key = decrypt_secret(user.api_key)
            encrypted_api_key = encrypt_secret(api_key)
            if encrypted_api_key != user.api_key:
                user.api_key = encrypted_api_key
                await db.commit()
            return api_key, user.base_url, user.model

    raise HTTPException(status_code=400, detail='请先在个人中心配置可用的大模型')


async def get_user_embedding_info(user_token: str) -> tuple[str, str, str]:
    """Return the user's single active embedding model configuration."""
    user_id = jwt_decode(user_token)

    async with async_db_session() as db:
        user = await db.get(User, user_id)
        if user is None or not user.status:
            raise HTTPException(status_code=401, detail='用户不存在或已停用')

        stmt = (
            select(LlmProvider, LlmModel.name.label('model_name'))
            .join(LlmModel, LlmModel.provider_uuid == LlmProvider.uuid)
            .where(
                LlmProvider.user_uuid == user.uuid,
                LlmProvider.status == 1,
                LlmProvider.api_key != '',
                LlmProvider.api_url != '',
                LlmModel.type == 'embedding',
                LlmModel.status == 1,
            )
            .order_by(LlmProvider.id.asc(), LlmModel.id.asc())
        )
        configured_model = (await db.execute(stmt.limit(1))).first()
        if configured_model is not None:
            provider, model_name = configured_model
            await validate_outbound_http_url(provider.api_url)
            api_key = decrypt_secret(provider.api_key)
            encrypted_api_key = encrypt_secret(api_key)
            if encrypted_api_key != provider.api_key:
                provider.api_key = encrypted_api_key
                await db.commit()
            return api_key, provider.api_url, model_name

    raise HTTPException(status_code=400, detail='请先在个人中心配置可用的嵌入模型')
