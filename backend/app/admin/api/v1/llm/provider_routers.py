from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Request

from backend.app.admin.schema import (
    CreateLlmProviderParam,
    LlmProviderDetailSchema,
    LlmProviderListSchema,
    UpdateLlmProviderParam,
)
from backend.app.admin.service.llm_provider_service import LlmProviderService
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.get('/all', summary='查看所有提供商', dependencies=[DependsJwtAuth])
async def get_all_providers(
    request: Request,
    name: Annotated[str | None, Query(description='提供商名称模糊搜索')] = None,
) -> ResponseModel:
    """获取所有提供商（支持条件筛选）"""
    try:
        providers = await LlmProviderService.get_all(user_uuid=request.user.uuid, name=name)
        data = [LlmProviderListSchema(**select_as_dict(provider)) for provider in providers]
        return response_base.success(data=data)
    except Exception as e:
        return response_base.fail(data=str(e))


@router.post('', summary='添加提供商', dependencies=[DependsJwtAuth])
async def create_provider(request: Request, obj: CreateLlmProviderParam) -> ResponseModel:
    """创建新提供商"""
    try:
        obj.user_uuid = request.user.uuid
        new_provider = await LlmProviderService.add(obj=obj)
        data = LlmProviderListSchema(**select_as_dict(new_provider))
        return response_base.success(data=data)
    except ValueError as e:
        return response_base.fail(data=str(e))
    except Exception as e:
        return response_base.fail(data=f'创建失败: {str(e)}')


@router.get('/{llm_provider_uuid}/detail', summary='获取提供商详细信息', dependencies=[DependsJwtAuth])
async def get_provider(
    request: Request, llm_provider_uuid: Annotated[str, Path(..., description='提供商UUID')]
) -> ResponseModel:
    """获取提供商详情（包含关联模型）"""
    try:
        provider = await LlmProviderService.get_detail(llm_provider_uuid)
        data = LlmProviderDetailSchema(**select_as_dict(provider))
        return response_base.success(data=data)
    except HTTPException as e:
        return response_base.fail(data=e.detail)
    except Exception as e:
        return response_base.fail(data=str(e))


@router.delete('', summary='删除提供商', dependencies=[DependsJwtAuth])
async def delete_provider(
    request: Request, llm_provider_uuid: Annotated[str, Query(description='提供商UUID')]
) -> ResponseModel:
    """删除指定提供商"""
    try:
        success = await LlmProviderService.delete(llm_provider_uuid=llm_provider_uuid)
        if success:
            return response_base.success(data='提供商删除成功')
        return response_base.fail()
    except HTTPException as e:
        return response_base.fail(data=e.detail)
    except Exception as e:
        return response_base.fail(data=f'删除失败: {str(e)}')


@router.put('/{llm_provider_uuid}', summary='更新提供商', dependencies=[DependsJwtAuth])
async def update_providers(
    request: Request,
    llm_provider_uuid: Annotated[str, Path(description='要更新的提供商UUID')],
    obj: UpdateLlmProviderParam,
) -> ResponseModel:
    """更新提供商信息"""
    try:
        updated_provider = await LlmProviderService.update(llm_provider_uuid=llm_provider_uuid, obj=obj)
        data = LlmProviderListSchema(**select_as_dict(updated_provider))
        return response_base.success(data=data)
    except ValueError as e:
        return response_base.fail(data=str(e))
    except Exception as e:
        return response_base.fail(data=f'更新失败: {str(e)}')
