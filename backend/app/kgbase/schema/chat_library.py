from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class LibraryBase(SchemaBase):
    kg_base_uuid: str | None = Field('')
    name: str | None = Field('')
    is_favorite: bool = False


class LibraryDetail(LibraryBase):
    messages: Dict[str, str] | None = Field(default_factory=dict)
    conversation: List[Dict[str, Any]] = Field(default_factory=list)


class CreateLibraryParam(LibraryBase):
    pass


class LibraryResponse(LibraryBase):
    uuid: str
    created_time: datetime
    updated_time: datetime | None = None


class UpdateLibraryParam(LibraryBase):
    messages: Dict[str, str] | None = Field(default_factory=dict)


class AppendTurnParam(SchemaBase):
    model_config = ConfigDict(protected_namespaces=())

    user_content: str
    assistant_content: str
    knowledge_graph_uuid: str | None = None
    model_name: str | None = None
    effort: str | None = None
    sources: Dict[str, Any] = Field(default_factory=dict)


class AppendMessageParam(SchemaBase):
    model_config = ConfigDict(protected_namespaces=())

    role: Literal['user', 'assistant']
    content: str
    knowledge_graph_uuid: str | None = None
    model_name: str | None = None
    effort: str | None = None
    sources: Dict[str, Any] = Field(default_factory=dict)


class UpdateMessageParam(SchemaBase):
    content: str = Field(min_length=1)


class GenerateTitleParam(SchemaBase):
    content: str


class FavoriteParam(SchemaBase):
    is_favorite: bool


class ChatShareResponse(SchemaBase):
    public_id: str
    title: str
    message_count: int
    is_active: bool
    created_time: datetime
    updated_time: datetime | None = None


class PublicChatShareResponse(SchemaBase):
    """Public, read-only conversation snapshot.

    Deliberately excludes the conversation, knowledge-base and message UUIDs.
    """

    public_id: str
    title: str
    message_count: int
    shared_time: datetime
    conversation: List[Dict[str, Any]] = Field(default_factory=list)
