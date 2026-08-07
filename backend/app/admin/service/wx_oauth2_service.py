#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fast_captcha import text_captcha

from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.schema.token import GetLoginToken
from backend.app.admin.schema.user import RegisterUserParam
from backend.common.security import jwt
from backend.database.db_mysql import async_db_session


class WxOAuth2Service:
    @staticmethod
    async def create_with_login(*, user_uuid: str) -> GetLoginToken | None:
        async with async_db_session.begin() as db:
            sys_user = await user_dao.get_with_relation(db=db, username=user_uuid)
            if not sys_user:
                # 创建系统用户
                _username = f'{user_uuid}'
                _email = f'#{text_captcha(5)}@wxlogin.com'
                _nickname = f'#{text_captcha(5)}'

                new_sys_user = RegisterUserParam(username=_username, password=None, nickname=_nickname, email=_email)
                await user_dao.create(db, new_sys_user, social=True)

        async with async_db_session.begin() as db:
            sys_user = await user_dao.get_with_relation(db=db, username=user_uuid)
            # 创建 token
            access_token = await jwt.create_access_token(str(sys_user.id), sys_user.is_multi_login)
            await jwt.create_refresh_token(str(sys_user.id), multi_login=sys_user.is_multi_login)
            await user_dao.update_login_time(db, sys_user.username)
            await db.refresh(sys_user)

            data = GetLoginToken(
                access_token=access_token.access_token,
                access_token_expire_time=access_token.access_token_expire_time,
                user=sys_user,
            )
            return data


wx_oauth2_service = WxOAuth2Service()
