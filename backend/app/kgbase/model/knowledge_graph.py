#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.kgbase.model import Community, KnowledgeEntity, KnowledgeRelationship, SchemaGraph
from backend.common.model import Base, id_key
from backend.database.db_mysql import uuid4_str


class KnowledgeGraph(Base):
    """知识图谱库表"""

    __tablename__ = 'knowledge_graph'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='Knowledge Graph Name')

    kg_base_uuid: Mapped[str] = mapped_column(ForeignKey('kg_base.uuid'), nullable=False)

    schema_graph_uuid: Mapped[str] = mapped_column(ForeignKey('schema_graph.uuid'), nullable=False)
    index_status: Mapped[str] = mapped_column(String(50), nullable=False, default='0', comment='Index Status')
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='Depth')
    schema_graph: Mapped['SchemaGraph'] = relationship('SchemaGraph', back_populates='knowledge_graphs', init=False)

    entities: Mapped[list['KnowledgeEntity']] = relationship(
        'KnowledgeEntity', back_populates='knowledge_graph', init=False, cascade='all, delete-orphan'
    )

    relationships: Mapped[list['KnowledgeRelationship']] = relationship(
        'KnowledgeRelationship', back_populates='knowledge_graph', init=False, cascade='all, delete-orphan'
    )

    communities: Mapped[list['Community']] = relationship(
        'Community', back_populates='knowledge_graph', init=False, cascade='all, delete-orphan'
    )
