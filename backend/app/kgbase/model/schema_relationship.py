#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.model import Base, id_key
from backend.database.db_mysql import uuid4_str

if TYPE_CHECKING:
    from backend.app.kgbase.model.schema_graph import SchemaGraph


class SchemaRelationship(Base):
    """模式图关系表"""

    __tablename__ = 'schema_relationship'

    id: Mapped[id_key] = mapped_column(init=False)
    # 外键，关联到 SchemaEntity 表中的实体
    source_entity_uuid: Mapped[str] = mapped_column(ForeignKey('schema_entity.uuid'))
    target_entity_uuid: Mapped[str] = mapped_column(ForeignKey('schema_entity.uuid'))

    # 外键，关联到 SchemaGraph 表
    schema_graph_uuid: Mapped[str] = mapped_column(ForeignKey('schema_graph.uuid'))
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)  # UUID

    name: Mapped[str] = mapped_column(Text, comment='关系名称')  # 关系的名称
    type: Mapped[str] = mapped_column(Text, comment='关系类型')  # 关系的类型
    attributes: Mapped[str] = mapped_column(Text, comment='关系属性')  # 关系的附加属性（例如，描述）
    definition: Mapped[str] = mapped_column(Text, comment='类型定义')  # 类型定义
    source: Mapped[str] = mapped_column(Text, comment='关系类型来源')

    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')  # 状态标识

    # 关系：指向 SchemaGraph 表
    schema_graph: Mapped['SchemaGraph'] = relationship('SchemaGraph', back_populates='relationships', init=False)
