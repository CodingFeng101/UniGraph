#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.kgbase.model import community_entity_map
from backend.common.model import Base, id_key
from backend.database.db_mysql import uuid4_str

if TYPE_CHECKING:
    from backend.app.kgbase.model.community import Community
    from backend.app.kgbase.model.embedding import Embedding
    from backend.app.kgbase.model.knowledge_graph import KnowledgeGraph


class KnowledgeEntity(Base):
    __tablename__ = 'knowledge_entity'

    # No default value fields first
    id: Mapped[id_key] = mapped_column(init=False)  # Typically the primary key
    knowledge_graph_uuid: Mapped[str] = mapped_column(ForeignKey('knowledge_graph.uuid'))
    # Fields with default values should follow
    uuid: Mapped[str] = mapped_column(
        String(50), init=False, default_factory=uuid4_str, unique=True
    )  # Using a UUID function to generate default value
    name: Mapped[str] = mapped_column(Text, comment='实体名称')
    type: Mapped[str] = mapped_column(Text, comment='实体类型')
    attributes: Mapped[str] = mapped_column(Text, comment='实体属性')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')

    # ForeignKey relationships

    knowledge_graph: Mapped['KnowledgeGraph'] = relationship('KnowledgeGraph', back_populates='entities', init=False)

    # Many-to-many relationships with Source and Community
    # The source relationship is disabled until its mapping table is restored.
    communities: Mapped[List['Community']] = relationship(
        'Community', secondary=community_entity_map, back_populates='entities', init=False
    )

    # One-to-many relationship with Embedding
    embeddings: Mapped[List['Embedding']] = relationship(
        'Embedding', back_populates='knowledge_entity', cascade='all, delete-orphan', init=False
    )
