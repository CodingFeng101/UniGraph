#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, EmailStr, Field, model_validator
from typing_extensions import Self

from backend.app.admin.schema.dept import GetDeptListDetails
from backend.app.admin.schema.role import GetRoleListDetails
from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class AuthSchemaBase(SchemaBase):
    username: str
    password: Optional[str]


class AuthLoginParam(AuthSchemaBase):
    captcha: str
    username_iv: str  # 添加 iv 字段
    password_iv: str  # 添加 iv 字段
    captcha_iv: str  # 添加 iv 字段


class RegisterUserParam(AuthSchemaBase):
    nickname: str
    email: str


class AuthRegisterParam(SchemaBase):
    username: str
    password: str
    nickname: str
    email: str
    setting: Optional[str] = None
    captcha: str
    username_iv: str  # 添加 iv 字段
    nickname_iv: str
    password_iv: str  # 添加 iv 字段
    captcha_iv: str  # 添加 iv 字段
    email_iv: str


class AuthResetPasswordParam(SchemaBase):
    username: str
    email: str
    password: str
    email_code: str
    username_iv: str  # 添加 iv 字段
    password_iv: str  # 添加 iv 字段
    email_iv: str
    email_code_iv: str


class AuthPasswordResetCodeParam(SchemaBase):
    username: str
    email: str
    username_iv: str
    email_iv: str


class AddUserParam(AuthSchemaBase):
    depts: list[int]
    roles: list[int]
    nickname: Optional[str] = None
    email: EmailStr = Field(..., examples=['user@example.com'])


class UserInfoSchemaBase(SchemaBase):
    # dept_id: Optional[int] = None
    username: str
    nickname: str
    email: EmailStr = Field(..., examples=['user@example.com'])
    # phone: Optional[CustomPhoneNumber] = None


# 临时修改为只更新key和url
class UpdateUserParam(SchemaBase):
    email: str
    nickname: str
    username: str


class UpdateUserPwdParam(UserInfoSchemaBase):
    password: str


class UpdateUserRoleParam(SchemaBase):
    roles: list[int]


class UpdateUserDeptParam(SchemaBase):
    depts: list[int]


class AvatarParam(SchemaBase):
    url: str = Field(..., min_length=1, description='头像文件地址')


class GetUserInfoNoRelationDetail(UserInfoSchemaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uuid: str
    avatar: Optional[str] = None
    status: StatusType = Field(default=StatusType.enable)
    # phone: Optional[CustomPhoneNumber] = None
    is_superuser: bool
    is_staff: bool
    is_multi_login: bool
    join_time: datetime = None
    last_login_time: Optional[datetime] = None


class GetUserInfoListDetails(GetUserInfoNoRelationDetail):
    model_config = ConfigDict(from_attributes=True)

    depts: list[GetDeptListDetails]
    roles: list[GetRoleListDetails]


class GetCurrentUserInfoDetail(GetUserInfoListDetails):
    model_config = ConfigDict(from_attributes=True)

    depts: Optional[List[GetDeptListDetails] | List[str]] = None
    roles: Optional[List[GetRoleListDetails] | List[str]] = None
    text_generation_model: Optional[str] = None

    @model_validator(mode='after')
    def handel(self) -> Self:
        """处理部门和角色"""
        roles = self.roles

        if roles:
            self.roles = [role.name for role in roles]  # type: ignore
        return self


class CurrentUserIns(GetUserInfoListDetails):
    model_config = ConfigDict(from_attributes=True)


class ResetPasswordParam(SchemaBase):
    old_password: str
    new_password: str
    confirm_password: str
