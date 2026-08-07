#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.app.kgbase.schema.schema_relationship import (
    AddSchemaRelationshipParam,
    SchemaRelationshipResponse,
    UpdateSchemaRelationshipParam,
)
from backend.app.kgbase.service.ownership_service import ownership_service
from backend.app.kgbase.service.schema_relationship_service import schema_relationship_service
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.database.db_mysql import CurrentSession
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.get('/all/{schema_graph_uuid}', summary='获取关系类型下所有实体', dependencies=[DependsJwtAuth])
async def get_all_schema_relationships(request: Request, schema_graph_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_schema_graph(user_uuid=request.user.uuid, uuid=schema_graph_uuid)
    schema_relationships = await schema_relationship_service.get_all(schema_graph_uuid=schema_graph_uuid)
    data = [
        SchemaRelationshipResponse(**select_as_dict(schema_relationship))
        for schema_relationship in schema_relationships
    ]
    return response_base.success(data=data)


@router.get('/{uuid}', summary='获取关系类型详情', dependencies=[DependsJwtAuth])
async def get_schema_relationship(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_schema_relationship(user_uuid=request.user.uuid, uuid=uuid)
    schema_relationship = await schema_relationship_service.get_schema_relationship(uuid=uuid)
    data = SchemaRelationshipResponse(**select_as_dict(schema_relationship))
    return response_base.success(data=data)


@router.get(
    '',
    summary='（模糊条件）分页获取所有关系类型',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_schema_relationships(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseModel:
    schema_relationship_select = await schema_relationship_service.get_select(
        user_uuid=request.user.uuid, name=name, status=status
    )
    page_data = await paging_data(db, schema_relationship_select, SchemaRelationshipResponse)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建关系类型',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:schema_relationship:add'))],
)
async def create_schema_relationship(request: Request, obj: AddSchemaRelationshipParam) -> ResponseModel:
    await ownership_service.require_schema_entity_in_graph(
        user_uuid=request.user.uuid,
        entity_uuid=obj.source_entity_uuid,
        schema_graph_uuid=obj.schema_graph_uuid,
    )
    await ownership_service.require_schema_entity_in_graph(
        user_uuid=request.user.uuid,
        entity_uuid=obj.target_entity_uuid,
        schema_graph_uuid=obj.schema_graph_uuid,
    )
    await schema_relationship_service.add(obj=obj)
    return response_base.success()


@router.put(
    '/{uuid}',
    summary='更新关系类型',
    dependencies=[Depends(RequestPermission('sys:schema_relationship:edit'))],
)
async def update_schema_relationship(
    request: Request, uuid: Annotated[str, Path(...)], obj: UpdateSchemaRelationshipParam
) -> ResponseModel:
    await ownership_service.require_schema_relationship(user_uuid=request.user.uuid, uuid=uuid)
    count = await schema_relationship_service.update(uuid=uuid, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{uuid}',
    summary='（批量）删除关系类型',
    dependencies=[Depends(RequestPermission('sys:schema_relationship:del'))],
)
async def delete_schema_relationship(request: Request, uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await ownership_service.require_schema_relationship(user_uuid=request.user.uuid, uuid=uuid)
    count = await schema_relationship_service.delete(uuid=uuid)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/status',
    summary='更新关系类型状态',
    dependencies=[Depends(RequestPermission('sys:schema_relationship:status'))],
)
async def update_schema_relationship_status(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    await ownership_service.require_schema_relationship(user_uuid=request.user.uuid, pk=pk)
    count = await schema_relationship_service.update_status(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
