#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.app.kgbase.schema import GetKnowledgeEntityDetail
from backend.app.kgbase.schema.knowledge_entity import (
    AddKnowledgeEntityParam,
    KnowledgeEntityResponse,
    UpdateKnowledgeEntityParam,
)
from backend.app.kgbase.service.knowledge_entity_service import knowledge_entity_service
from backend.app.kgbase.service.ownership_service import ownership_service
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.database.db_mysql import CurrentSession
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.get('/all/{knowledge_graph_uuid}', summary='获取实体类型下所有实体', dependencies=[DependsJwtAuth])
async def get_all_knowledge_entities(
    request: Request, knowledge_graph_uuid: Annotated[str, Path(...)]
) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=knowledge_graph_uuid)
    knowledge_entities = await knowledge_entity_service.get_all(knowledge_graph_uuid=knowledge_graph_uuid)
    data = [KnowledgeEntityResponse(**select_as_dict(knowledge_entity)) for knowledge_entity in knowledge_entities]
    return response_base.success(data=data)


@router.get('/{uuid}', summary='获取实体详情', dependencies=[DependsJwtAuth])
async def get_knowledge_entity(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_knowledge_entity(user_uuid=request.user.uuid, uuid=uuid)
    knowledge_entity = await knowledge_entity_service.get_knowledge_entity(uuid=uuid)
    data = GetKnowledgeEntityDetail(**select_as_dict(knowledge_entity))
    return response_base.success(data=data)


@router.get(
    '',
    summary='（模糊条件）分页获取所有实体',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_knowledge_entities(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseModel:
    knowledge_entity_select = await knowledge_entity_service.get_select(
        user_uuid=request.user.uuid, name=name, status=status
    )
    page_data = await paging_data(db, knowledge_entity_select, KnowledgeEntityResponse)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建实体',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:knowledge_entity:add'))],
)
async def create_knowledge_entity(request: Request, obj: AddKnowledgeEntityParam) -> ResponseModel:
    await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=obj.knowledge_graph_uuid)
    await knowledge_entity_service.add(obj=obj)
    return response_base.success()


@router.put(
    '/{uuid}',
    summary='更新实体',
    dependencies=[Depends(RequestPermission('sys:knowledge_entity:edit'))],
)
async def update_knowledge_entity(
    request: Request, uuid: Annotated[str, Path(...)], obj: UpdateKnowledgeEntityParam
) -> ResponseModel:
    await ownership_service.require_knowledge_entity(user_uuid=request.user.uuid, uuid=uuid)
    count = await knowledge_entity_service.update(uuid=uuid, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{uuid}',
    summary='删除实体',
    dependencies=[Depends(RequestPermission('sys:knowledge_entity:del'))],
)
async def delete_knowledge_entity(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_knowledge_entity(user_uuid=request.user.uuid, uuid=uuid)
    count = await knowledge_entity_service.delete(uuid=uuid)
    if count > 0:
        return response_base.success()

    return response_base.fail()


@router.put(
    '/{pk}/status',
    summary='更新实体状态',
    dependencies=[Depends(RequestPermission('sys:knowledge_entity:status'))],
)
async def update_knowledge_entity_status(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    await ownership_service.require_knowledge_entity(user_uuid=request.user.uuid, pk=pk)
    count = await knowledge_entity_service.update_status(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
