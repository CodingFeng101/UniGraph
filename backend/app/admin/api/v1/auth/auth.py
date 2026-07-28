#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPBasicCredentials
from starlette.background import BackgroundTasks

from backend.app.admin.schema.token import GetSwaggerToken
from backend.app.admin.schema.user import AuthLoginParam, AuthRegisterParam, AuthResetPasswordParam
from backend.app.admin.service.auth_service import auth_service
from backend.app.admin.service.llm_create_service import llm_create_service
from backend.app.admin.service.user_service import user_service
from backend.common.rate_limit import rate_limiter
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth

router = APIRouter()


@router.post('/login/swagger', summary='swagger 调试专用', description='用于快捷获取 token 进行 swagger 认证')
async def swagger_login(obj: Annotated[HTTPBasicCredentials, Depends()]) -> GetSwaggerToken:
    token, user = await auth_service.swagger_login(obj=obj)
    return GetSwaggerToken(access_token=token, user=user)  # type: ignore


@router.post(
    '/login',
    summary='用户登录',
    description='json 格式登录, 仅支持在第三方api工具调试, 例如: postman',
    dependencies=[Depends(rate_limiter(times=5, seconds=60))],
)
async def user_login(
    request: Request, response: Response, obj: AuthLoginParam, background_tasks: BackgroundTasks
) -> ResponseModel:
    data = await auth_service.login(request=request, response=response, obj=obj, background_tasks=background_tasks)
    return response_base.success(data=data)


@router.post('/register', summary='注册用户', dependencies=[Depends(rate_limiter(times=5, seconds=60))])
async def user_register(request: Request, obj: AuthRegisterParam) -> ResponseModel:
    await auth_service.register(request=request, obj=obj)
    user = await user_service.get_userinfo(username=obj.username)
    await llm_create_service.add_llm_providers(user.uuid)
    return response_base.success(data='注册成功')


@router.put('/password/reset', summary='密码重置', dependencies=[Depends(rate_limiter(times=5, seconds=60))])
async def forgetPassword(request: Request, obj: AuthResetPasswordParam) -> ResponseModel:
    await auth_service.pwd_reset(request=request, obj=obj)
    return response_base.success(data='密码重置成功')


@router.post('/token/new', summary='创建新 token', dependencies=[DependsJwtAuth])
async def create_new_token(request: Request, response: Response) -> ResponseModel:
    data = await auth_service.new_token(request=request, response=response)
    return response_base.success(data=data)


@router.post('/logout', summary='用户登出', dependencies=[DependsJwtAuth])
async def user_logout(request: Request, response: Response) -> ResponseModel:
    await auth_service.logout(request=request, response=response)
    return response_base.success()
