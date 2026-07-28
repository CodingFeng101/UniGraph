from __future__ import annotations

from datetime import datetime

from pydantic import model_validator

from backend.app.kgbase.schema.knowledge_graph import KnowledgeGraphResponse
from backend.app.kgbase.schema.schema_graph import SchemaGraphResponse
from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class KgBase(SchemaBase):
    """获取图谱库详情"""

    name: str
    description: str | None
    cover_image: str | None
    status: int | None = StatusType.enable.value


class KgBaseResponse(KgBase):
    id: int
    uuid: str
    user_uuid: str
    created_time: datetime
    updated_time: datetime | None = None


class AddKgBaseParam(KgBase):
    user_uuid: str | None = None

    @model_validator(mode='before')
    def check_name(cls, values):
        name = values.get('name')
        if len(name) < 3:
            raise ValueError('图谱库名称不能少于 3 个字符')
        return values


class UpdateKgBaseParam(KgBase):
    @model_validator(mode='before')
    def check_name(cls, values):
        if values.get('name') and len(values.get('name')) < 3:
            raise ValueError('图谱库名称不能少于 3 个字符')
        return values


class GetKgBaseDetail(KgBaseResponse):
    knowledge_graphs: list[KnowledgeGraphResponse]
    schema_graphs: list[SchemaGraphResponse]
