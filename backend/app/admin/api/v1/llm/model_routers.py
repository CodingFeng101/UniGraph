from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, Path, Query, Request

from backend.app.admin.schema import CreateLlmModelParam, LlmModelListSchema, UpdateLlmModelParam
from backend.app.admin.service.llm_create_service import LlmCreateService
from backend.app.admin.service.llm_model_service import LlmModelService
from backend.common.exception.errors import NotFoundError, RequestError
from backend.common.rate_limit import rate_limiter
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.get('/all', summary='查看所有模型', dependencies=[DependsJwtAuth])
async def get_all_model(
    request: Request,
    llm_provider_uuid: Annotated[str | None, Query(description='提供商UUID检索')] = None,
) -> ResponseModel:
    models = await LlmModelService.get_all(
        llm_provider_uuid=llm_provider_uuid,
        user_uuid=request.user.uuid,
    )
    data = [LlmModelListSchema(**select_as_dict(model)) for model in models]
    return response_base.success(data=data)


@router.post(
    '/test',
    summary='测试api_key',
    dependencies=[DependsJwtAuth, Depends(rate_limiter(times=10, seconds=60))],
)
async def test_api_key(
    base_url: str = Body(..., description='API地址'),
    api_key: str = Body(..., description='API密钥'),
    model_name: str = Body(..., description='模型名称'),
    model_type: Literal['llm', 'embedding'] = Body('llm', description='模型类型'),
) -> ResponseModel:
    try:
        await LlmCreateService.test(base_url, api_key, model_name, model_type)
    except Exception as exc:
        raise RequestError(msg='模型连接测试失败，请检查地址、密钥和模型名称') from exc
    return response_base.success(data={'message': '模型连接测试成功'})


@router.post('', summary='添加模型', dependencies=[DependsJwtAuth])
async def create_llm_model(request: Request, obj: CreateLlmModelParam) -> ResponseModel:
    try:
        new_model = await LlmModelService.add(obj=obj, user_uuid=request.user.uuid)
    except ValueError as exc:
        raise RequestError(msg=str(exc)) from exc
    data = LlmModelListSchema(**select_as_dict(new_model))
    return response_base.success(data=data)


@router.get('/{llm_model_uuid}/detail', summary='获取模型详细信息', dependencies=[DependsJwtAuth])
async def get_llm_model(
    request: Request, llm_model_uuid: Annotated[str, Path(..., description='模型UUID')]
) -> ResponseModel:
    model = await LlmModelService.get_detail(llm_model_uuid, request.user.uuid)
    if model is None:
        raise NotFoundError(msg='模型不存在')
    data = LlmModelListSchema(**select_as_dict(model))
    return response_base.success(data=data)


@router.delete('', summary='删除模型', dependencies=[DependsJwtAuth])
async def delete_llm_model(
    request: Request, llm_model_uuid: Annotated[str, Query(description='模型UUID')]
) -> ResponseModel:
    if not await LlmModelService.delete(llm_model_uuid=llm_model_uuid, user_uuid=request.user.uuid):
        raise NotFoundError(msg='模型不存在')
    return response_base.success(data='模型删除成功')


@router.put('/{llm_model_uuid}', summary='更新模型', dependencies=[DependsJwtAuth])
async def update_llm_model(
    request: Request, llm_model_uuid: Annotated[str, Path(description='要更新的模型UUID')], obj: UpdateLlmModelParam
) -> ResponseModel:
    try:
        updated_model = await LlmModelService.update(
            llm_model_uuid=llm_model_uuid,
            obj=obj,
            user_uuid=request.user.uuid,
        )
    except ValueError as exc:
        if str(exc) == '每个用户只能配置一个嵌入模型':
            raise RequestError(msg=str(exc)) from exc
        raise NotFoundError(msg='模型不存在') from exc
    if updated_model is None:
        raise NotFoundError(msg='模型不存在')
    data = LlmModelListSchema(**select_as_dict(updated_model))
    return response_base.success(data=data)
