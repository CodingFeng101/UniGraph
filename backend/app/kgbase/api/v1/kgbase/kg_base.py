#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.app.kgbase.schema.kg_base import AddKgBaseParam, GetKgBaseDetail, KgBaseResponse, UpdateKgBaseParam
from backend.app.kgbase.service.kg_base_service import kg_base_service
from backend.app.kgbase.service.ownership_service import ownership_service
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.database.db_mysql import CurrentSession
from backend.utils.serializers import select_as_dict

router = APIRouter()


# ===========================CRUD类型，
@router.get('/all/', summary='获取所有图谱库', dependencies=[DependsJwtAuth])
async def get_all_kg_bases(request: Request) -> ResponseModel:
    kg_bases = await kg_base_service.get_all(user_uuid=request.user.uuid)
    data = [KgBaseResponse(**select_as_dict(kg_base)) for kg_base in kg_bases]
    return response_base.success(data=data)


@router.get('/{uuid}', summary='获取图谱库详情', dependencies=[DependsJwtAuth])
async def get_kg_base(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_kg_base(user_uuid=request.user.uuid, uuid=uuid)
    kg_base = await kg_base_service.get_kg_base(uuid=uuid)
    data = GetKgBaseDetail(**select_as_dict(kg_base))
    return response_base.success(data=data)


@router.get(
    '',
    summary='（模糊条件）分页获取所有图谱库',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_kg_bases(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseModel:
    kg_base_select = await kg_base_service.get_select(user_uuid=request.user.uuid, name=name, status=status)
    page_data = await paging_data(db, kg_base_select, KgBaseResponse)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建图谱库',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:kg_base:add'))],
)
async def create_kg_base(request: Request, obj: AddKgBaseParam) -> ResponseModel:
    user_uuid = request.user.uuid
    obj.user_uuid = user_uuid
    await kg_base_service.add(obj=obj)
    return response_base.success()


@router.put(
    '/{uuid}',
    summary='更新图谱库',
    dependencies=[Depends(RequestPermission('sys:kg_base:edit'))],
)
async def update_kg_base(request: Request, uuid: Annotated[str, Path(...)], obj: UpdateKgBaseParam) -> ResponseModel:
    await ownership_service.require_kg_base(user_uuid=request.user.uuid, uuid=uuid)
    count = await kg_base_service.update(uuid=uuid, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{uuid}',
    summary='（批量）删除图谱库',
    dependencies=[Depends(RequestPermission('sys:kg_base:del'))],
)
async def delete_kg_base(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_kg_base(user_uuid=request.user.uuid, uuid=uuid)
    count = await kg_base_service.delete(uuid=uuid)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/status',
    summary='更新图谱库状态',
    dependencies=[Depends(RequestPermission('sys:kg_base:status'))],
)
async def update_kg_base_status(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    await ownership_service.require_kg_base(user_uuid=request.user.uuid, pk=pk)
    count = await kg_base_service.update_status(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
