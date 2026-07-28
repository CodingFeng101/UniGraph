from typing import Any, Dict, List

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key
from backend.database.db_mysql import uuid4_str


class ChatLibrary(Base):
    """Conversation session."""

    __tablename__ = 'chat_library'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='Chat Message Name')
    kg_base_uuid: Mapped[str] = mapped_column(ForeignKey('kg_base.uuid'), nullable=False)
    messages: Mapped[List[Dict[str, str]]] = mapped_column(JSON, nullable=True, default_factory=dict)
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ChatMessage(Base):
    """One user or assistant message in a conversation."""

    __tablename__ = 'chat_message'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    chat_library_uuid: Mapped[str] = mapped_column(
        ForeignKey('chat_library.uuid', ondelete='CASCADE'), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    knowledge_graph_uuid: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    effort: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)


class ChatMessageSource(Base):
    """A source category attached to one assistant response."""

    __tablename__ = 'chat_message_source'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    message_uuid: Mapped[str] = mapped_column(
        ForeignKey('chat_message.uuid', ondelete='CASCADE'), nullable=False, index=True
    )
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[Dict[str, Any] | List[Any]] = mapped_column(JSON, nullable=False, default_factory=dict)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ChatShare(Base):
    """Read-only snapshot shared through an unguessable public identifier."""

    __tablename__ = 'chat_share'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    chat_library_uuid: Mapped[str] = mapped_column(
        ForeignKey('chat_library.uuid', ondelete='CASCADE'), nullable=False, unique=True, index=True
    )
    public_id: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
