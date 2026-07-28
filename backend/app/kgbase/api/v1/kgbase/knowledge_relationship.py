#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.app.kgbase.schema.knowledge_relationship import (
    AddKnowledgeRelationshipParam,
    KnowledgeRelationshipResponse,
    UpdateKnowledgeRelationshipParam,
)
from backend.app.kgbase.service.knowledge_relationship_service import knowledge_relationship_service
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.database.db_mysql import CurrentSession
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.get('/all/{knowledge_graph_uuid}', summary='获取关系类型下所有实体', dependencies=[DependsJwtAuth])
async def get_all_knowledge_relationships(knowledge_graph_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    knowledge_relationships = await knowledge_relationship_service.get_all(knowledge_graph_uuid=knowledge_graph_uuid)
    data = [
        KnowledgeRelationshipResponse(**select_as_dict(knowledge_relationship))
        for knowledge_relationship in knowledge_relationships
    ]
    return response_base.success(data=data)


@router.get('/{uuid}', summary='获取关系类型详情', dependencies=[DependsJwtAuth])
async def get_knowledge_relationship(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    knowledge_relationship = await knowledge_relationship_service.get_knowledge_relationship(uuid=uuid)
    data = KnowledgeRelationshipResponse(**select_as_dict(knowledge_relationship))
    return response_base.success(data=data)


@router.get(
    '',
    summary='（模糊条件）分页获取所有关系',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_knowledge_relationships(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseModel:
    knowledge_relationship_select = await knowledge_relationship_service.get_select(
        user_uuid=request.user.uuid, name=name, status=status
    )
    page_data = await paging_data(db, knowledge_relationship_select, KnowledgeRelationshipResponse)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建关系',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:knowledge_relationship:add'))],
)
async def create_knowledge_relationship(request: Request, obj: AddKnowledgeRelationshipParam) -> ResponseModel:
    await knowledge_relationship_service.add(obj=obj)
    return response_base.success()


@router.put(
    '/{uuid}',
    summary='更新关系',
    dependencies=[Depends(RequestPermission('sys:knowledge_relationship:edit'))],
)
async def update_knowledge_relationship(
    uuid: Annotated[str, Path(...)], obj: UpdateKnowledgeRelationshipParam
) -> ResponseModel:
    count = await knowledge_relationship_service.update(uuid=uuid, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{uuid}',
    summary='（批量）删除关系',
    dependencies=[Depends(RequestPermission('sys:knowledge_relationship:del'))],
)
async def delete_knowledge_relationship(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    count = await knowledge_relationship_service.delete(uuid=uuid)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/status',
    summary='更新关系状态',
    dependencies=[Depends(RequestPermission('sys:knowledge_relationship:status'))],
)
async def update_knowledge_relationship_status(pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await knowledge_relationship_service.update_status(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
