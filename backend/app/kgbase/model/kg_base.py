#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.kgbase.model.chat_library import ChatLibrary
from backend.app.kgbase.model.knowledge_graph import KnowledgeGraph
from backend.app.kgbase.model.schema_graph import SchemaGraph
from backend.common.model import Base, id_key
from backend.database.db_mysql import uuid4_str


class KgBase(Base):
    """图谱库表"""

    __tablename__ = 'kg_base'

    id: Mapped[id_key] = mapped_column(init=False)
    user_uuid: Mapped[str] = mapped_column(ForeignKey('sys_user.uuid'), nullable=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, comment='名')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')
    cover_image: Mapped[str | None] = mapped_column(String(255), default=None, comment='头像')
    description: Mapped[str | None] = mapped_column(Text, default=None, comment='描述')

    knowledge_graphs: Mapped[list['KnowledgeGraph']] = relationship(
        'KnowledgeGraph',
        cascade='all, delete-orphan',
        init=False,
    )

    schema_graphs: Mapped[list['SchemaGraph']] = relationship(
        'SchemaGraph',
        cascade='all, delete-orphan',
        init=False,
    )

    chat_library: Mapped[list['ChatLibrary']] = relationship(
        'ChatLibrary',
        cascade='all, delete-orphan',
        init=False,
    )
