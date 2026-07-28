import xml.etree.ElementTree as ET
from typing import Annotated

import httpx
from fastapi import APIRouter, Path, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.background import BackgroundTasks

from backend.app.admin.schema.user import (
    AuthSSOLoginParam,
    GetUserInfoListDetails,
    SSORegisterUserParam,
)
from backend.app.admin.service.auth_service import auth_service
from backend.app.admin.service.llm_create_service import LlmCreateService
from backend.app.admin.service.user_service import user_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.utils.serializers import select_as_dict

# CAS 服务器和服务验证接口 URL
CAS_SERVER = 'https://uis.jxnu.edu.cn/cas'
SERVICE_URL = 'https://ai.jxnu.edu.cn/sso/login'  # 请替换成你的应用回调地址


class TicketRequest(BaseModel):
    ticket: str  # 定义 ticket 字段


router = APIRouter()


@router.post(
    '/ssologin',
    summary='sso用户登录',
)
async def user_sso_login(
    request: Request, response: Response, obj: AuthSSOLoginParam, background_tasks: BackgroundTasks
) -> ResponseModel:
    data = await auth_service.sso_login(request=request, response=response, obj=obj, background_tasks=background_tasks)
    return response_base.success(data=data)


@router.post('/sso/register', summary='sso注册用户')
async def user_sso_register(request: Request, obj: SSORegisterUserParam) -> ResponseModel:
    await auth_service.sso_register(request=request, obj=obj)
    user = await user_service.get_userinfo(username=obj.username)
    await LlmCreateService.add_llm_providers(user.uuid)
    return response_base.success(data='注册成功')


@router.get('/sso/{username}', summary='sso检查用户', dependencies=[])
async def get_sso_user(username: Annotated[str, Path(...)]) -> ResponseModel:
    current_user = await user_service.get_sso_userinfo(username=username)
    if current_user:
        data = GetUserInfoListDetails(**select_as_dict(current_user))
        return response_base.success(data=data)
    else:
        return response_base.success(data='注册')


@router.post('/checksso', summary='sso验证用户')
async def validate_ticket(ticket_request: TicketRequest):
    ticket = ticket_request.ticket
    validate_url = f'{CAS_SERVER}/serviceValidate'

    params = {'ticket': ticket, 'service': SERVICE_URL}

    async with httpx.AsyncClient() as client:
        response = await client.get(validate_url, params=params)

    if response.status_code != 200:
        print('Error: 无法验证票据，CAS 返回错误')
        return JSONResponse(status_code=400, content={'error': '无法验证票据'})

    try:
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()

        auth_success = root.find('.//{http://www.yale.edu/tp/cas}authenticationSuccess')

        if auth_success is not None:
            user_info = {}
            user_info['user'] = auth_success.find('.//{http://www.yale.edu/tp/cas}user').text

            attributes = auth_success.find('.//{http://www.yale.edu/tp/cas}attributes')

            if attributes is not None:
                user_info['accountName'] = (
                    attributes.find('.//{http://www.yale.edu/tp/cas}accountName').text
                    if attributes.find('.//{http://www.yale.edu/tp/cas}accountName') is not None
                    else None
                )
                user_info['identityTypeName'] = (
                    attributes.find('.//{http://www.yale.edu/tp/cas}identityTypeName').text
                    if attributes.find('.//{http://www.yale.edu/tp/cas}identityTypeName') is not None
                    else None
                )
                user_info['organizationId'] = (
                    attributes.find('.//{http://www.yale.edu/tp/cas}organizationId').text
                    if attributes.find('.//{http://www.yale.edu/tp/cas}organizationId') is not None
                    else None
                )
                user_info['organizationName'] = (
                    attributes.find('.//{http://www.yale.edu/tp/cas}organizationName').text
                    if attributes.find('.//{http://www.yale.edu/tp/cas}organizationName') is not None
                    else None
                )
                user_info['userName'] = (
                    attributes.find('.//{http://www.yale.edu/tp/cas}userName').text
                    if attributes.find('.//{http://www.yale.edu/tp/cas}userName') is not None
                    else None
                )
                user_info['userId'] = (
                    attributes.find('.//{http://www.yale.edu/tp/cas}userId').text
                    if attributes.find('.//{http://www.yale.edu/tp/cas}userId') is not None
                    else None
                )
                user_info['accountId'] = (
                    attributes.find('.//{http://www.yale.edu/tp/cas}accountId').text
                    if attributes.find('.//{http://www.yale.edu/tp/cas}accountId') is not None
                    else None
                )
                user_info['name'] = (
                    attributes.find('.//{http://www.yale.edu/tp/cas}name').text
                    if attributes.find('.//{http://www.yale.edu/tp/cas}name') is not None
                    else None
                )
                user_info['identityTypeId'] = (
                    attributes.find('.//{http://www.yale.edu/tp/cas}identityTypeId').text
                    if attributes.find('.//{http://www.yale.edu/tp/cas}identityTypeId') is not None
                    else None
                )

            return JSONResponse(status_code=200, content=user_info)  # 这里直接返回用户信息
        else:
            print('Error: 无法从 CAS 响应中提取用户信息')
            return JSONResponse(status_code=400, content={'error': '无法从 CAS 响应中提取用户信息'})
    except ET.ParseError:
        print('Error: 无法解析 CAS 响应 XML')
        return JSONResponse(status_code=400, content={'error': '无法解析 CAS 响应 XML'})
