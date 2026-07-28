#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.path_conf import BasePath


class Settings(BaseSettings):
    """Global settings loaded from backend/.env."""

    model_config = SettingsConfigDict(
        env_file=f'{BasePath}/.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    ENVIRONMENT: Literal['dev', 'pro']

    SSO_USER_INFO_URL: str | None = 'http://127.0.0.1:8000/tsp/v1/sys/users/me'
    INDEX_EXPORT_URL_ROOT: str | None = 'http://127.0.0.1:8000/knowg/v1/knowledge/ask'

    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DATABASE: int

    TOKEN_SECRET_KEY: str
    OPERA_LOG_ENCRYPT_SECRET_KEY: str
    JXNU_AES_SECRET_KEY: str | None = None

    FASTAPI_API_V1_PATH: str = '/knowg/v1'
    FASTAPI_TITLE: str = 'FastAPI'
    FASTAPI_VERSION: str = '0.0.1'
    FASTAPI_DESCRIPTION: str = 'FastAPI Best Architecture'
    FASTAPI_DOCS_URL: str | None = f'{FASTAPI_API_V1_PATH}/docs'
    FASTAPI_REDOCS_URL: str | None = f'{FASTAPI_API_V1_PATH}/redocs'
    FASTAPI_OPENAPI_URL: str | None = f'{FASTAPI_API_V1_PATH}/openapi'
    FASTAPI_STATIC_FILES: bool = True

    @model_validator(mode='before')
    @classmethod
    def validate_openapi_url(cls, values):
        if values.get('ENVIRONMENT') == 'pro':
            values['FASTAPI_DOCS_URL'] = None
            values['FASTAPI_REDOCS_URL'] = None
            values['FASTAPI_OPENAPI_URL'] = None
        return values

    MYSQL_ECHO: bool = False
    MYSQL_DATABASE: str = 'onlineunigraph'
    MYSQL_CHARSET: str = 'utf8mb4'

    REDIS_TIMEOUT: int = 5

    TOKEN_ALGORITHM: str = 'HS256'
    TOKEN_EXPIRE_SECONDS: int = 120 * 60
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7
    TOKEN_REDIS_PREFIX: str = 'fba:token'
    TOKEN_REFRESH_REDIS_PREFIX: str = 'fba:refresh_token'

    TOKEN_REQUEST_PATH_EXCLUDE: list[str] = [
        f'{FASTAPI_API_V1_PATH}/auth/login',
        f'{FASTAPI_API_V1_PATH}/oauth2/jxnu/jxnu-auth',
        f'{FASTAPI_API_V1_PATH}/auth/captcha',
        f'{FASTAPI_API_V1_PATH}/auth/register',
        f'{FASTAPI_API_V1_PATH}/sys/users/register',
        f'{FASTAPI_API_V1_PATH}/sys/users/reset_password',
        f'{FASTAPI_API_V1_PATH}/auth/sso',
        f'{FASTAPI_API_V1_PATH}/auth/ssologin',
    ]

    JWT_USER_REDIS_PREFIX: str = 'fba:user'
    JWT_USER_REDIS_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7

    PERMISSION_MODE: Literal['casbin', 'role-menu'] = 'role-menu'
    PERMISSION_REDIS_PREFIX: str = 'fba:permission'

    RBAC_CASBIN_EXCLUDE: set[tuple[str, str]] = {
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/logout'),
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/token/new'),
    }

    RBAC_ROLE_MENU_EXCLUDE: list[str] = [
        'sys:monitor:redis',
        'sys:monitor:server',
    ]

    COOKIE_REFRESH_TOKEN_KEY: str = 'fba_refresh_token'
    COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS: int = TOKEN_REFRESH_EXPIRE_SECONDS

    LOG_ROOT_LEVEL: str = 'NOTSET'
    LOG_STD_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_LOGURU_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_CID_DEFAULT_VALUE: str = '-'
    LOG_CID_UUID_LENGTH: int = 32
    LOG_STDOUT_LEVEL: str = 'INFO'
    LOG_STDERR_LEVEL: str = 'ERROR'
    LOG_STDOUT_FILENAME: str = 'fba_access.log'
    LOG_STDERR_FILENAME: str = 'fba_error.log'

    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_ACCESS: bool = True

    TRACE_ID_REQUEST_HEADER_KEY: str = 'X-Request-ID'

    CORS_ALLOWED_ORIGINS: list[str] = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:5174',
        'http://localhost:5175',
        'http://localhost:5273',
        'http://localhost:5001',
        'http://localhost:8000',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5174',
        'http://127.0.0.1:5273',
        'http://127.0.0.1:8000',
    ]
    CORS_EXPOSE_HEADERS: list[str] = [
        TRACE_ID_REQUEST_HEADER_KEY,
    ]

    DATETIME_TIMEZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    REQUEST_LIMITER_REDIS_PREFIX: str = 'fba:limiter'

    DEMO_MODE: bool = False
    DEMO_MODE_EXCLUDE: set[tuple[str, str]] = {
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/login'),
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/logout'),
        ('GET', f'{FASTAPI_API_V1_PATH}/auth/captcha'),
    }

    IP_LOCATION_PARSE: Literal['online', 'offline', 'false'] = 'offline'
    IP_LOCATION_REDIS_PREFIX: str = 'fba:ip:location'
    IP_LOCATION_EXPIRE_SECONDS: int = 60 * 60 * 24

    OPERA_LOG_PATH_EXCLUDE: list[str] = [
        '/favicon.ico',
        FASTAPI_DOCS_URL,
        FASTAPI_REDOCS_URL,
        FASTAPI_OPENAPI_URL,
        f'{FASTAPI_API_V1_PATH}/auth/login/swagger',
        f'{FASTAPI_API_V1_PATH}/oauth2/github/callback',
        f'{FASTAPI_API_V1_PATH}/oauth2/linux-do/callback',
    ]
    OPERA_LOG_ENCRYPT_TYPE: int = 1
    OPERA_LOG_ENCRYPT_KEY_INCLUDE: list[str] = [
        'access_token',
        'api_key',
        'client_secret',
        'password',
        'old_password',
        'new_password',
        'confirm_password',
        'secret',
        'token',
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
