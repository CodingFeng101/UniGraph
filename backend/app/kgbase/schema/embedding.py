from __future__ import annotations

import json

from pydantic import Field, model_validator

from backend.common.schema import SchemaBase


class EmbeddingBase(SchemaBase):
    """获取实体向量详情"""

    vector: str
    knowledge_entity_uuid: str | None = Field('')


class EmbeddingResponse(SchemaBase):
    vector: str

    @model_validator(mode='after')
    def handel(self):
        vector = self.vector

        if vector:
            self.vector = json.loads(vector)
        return self


class AddEmbeddingParam(SchemaBase):
    content: str
    knowledge_graph_uuid: EmbeddingBase


class UpdateEmbeddingParam(SchemaBase):
    content: str | None = None


class GetEmbeddingDetail(EmbeddingBase):
    knowledge_graph: list
