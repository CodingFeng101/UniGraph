from __future__ import annotations

from datetime import datetime

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class SchemaEntityBase(SchemaBase):
    """获取图谱详情"""

    name: str
    type: str | None = None
    attributes: str | None = None
    definition: str | None = None
    source: str | None = None
    status: int | None = StatusType.enable.value


class SchemaEntityResponse(SchemaEntityBase):
    id: int
    uuid: str
    schema_graph_uuid: str
    created_time: datetime
    updated_time: datetime | None = None


class AddSchemaEntityParam(SchemaEntityBase):
    schema_graph_uuid: str

    def __str__(self):
        return self.attributes


class UpdateSchemaEntityParam(SchemaBase):
    schema_graph_uuid: str
    data: SchemaEntityBase


class GetSchemaEntityDetail(SchemaEntityBase):
    schema_graph: list
