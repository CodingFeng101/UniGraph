from fastapi import APIRouter

from backend.app.admin.service.llm_create_service import LlmCreateService
from backend.common.response.response_schema import ResponseModel, response_base

router = APIRouter()


@router.post('/providers/{user_uuid}', summary='添加LLM提供商')
async def add_llm_providers(user_uuid: str) -> ResponseModel:
    """添加LLM提供商"""
    try:
        await LlmCreateService.add_llm_providers(user_uuid)
        return response_base.success(data={'message': 'LLM providers added successfully.'})
    except Exception as e:
        return response_base.fail(data=str(e))
