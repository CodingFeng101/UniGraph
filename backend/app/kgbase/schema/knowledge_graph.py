from __future__ import annotations

from datetime import datetime

from pydantic import Field

from backend.common.schema import SchemaBase


class KnowledgeGraphBase(SchemaBase):
    """获取图谱详情"""

    name: str
    schema_graph_uuid: str | None = Field('')
    kg_base_uuid: str | None = Field('')


class KnowledgeGraphResponse(KnowledgeGraphBase):
    id: int
    uuid: str
    index_status: int
    created_time: datetime
    updated_time: datetime | None = None


class AddKnowledgeGraphParam(SchemaBase):
    file_paths: list[str]
    data: KnowledgeGraphBase


class AskKnowledgeGraphParam(SchemaBase):
    message: str
    infer: bool = False
    depth: int = 1
    user_token: str
    chat_library_uuid: str | None = None
    current_message_uuid: str | None = None
    llm_model_uuid: str | None = None


class BuildKnowledgeGraphIndexParam(SchemaBase):
    knowledge_graph_uuid: str


class UpdateKnowledgeGraphBase(SchemaBase):
    name: str | None = None
    schema_graph_uuid: str | None = Field('')


class UpdateKnowledgeGraphParam(SchemaBase):
    file_paths: list[str]
    data: UpdateKnowledgeGraphBase


class IndexKnowledgeGraphBase(BuildKnowledgeGraphIndexParam):
    file_path: str | None = None
