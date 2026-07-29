#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, Response

from backend.app.kgbase.schema.chat_library import (
    AppendMessageParam,
    AppendTurnParam,
    ChatShareResponse,
    CreateLibraryParam,
    FavoriteParam,
    GenerateTitleParam,
    LibraryResponse,
    PublicChatShareResponse,
    UpdateLibraryParam,
    UpdateMessageParam,
)
from backend.app.kgbase.service.chat_library_service import chat_library_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.get('/public/{public_id}', summary='查看公开的对话快照')
async def get_public_share(
    response: Response,
    public_id: Annotated[str, Path(...)],
) -> ResponseModel:
    # Shared conversations can contain user-authored or confidential material.
    # Browsers/proxies must not retain them and search engines must not index them.
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive'
    data = await chat_library_service.get_public_share(public_id=public_id)
    return response_base.success(data=PublicChatShareResponse(**data))


@router.get('/{chat_library_uuid}/share', summary='获取当前对话的分享状态', dependencies=[DependsJwtAuth])
async def get_share(request: Request, chat_library_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    data = await chat_library_service.get_share(
        chat_library_uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
    )
    return response_base.success(data=data)


@router.post('/{chat_library_uuid}/share', summary='创建只读对话快照', dependencies=[DependsJwtAuth])
async def create_share(request: Request, chat_library_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    data = await chat_library_service.create_share(
        chat_library_uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
    )
    return response_base.success(data=ChatShareResponse(**data))


@router.put('/{chat_library_uuid}/share', summary='更新只读对话快照', dependencies=[DependsJwtAuth])
async def update_share(request: Request, chat_library_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    data = await chat_library_service.update_share(
        chat_library_uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
    )
    return response_base.success(data=ChatShareResponse(**data))


@router.post(
    '/{chat_library_uuid}/share/rotate',
    summary='重新生成只读分享链接',
    dependencies=[DependsJwtAuth],
)
async def rotate_share(request: Request, chat_library_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    data = await chat_library_service.rotate_share(
        chat_library_uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
    )
    return response_base.success(data=ChatShareResponse(**data))


@router.delete('/{chat_library_uuid}/share', summary='停止分享对话', dependencies=[DependsJwtAuth])
async def revoke_share(request: Request, chat_library_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    await chat_library_service.revoke_share(
        chat_library_uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
    )
    return response_base.success()


@router.get('/all/{kg_base_uuid}', summary='获取所有聊天库', dependencies=[DependsJwtAuth])
async def get_all_library(request: Request, kg_base_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    libraries = await chat_library_service.get_all(
        kg_base_uuid=kg_base_uuid,
        user_uuid=request.user.uuid,
    )
    data = [LibraryResponse(**select_as_dict(library)) for library in libraries]
    return response_base.success(data=data)


@router.get('/{chat_library_uuid}', summary='获取聊天库具体信息', dependencies=[DependsJwtAuth])
async def get_library(request: Request, chat_library_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    data = await chat_library_service.get_conversation(
        uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
    )
    return response_base.success(data=data)


@router.post('/{chat_library_uuid}/turn', summary='保存一轮对话及四类信息源', dependencies=[DependsJwtAuth])
async def append_turn(
    request: Request,
    chat_library_uuid: Annotated[str, Path(...)],
    obj: AppendTurnParam,
) -> ResponseModel:
    data = await chat_library_service.append_turn(
        uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
        obj=obj,
    )
    return response_base.success(data=data)


@router.post('/{chat_library_uuid}/message', summary='Save one chat message', dependencies=[DependsJwtAuth])
async def append_message(
    request: Request,
    chat_library_uuid: Annotated[str, Path(...)],
    obj: AppendMessageParam,
) -> ResponseModel:
    data = await chat_library_service.append_message(
        uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
        obj=obj,
    )
    return response_base.success(data=data)


@router.patch(
    '/{chat_library_uuid}/message/{message_uuid}',
    summary='Edit one user message',
    dependencies=[DependsJwtAuth],
)
async def update_message(
    request: Request,
    chat_library_uuid: Annotated[str, Path(...)],
    message_uuid: Annotated[str, Path(...)],
    obj: UpdateMessageParam,
) -> ResponseModel:
    data = await chat_library_service.update_message(
        uuid=chat_library_uuid,
        message_uuid=message_uuid,
        user_uuid=request.user.uuid,
        content=obj.content,
    )
    return response_base.success(data=data)


@router.post(
    '/{chat_library_uuid}/title', summary='Generate a title from the first message', dependencies=[DependsJwtAuth]
)
async def generate_title(
    request: Request,
    chat_library_uuid: Annotated[str, Path(...)],
    obj: GenerateTitleParam,
) -> ResponseModel:
    token = request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
    title = await chat_library_service.generate_title(
        uuid=chat_library_uuid,
        content=obj.content,
        user_token=token,
        user_uuid=request.user.uuid,
    )
    return response_base.success(data=title)


@router.patch('/{chat_library_uuid}/favorite', summary='收藏或取消收藏对话', dependencies=[DependsJwtAuth])
async def set_favorite(
    request: Request,
    chat_library_uuid: Annotated[str, Path(...)],
    obj: FavoriteParam,
) -> ResponseModel:
    await chat_library_service.set_favorite(
        uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
        is_favorite=obj.is_favorite,
    )
    return response_base.success()


@router.post(
    '',
    summary='创建聊天库',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:chat_library:add'))],
)
async def create_library(request: Request, obj: CreateLibraryParam) -> ResponseModel:
    chat_library_uuid = await chat_library_service.add(obj=obj, user_uuid=request.user.uuid)
    return response_base.success(data=chat_library_uuid)


@router.put(
    '/{chat_library_uuid}',
    summary='编辑聊天库',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:chat_library:update'))],
)
async def update_library(
    request: Request,
    chat_library_uuid: Annotated[str, Path(...)],
    obj: UpdateLibraryParam,
) -> ResponseModel:
    count = await chat_library_service.update(
        uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
        obj=obj,
    )
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{chat_library_uuid}',
    summary='删除聊天库',
    dependencies=[DependsJwtAuth, Depends(RequestPermission('sys:chat_library:del'))],
)
async def delete_library(request: Request, chat_library_uuid: Annotated[str, Path(...)]) -> ResponseModel:
    count = await chat_library_service.delete(
        uuid=chat_library_uuid,
        user_uuid=request.user.uuid,
    )
    if count > 0:
        return response_base.success()

    return response_base.fail()
