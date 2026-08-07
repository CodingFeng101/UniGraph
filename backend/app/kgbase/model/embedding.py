from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.model import Base, id_key
from backend.database.db_mysql import uuid4_str

if TYPE_CHECKING:
    from backend.app.kgbase.model.knowledge_entity import KnowledgeEntity


class Embedding(Base):
    __tablename__ = 'uni_embedding'
    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    vector: Mapped[str] = mapped_column(Text, comment='实体嵌入向量')

    # 外键，关联 knowledge_entity 表
    knowledge_entity_uuid: Mapped[str] = mapped_column(
        ForeignKey('knowledge_entity.uuid'), nullable=False, comment='关联的知识实体ID'
    )

    # 多对一关系：多个embedding可以关联到一个knowledge_entity
    knowledge_entity: Mapped['KnowledgeEntity'] = relationship(
        'KnowledgeEntity',
        init=False,
        back_populates='embeddings',
    )
