#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.enums import StatusType
from backend.common.schema import CustomEmailStr, CustomPhoneNumber, SchemaBase


class DeptSchemaBase(SchemaBase):
    id: int
    name: str
    parent_id: int | None = Field(default=None, description='部门父级ID')
    sort: int = Field(default=0, ge=0, description='排序')
    leader: str | None = None
    phone: CustomPhoneNumber | None = None
    email: CustomEmailStr | None = None
    worklogStandard: str | None = None
    control: str | None = None
    status: StatusType = Field(default=StatusType.enable)


class CreateDeptParam(SchemaBase):
    name: str
    parent_id: int | None = Field(default=None, description='部门父级ID')
    sort: int = Field(default=0, ge=0, description='排序')
    leader: str | None = None
    # phone: str | None = None
    email: CustomEmailStr | None = None
    status: StatusType = Field(default=StatusType.enable)


class UpdateDeptParam(SchemaBase):
    name: str
    parent_id: int | None = Field(default=None, description='部门父级ID')
    worklogStandard: str | None = None
    control: str | None = None
    leader: str | None = None
    phone: CustomPhoneNumber | None = None
    email: CustomEmailStr | None = None
    status: StatusType = Field(default=StatusType.enable)


class GetDeptListDetails(DeptSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    del_flag: bool
    created_time: datetime
    updated_time: datetime | None = None
