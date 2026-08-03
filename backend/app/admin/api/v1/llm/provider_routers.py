from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from backend.app.admin.schema import (
    CreateLlmProviderParam,
    LlmProviderDetailSchema,
    LlmProviderListSchema,
    ReorderLlmProviderParam,
    UpdateLlmProviderParam,
)
from backend.app.admin.service.llm_provider_service import LlmProviderService
from backend.common.exception.errors import NotFoundError, RequestError
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.get('/all', summary='查看所有提供商', dependencies=[DependsJwtAuth])
async def get_all_providers(
    request: Request,
    name: Annotated[str | None, Query(description='提供商名称模糊搜索')] = None,
) -> ResponseModel:
    providers = await LlmProviderService.get_all(user_uuid=request.user.uuid, name=name)
    data = [LlmProviderListSchema(**select_as_dict(provider)) for provider in providers]
    return response_base.success(data=data)


@router.post('', summary='添加提供商', dependencies=[DependsJwtAuth])
async def create_provider(request: Request, obj: CreateLlmProviderParam) -> ResponseModel:
    obj.user_uuid = request.user.uuid
    try:
        new_provider = await LlmProviderService.add(obj=obj)
    except ValueError as exc:
        raise RequestError(msg='提供商配置无效或名称已存在') from exc
    data = LlmProviderListSchema(**select_as_dict(new_provider))
    return response_base.success(data=data)


@router.put('/order', summary='调整模型顺序', dependencies=[DependsJwtAuth])
async def reorder_providers(request: Request, obj: ReorderLlmProviderParam) -> ResponseModel:
    try:
        await LlmProviderService.reorder(provider_uuids=obj.provider_uuids, user_uuid=request.user.uuid)
    except ValueError as exc:
        raise RequestError(msg=str(exc)) from exc
    return response_base.success(data='模型顺序已更新')


@router.get('/{llm_provider_uuid}/detail', summary='获取提供商详细信息', dependencies=[DependsJwtAuth])
async def get_provider(
    request: Request, llm_provider_uuid: Annotated[str, Path(..., description='提供商UUID')]
) -> ResponseModel:
    provider = await LlmProviderService.get_detail(llm_provider_uuid, request.user.uuid)
    if provider is None:
        raise NotFoundError(msg='模型提供商不存在')
    data = LlmProviderDetailSchema(**select_as_dict(provider))
    return response_base.success(data=data)


@router.delete('', summary='删除提供商', dependencies=[DependsJwtAuth])
async def delete_provider(
    request: Request, llm_provider_uuid: Annotated[str, Query(description='提供商UUID')]
) -> ResponseModel:
    if not await LlmProviderService.delete(llm_provider_uuid=llm_provider_uuid, user_uuid=request.user.uuid):
        raise NotFoundError(msg='模型提供商不存在')
    return response_base.success(data='提供商删除成功')


@router.put('/{llm_provider_uuid}', summary='更新提供商', dependencies=[DependsJwtAuth])
async def update_providers(
    request: Request,
    llm_provider_uuid: Annotated[str, Path(description='要更新的提供商UUID')],
    obj: UpdateLlmProviderParam,
) -> ResponseModel:
    try:
        updated_provider = await LlmProviderService.update(
            llm_provider_uuid=llm_provider_uuid,
            obj=obj,
            user_uuid=request.user.uuid,
        )
    except ValueError as exc:
        raise NotFoundError(msg='模型提供商不存在') from exc
    if updated_provider is None:
        raise NotFoundError(msg='模型提供商不存在')
    data = LlmProviderListSchema(**select_as_dict(updated_provider))
    return response_base.success(data=data)
