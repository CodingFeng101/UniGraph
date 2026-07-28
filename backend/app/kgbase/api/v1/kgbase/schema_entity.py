#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.app.kgbase.schema.schema_entity import AddSchemaEntityParam, SchemaEntityResponse, UpdateSchemaEntityParam
from backend.app.kgbase.schema.schema_graph import UpdateSchemaGraphBase
from backend.app.kgbase.service.schema_entity_service import schema_entity_service
from backend.app.kgbase.service.schema_graph_service import schema_graph_service
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.database.db_mysql import CurrentSession
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.get('/all/{schema_graph_uuid}', summary='获取架构下所有实体类型', dependencies=[DependsJwtAuth])
async def get_all_schema_entities(schema_graph_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    schema_entities = await schema_entity_service.get_all(schema_graph_uuid=schema_graph_uuid)
    data = [SchemaEntityResponse(**select_as_dict(schema_entity)) for schema_entity in schema_entities]
    return response_base.success(data=data)


@router.get('/{uuid}', summary='获取实体类型详情', dependencies=[DependsJwtAuth])
async def get_schema_entity(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    schema_entity = await schema_entity_service.get_schema_entity(uuid=uuid)
    data = SchemaEntityResponse(**select_as_dict(schema_entity))
    return response_base.success(data=data)


@router.get(
    '',
    summary='（模糊条件）分页获取所有实体类型',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_schema_entities(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseModel:
    schema_entity_select = await schema_entity_service.get_select(user_uuid=request.user.uuid, name=name, status=status)
    page_data = await paging_data(db, schema_entity_select, SchemaEntityResponse)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建实体类型',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:schema_entity:add'))],
)
async def create_schema_entity(obj: AddSchemaEntityParam) -> ResponseModel:
    await schema_entity_service.add(obj=obj)
    schema_graph = await schema_graph_service.get_schema_graph(uuid=obj.schema_graph_uuid)

    modify_info = {}
    if schema_graph.modify_info:
        modify_info = json.loads(schema_graph.modify_info)

    add_entity = modify_info.get('add_entity', [])
    add_entity.append(obj.name)

    modify_info['add_entity'] = add_entity
    await schema_graph_service.update(
        uuid=schema_graph.uuid, obj=UpdateSchemaGraphBase(modify_info=json.dumps(modify_info))
    )
    return response_base.success()


@router.put(
    '/{uuid}',
    summary='更新实体类型',
    dependencies=[Depends(RequestPermission('sys:schema_entity:edit'))],
)
async def update_schema_entity(uuid: Annotated[str, Path(...)], obj: UpdateSchemaEntityParam) -> ResponseModel:
    count = await schema_entity_service.update(uuid=uuid, obj=obj)

    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{uuid}',
    summary='删除实体类型',
    dependencies=[
        Depends(RequestPermission('sys:schema_entity:del')),
    ],
)
async def delete_schema_entity(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    schema_entity = await schema_entity_service.get_schema_entity(uuid=uuid)
    schema_graph = await schema_graph_service.get_schema_graph(uuid=schema_entity.schema_graph_uuid)

    modify_info = {}
    if schema_graph.modify_info:
        modify_info = json.loads(schema_graph.modify_info)

    del_entity = modify_info.get('del_entity', [])
    del_entity.append(schema_entity.name)

    modify_info['del_entity'] = del_entity
    await schema_graph_service.update(
        uuid=schema_graph.uuid, obj=UpdateSchemaGraphBase(modify_info=json.dumps(modify_info))
    )
    count = await schema_entity_service.delete(uuid=uuid)
    if count > 0:
        return response_base.success()

    return response_base.fail()


@router.put(
    '/{pk}/status',
    summary='更新实体类型状态',
    dependencies=[Depends(RequestPermission('sys:schema_entity:status'))],
)
async def update_schema_entity_status(pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await schema_entity_service.update_status(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
