#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.model import Base, id_key
from backend.database.db_mysql import uuid4_str

if TYPE_CHECKING:
    from backend.app.kgbase.model.knowledge_graph import KnowledgeGraph
    from backend.app.kgbase.model.schema_entity import SchemaEntity
    from backend.app.kgbase.model.schema_relationship import SchemaRelationship


class SchemaGraph(Base):
    __tablename__ = 'schema_graph'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    kg_base_uuid: Mapped[str] = mapped_column(ForeignKey('kg_base.uuid'), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='Schema Graph Name')
    aim: Mapped[str | None] = mapped_column(Text, default=None, comment='目标描述')
    modify_info: Mapped[str | None] = mapped_column(Text, default=None, comment='修改信息')
    modify_suggestion: Mapped[str | None] = mapped_column(Text, default=None, comment='修改建议')

    entities: Mapped[list['SchemaEntity']] = relationship(
        'SchemaEntity', back_populates='schema_graph', cascade='all, delete-orphan', init=False
    )

    relationships: Mapped[list['SchemaRelationship']] = relationship(
        'SchemaRelationship', back_populates='schema_graph', cascade='all, delete-orphan', init=False
    )

    knowledge_graphs: Mapped[list['KnowledgeGraph']] = relationship(
        'KnowledgeGraph',
        # back_populates="schema_graph",
        cascade='all, delete-orphan',
        init=False,
    )
