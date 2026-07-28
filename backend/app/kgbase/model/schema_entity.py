# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.model import Base, id_key
from backend.database.db_mysql import uuid4_str

if TYPE_CHECKING:
    from backend.app.kgbase.model.schema_graph import SchemaGraph


class SchemaEntity(Base):
    """知识图谱实体表"""

    __tablename__ = 'schema_entity'

    # 主键，实体ID
    id: Mapped[id_key] = mapped_column(init=False)
    # 外键，关联 SchemaGraph
    schema_graph_uuid: Mapped[str] = mapped_column(ForeignKey('schema_graph.uuid'))
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)  # UUID
    name: Mapped[str] = mapped_column(Text, comment='实体名')  # 实体名称
    type: Mapped[str | None] = mapped_column(Text, nullable=True, comment='实体类型')  # 实体类型
    definition: Mapped[str] = mapped_column(Text, comment='类型定义')  # 类型定义
    attributes: Mapped[str] = mapped_column(Text, comment='实体属性')  # 实体的属性（JSON 或字符串格式）
    source: Mapped[str] = mapped_column(Text, comment='实体类型来源')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')  # 状态标识

    # 关系：指向 SchemaGraph 表
    schema_graph: Mapped['SchemaGraph'] = relationship('SchemaGraph', back_populates='entities', init=False)
