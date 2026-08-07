from __future__ import annotations

from datetime import datetime

from pydantic import Field

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class KnowledgeRelationshipBase(SchemaBase):
    """获取图谱详情"""

    name: str
    type: str | None = None
    attributes: str | None = Field('')
    status: int | None = StatusType.enable.value
    source: str | None = Field('')


class KnowledgeRelationshipResponse(KnowledgeRelationshipBase):
    id: int
    uuid: str
    knowledge_graph_uuid: str
    source_entity_uuid: str
    target_entity_uuid: str
    source: str

    created_time: datetime
    updated_time: datetime | None = None


class AddKnowledgeRelationshipParam(KnowledgeRelationshipBase):
    knowledge_graph_uuid: str
    source_entity_uuid: str
    target_entity_uuid: str


class UpdateKnowledgeRelationshipParam(KnowledgeRelationshipBase):
    pass


class GetKnowledgeRelationshipDetail(KnowledgeRelationshipBase):
    knowledge_graph: list
