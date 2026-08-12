#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import random
import secrets
import smtplib
from email.message import EmailMessage

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.exc import IntegrityError
from starlette.background import BackgroundTask, BackgroundTasks
from starlette.concurrency import run_in_threadpool

from backend.app.admin.conf import admin_settings
from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.model import User
from backend.app.admin.schema.token import GetLoginToken, GetNewToken
from backend.app.admin.schema.user import (
    AuthLoginParam,
    AuthPasswordResetCodeParam,
    AuthRegisterParam,
    AuthResetPasswordParam,
    RegisterUserParam,
)
from backend.app.admin.service.login_log_service import LoginLogService
from backend.common.enums import LoginLogStatusType
from backend.common.exception import errors
from backend.common.response.response_code import CustomErrorCode
from backend.common.security.jwt import (
    create_access_token,
    create_new_token,
    create_refresh_token,
    get_hash_password,
    get_token,
    jwt_decode,
    password_verify,
)
from backend.core.conf import settings
from backend.database.db_mysql import async_db_session
from backend.database.db_redis import redis_client
from backend.utils.timezone import timezone

# 设置密钥，前端和后端需要一致
try:
    SECRET_KEY = base64.b64decode(settings.AUTH_AES_SECRET_KEY, validate=True)
except ValueError as exc:
    raise RuntimeError('AUTH_AES_SECRET_KEY must be valid Base64') from exc
if len(SECRET_KEY) != 32:
    raise RuntimeError('AUTH_AES_SECRET_KEY must decode to exactly 32 bytes')

BLOCK_SIZE = AES.block_size


# 解密函数
# 解密函数
def decrypt_data(encrypted_data: str, iv_base64: str) -> str:
    try:
        # 解码 IV 和密文
        iv = base64.b64decode(iv_base64)
        ciphertext = base64.b64decode(encrypted_data)

        # 使用 AES 解密
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext), BLOCK_SIZE).decode('utf-8')

        return decrypted_data
    except Exception as exc:
        raise HTTPException(status_code=400, detail='Invalid encrypted request data') from exc


class AuthService:
    @staticmethod
    def _password_reset_key(email: str) -> str:
        email_hash = hashlib.sha256(email.casefold().encode('utf-8')).hexdigest()
        return f'{admin_settings.PASSWORD_RESET_CODE_REDIS_PREFIX}:{email_hash}'

    @staticmethod
    def _password_reset_cooldown_key(email: str) -> str:
        email_hash = hashlib.sha256(email.casefold().encode('utf-8')).hexdigest()
        return f'{admin_settings.PASSWORD_RESET_CODE_COOLDOWN_PREFIX}:{email_hash}'

    @staticmethod
    def _send_password_reset_email(*, recipient: str, code: str) -> None:
        message = EmailMessage()
        message['Subject'] = 'UniGraph 密码重置验证码'
        message['From'] = f'{admin_settings.MAIL_FROM_NAME} <{admin_settings.MAIL_USERNAME}>'
        message['To'] = recipient
        message.set_content(
            f'您好，您正在重置 UniGraph 账号密码。\n\n'
            f'您的验证码是：{code}\n'
            f'验证码 {admin_settings.PASSWORD_RESET_CODE_EXPIRE_SECONDS // 60} 分钟内有效。\n\n'
            '如果不是您本人操作，请忽略此邮件。'
        )
        if admin_settings.MAIL_USE_SSL:
            with smtplib.SMTP_SSL(admin_settings.MAIL_SERVER, admin_settings.MAIL_PORT, timeout=20) as server:
                server.login(admin_settings.MAIL_USERNAME, admin_settings.MAIL_PASSWORD)
                server.send_message(message)
        else:
            with smtplib.SMTP(admin_settings.MAIL_SERVER, admin_settings.MAIL_PORT, timeout=20) as server:
                server.starttls()
                server.login(admin_settings.MAIL_USERNAME, admin_settings.MAIL_PASSWORD)
                server.send_message(message)

    @staticmethod
    async def send_password_reset_code(*, request: Request, obj: AuthPasswordResetCodeParam) -> None:
        obj.username = decrypt_data(obj.username, obj.username_iv).strip()
        obj.email = decrypt_data(obj.email, obj.email_iv).strip().casefold()
        if not obj.username or not obj.email:
            raise errors.ForbiddenError(msg='请输入用户名和注册邮箱')
        if not admin_settings.MAIL_USERNAME or not admin_settings.MAIL_PASSWORD:
            raise errors.ServerError(msg='邮件服务尚未配置，请联系管理员')

        async with async_db_session() as db:
            user = await user_dao.get_by_username(db, obj.username)
        if not user or not user.email or user.email.casefold() != obj.email:
            # 对外保持统一响应，避免通过接口枚举系统账号和邮箱。
            return

        cooldown_key = AuthService._password_reset_cooldown_key(obj.email)
        cooldown_created = await redis_client.set(
            cooldown_key,
            '1',
            ex=admin_settings.PASSWORD_RESET_CODE_COOLDOWN_SECONDS,
            nx=True,
        )
        if not cooldown_created:
            raise errors.ForbiddenError(msg='验证码发送过于频繁，请稍后再试')

        code = f'{secrets.randbelow(900000) + 100000}'
        code_key = AuthService._password_reset_key(obj.email)
        await redis_client.set(code_key, code, ex=admin_settings.PASSWORD_RESET_CODE_EXPIRE_SECONDS)
        try:
            await run_in_threadpool(AuthService._send_password_reset_email, recipient=obj.email, code=code)
        except Exception as exc:
            await redis_client.delete(code_key, cooldown_key)
            raise errors.ServerError(msg='验证码邮件发送失败，请检查邮箱配置后重试') from exc

    @staticmethod
    async def swagger_login(*, obj: HTTPBasicCredentials) -> tuple[str, User]:
        async with async_db_session.begin() as db:
            current_user = await user_dao.get_by_username(db, obj.username)
            if not current_user:
                raise errors.NotFoundError(msg='账号或密码有误')
            elif not password_verify(f'{obj.password}{current_user.salt}', current_user.password):
                raise errors.AuthorizationError(msg='账号或密码有误')
            elif not current_user.status:
                raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')
            access_token = await create_access_token(str(current_user.id), current_user.is_multi_login)
            await user_dao.update_login_time(db, obj.username)
            return access_token.access_token, current_user

    @staticmethod
    async def login(
        *, request: Request, response: Response, obj: AuthLoginParam, background_tasks: BackgroundTasks
    ) -> GetLoginToken:
        async with async_db_session.begin() as db:
            user_uuid = None
            username = ''
            try:
                # 解密前端加密的字段
                obj.username = decrypt_data(obj.username, obj.username_iv)  # 使用传来的 IV 和密文解密
                obj.password = decrypt_data(obj.password, obj.password_iv)  # 使用传来的 IV 和密文解密
                obj.captcha = decrypt_data(obj.captcha, obj.captcha_iv)  # 使用传来的 IV 和密文解密

                current_user = await user_dao.get_by_username(db, obj.username)
                if not current_user:
                    raise errors.NotFoundError(msg='账号或密码有误')
                user_uuid = current_user.uuid
                username = current_user.username
                if not password_verify(obj.password + current_user.salt, current_user.password):
                    raise errors.AuthorizationError(msg='账号或密码有误')
                elif not current_user.status:
                    raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')
                captcha_code = await redis_client.get(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
                if not captcha_code:
                    raise errors.AuthorizationError(msg='验证码失效，请重新获取')
                if captcha_code.lower() != obj.captcha.lower():
                    raise errors.CustomError(error=CustomErrorCode.CAPTCHA_ERROR)
                current_user_id = current_user.id
                access_token = await create_access_token(str(current_user_id), current_user.is_multi_login)
                refresh_token = await create_refresh_token(str(current_user_id), current_user.is_multi_login)
            except errors.NotFoundError as e:
                raise errors.NotFoundError(msg=e.msg)
            except (errors.AuthorizationError, errors.CustomError) as e:
                task = BackgroundTask(
                    LoginLogService.create,
                    **dict(
                        request=request,
                        user_uuid=user_uuid,
                        username=username,
                        login_time=timezone.now(),
                        status=LoginLogStatusType.fail.value,
                        msg=e.msg,
                    ),
                )
                raise errors.AuthorizationError(msg=e.msg, background=task)
            except Exception as e:
                raise e
            else:
                background_tasks.add_task(
                    LoginLogService.create,
                    **dict(
                        request=request,
                        user_uuid=user_uuid,
                        username=username,
                        login_time=timezone.now(),
                        status=LoginLogStatusType.success.value,
                        msg='登录成功',
                    ),
                )
                await redis_client.delete(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
                await user_dao.update_login_time(db, obj.username)
                response.set_cookie(
                    key=settings.COOKIE_REFRESH_TOKEN_KEY,
                    value=refresh_token.refresh_token,
                    max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                    expires=timezone.f_utc(refresh_token.refresh_token_expire_time),
                    httponly=True,
                    secure=settings.COOKIE_SECURE,
                    samesite='lax',
                )
                await db.refresh(current_user)
                data = GetLoginToken(
                    access_token=access_token.access_token,
                    access_token_expire_time=access_token.access_token_expire_time,
                    user=current_user,  # type: ignore
                )
                return data

    @staticmethod
    async def register(
        *,
        request: Request,
        obj: AuthRegisterParam,
    ):
        async with async_db_session.begin() as db:
            try:
                obj.username = decrypt_data(obj.username, obj.username_iv)  # 使用传来的 IV 和密文解密
                obj.email = decrypt_data(obj.email, obj.email_iv)
                obj.password = decrypt_data(obj.password, obj.password_iv)  # 使用传来的 IV 和密文解密
                obj.captcha = decrypt_data(obj.captcha, obj.captcha_iv)  # 使用传来的 IV 和密文解密
                obj.nickname = decrypt_data(obj.nickname, obj.nickname_iv)  # 使用传来的 IV 和密文解密

                if not obj.password:
                    raise errors.ForbiddenError(msg='密码为空')
                username = await user_dao.get_by_username(db, obj.username)
                if username:
                    raise errors.ForbiddenError(msg='用户已注册')
                obj.nickname = obj.nickname or obj.username
                if await user_dao.get_by_nickname(db, obj.nickname):
                    for _ in range(10):
                        candidate = f'{obj.username[:14]}#{random.randrange(10000, 100000)}'
                        if not await user_dao.get_by_nickname(db, candidate):
                            obj.nickname = candidate
                            break
                    else:
                        raise errors.ForbiddenError(msg='无法生成可用昵称，请重试')
                email = await user_dao.check_email(db, obj.email)
                if email:
                    raise errors.ForbiddenError(msg='邮箱已注册')
                captcha_code = await redis_client.get(f'{admin_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
                if not captcha_code:
                    raise errors.AuthorizationError(msg='验证码失效，请重新获取')
                if captcha_code.lower() != obj.captcha.lower():
                    raise errors.CustomError(error=CustomErrorCode.CAPTCHA_ERROR)
                obj_dict = obj.dict(exclude={'captcha'})
                # 临时增加超级管理员权限
                user_param = RegisterUserParam(**obj_dict)
                await user_dao.create(db, user_param)
                await db.flush()

            except IntegrityError as exc:
                raise errors.ForbiddenError(msg='用户名、邮箱或昵称已存在') from exc
            except errors.NotFoundError as e:
                raise errors.NotFoundError(msg=e.msg)

    @staticmethod
    async def pwd_reset(*, request: Request, obj: AuthResetPasswordParam) -> int:
        async with async_db_session.begin() as db:
            try:
                obj.username = decrypt_data(obj.username, obj.username_iv)  # 使用传来的 IV 和密文解密
                obj.email = decrypt_data(obj.email, obj.email_iv)
                obj.password = decrypt_data(obj.password, obj.password_iv)  # 使用传来的 IV 和密文解密
                obj.email_code = decrypt_data(obj.email_code, obj.email_code_iv)
                obj.email = obj.email.strip().casefold()
                # 验证验证码
                code_key = AuthService._password_reset_key(obj.email)
                email_code = await redis_client.get(code_key)
                if not email_code:
                    raise errors.AuthorizationError(msg='邮箱验证码已失效，请重新获取')
                if not hmac.compare_digest(email_code, obj.email_code.strip()):
                    raise errors.CustomError(error=CustomErrorCode.CAPTCHA_ERROR)

                    # 检查密码
                if not obj.password:
                    raise errors.ForbiddenError(msg='密码为空')
                user = await user_dao.get_by_username(db, obj.username)
                if not user:
                    raise errors.ForbiddenError(msg='用户不存在')
                if not user.email or obj.email != user.email.casefold():
                    raise errors.ForbiddenError(msg='邮箱验证错误')

                    # 更新密码
                salt = user.salt
                hashed_password = get_hash_password(f'{obj.password}{salt}')  # 假设你需要哈希密码
                await user_dao.update_user_pwd(db, obj.username, hashed_password)
                await redis_client.delete(code_key)

            except errors.NotFoundError as e:
                raise errors.NotFoundError(msg=e.msg)

    @staticmethod
    async def new_token(*, request: Request, response: Response) -> GetNewToken:
        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
        if not refresh_token:
            raise errors.TokenError(msg='Refresh Token 丢失，请重新登录')
        try:
            user_id = jwt_decode(refresh_token)
        except Exception:
            raise errors.TokenError(msg='Refresh Token 无效')
        if request.user.id != user_id:
            raise errors.TokenError(msg='Refresh Token 无效')
        async with async_db_session() as db:
            current_user = await user_dao.get(db, user_id)
            if not current_user:
                raise errors.NotFoundError(msg='账号或密码有误')
            elif not current_user.status:
                raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')
            current_token = get_token(request)
            new_token = await create_new_token(
                sub=str(current_user.id),
                token=current_token,
                refresh_token=refresh_token,
                multi_login=current_user.is_multi_login,
            )
            response.set_cookie(
                key=settings.COOKIE_REFRESH_TOKEN_KEY,
                value=new_token.new_refresh_token,
                max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                expires=timezone.f_utc(new_token.new_refresh_token_expire_time),
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite='lax',
            )
            data = GetNewToken(
                access_token=new_token.new_access_token,
                access_token_expire_time=new_token.new_access_token_expire_time,
            )
            return data

    @staticmethod
    async def logout(*, request: Request, response: Response) -> None:
        token = get_token(request)
        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
        response.delete_cookie(settings.COOKIE_REFRESH_TOKEN_KEY)
        if request.user.is_multi_login:
            key = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:{token}'
            await redis_client.delete(key)
            if refresh_token:
                key = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:{refresh_token}'
                await redis_client.delete(key)
        else:
            key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:'
            await redis_client.delete_prefix(key_prefix)
            key_prefix = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:'
            await redis_client.delete_prefix(key_prefix)


auth_service = AuthService()
