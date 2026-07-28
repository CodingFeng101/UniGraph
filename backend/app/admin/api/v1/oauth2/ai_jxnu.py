#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import json
from typing import Optional

import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from fastapi import APIRouter, HTTPException

from backend.app.admin.service.wx_oauth2_service import wx_oauth2_service
from backend.common.exception.errors import RequestError
from backend.common.schema import SchemaBase
from backend.core.conf import settings

router = APIRouter()


class JxnuLoginRequest(SchemaBase):
    token: str  # Encrypted token from frontend
    iv: str  # Initialization vector for decryption


def decrypt_token(encrypted_token: str, iv: str) -> Optional[str]:
    """
    Decrypt the token using AES-CBC with the provided IV
    Args:
        encrypted_token: Base64 encoded encrypted token
        iv: Hex encoded initialization vector
    Returns:
        Decrypted token string or None if decryption fails
    """
    try:
        # Prepare the key and IV
        if not settings.JXNU_AES_SECRET_KEY:
            return None

        key = base64.b64decode(settings.JXNU_AES_SECRET_KEY, validate=True)
        iv_bytes = bytes.fromhex(iv)
        if len(iv_bytes) != AES.block_size:
            return None

        # Decode the encrypted token
        encrypted_bytes = base64.b64decode(encrypted_token)

        # Create cipher and decrypt
        cipher = AES.new(key, AES.MODE_CBC, iv_bytes)
        decrypted = cipher.decrypt(encrypted_bytes)

        # Remove padding and decode to string
        unpadded = unpad(decrypted, AES.block_size)
        return unpadded.decode('utf-8')
    except (ValueError, UnicodeDecodeError):
        return None


@router.post(
    '/jxnu-auth', summary='江西师大AI门户一键登录', response_description='授权成功返回用户凭证', dependencies=[]
)
async def ai_jxnu_login(obj: JxnuLoginRequest):
    """
    江西师大AI门户登录流程：
    1. 用密钥将token解密
    2. 用临时token换取 user_uuid
    3. 后续应创建自己的用户会话（示例仅返回江西师大AI门户数据）
    """
    if not settings.JXNU_AES_SECRET_KEY:
        raise HTTPException(status_code=503, detail='JXNU login is not configured')

    # Step 1: Decrypt the token
    decrypted_token = decrypt_token(obj.token, obj.iv)
    if not decrypted_token:
        raise HTTPException(status_code=400, detail='Token解密失败，请检查参数')

    wx_api_url = 'https://ai.jxselab.com/tsp/v1/sys/users/me'

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                wx_api_url,
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'AI-Portal-Auth/1.0',
                    'Authorization': f'Bearer {decrypted_token}',
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail=f'江西师大AI门户接口异常: HTTP {response.status_code}'
                )

            jxnu_data = response.json()

            if not isinstance(jxnu_data, dict):
                raise RequestError(msg='江西师大AI门户返回数据格式异常')

            user_uuid = jxnu_data['data'].get('username')
            if not user_uuid or not isinstance(user_uuid, str):
                raise RequestError(msg='无效的用户标识')

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail='江西师大AI门户接口请求超时')
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f'江西师大AI门户接口网络错误: {str(e)}')
    except json.JSONDecodeError:
        raise RequestError(msg='江西师大AI门户返回数据解析失败')

    try:
        data = await wx_oauth2_service.create_with_login(user_uuid=user_uuid)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'用户会话创建失败: {str(e)}')
