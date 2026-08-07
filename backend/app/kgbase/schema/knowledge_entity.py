from __future__ import annotations

from datetime import datetime

from pydantic import model_validator

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class KnowledgeEntityBase(SchemaBase):
    """获取图谱详情"""

    name: str
    type: str | None = None
    attributes: str | None = None
    status: int | None = StatusType.enable.value


class KnowledgeEntityResponse(KnowledgeEntityBase):
    id: int
    uuid: str
    knowledge_graph_uuid: str
    created_time: datetime
    updated_time: datetime | None = None


class AddKnowledgeEntityParam(KnowledgeEntityBase):
    knowledge_graph_uuid: str


class UpdateKnowledgeEntityParam(KnowledgeEntityBase):
    @model_validator(mode='before')
    def check_name(cls, values):
        if values.get('name') and len(values.get('name')) < 1:
            raise ValueError('实体不能少于 1 个字符')
        return values


class AddKnowledgeEntitySource(SchemaBase):
    knowledge_entity_id: int
    source_id: int
