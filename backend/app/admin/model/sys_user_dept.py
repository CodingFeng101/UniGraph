#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from sqlalchemy import INT, Column, ForeignKey, Integer, Table

from backend.common.model import MappedBase

# 定义 sys_user_dept 表，表示用户和部门的多对多关系
sys_user_dept = Table(
    'sys_user_dept',
    MappedBase.metadata,
    Column('id', INT, primary_key=True, unique=True, index=True, autoincrement=True, comment='主键ID'),
    Column('user_id', Integer, ForeignKey('sys_user.id', ondelete='CASCADE'), primary_key=True, comment='用户ID'),
    Column('dept_id', Integer, ForeignKey('sys_dept.id', ondelete='CASCADE'), primary_key=True, comment='部门ID'),
)
