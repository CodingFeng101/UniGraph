import json

from pydantic import model_validator

from backend.app.kgbase.schema.community import CommunityResponse
from backend.app.kgbase.schema.embedding import EmbeddingResponse
from backend.app.kgbase.schema.knowledge_entity import KnowledgeEntityResponse
from backend.app.kgbase.schema.knowledge_graph import KnowledgeGraphResponse
from backend.app.kgbase.schema.knowledge_relationship import KnowledgeRelationshipResponse
from backend.app.kgbase.schema.schema_entity import SchemaEntityResponse
from backend.app.kgbase.schema.schema_graph import SchemaGraphResponse
from backend.app.kgbase.schema.schema_relationship import SchemaRelationshipResponse
from backend.app.kgbase.schema.source import SourceResponse as SourceResponse


class GetSchemaGraphDetail(SchemaGraphResponse):
    knowledge_graphs: list[KnowledgeGraphResponse]
    entities: list[SchemaEntityResponse]
    relationships: list[SchemaRelationshipResponse]


class GetKnowledgeEntityDetail(KnowledgeEntityResponse):
    embeddings: list[EmbeddingResponse] | list
    communities: list[CommunityResponse] | list[str]

    @model_validator(mode='after')
    def handel(self):
        embeddings = self.embeddings
        if embeddings and len(embeddings) >= 1:
            self.embeddings = json.loads(embeddings[0].vector)

        communities = self.communities
        if communities and len(communities) >= 1:
            self.communities = [entity_community.uuid for entity_community in communities]
        return self


class GetIndexDetail(KnowledgeGraphResponse):
    entities: list[GetKnowledgeEntityDetail]
    relationships: list[KnowledgeRelationshipResponse]
    communities: list[CommunityResponse]


class GetKnowledgeGraphDetail(GetIndexDetail):
    schema_graph: SchemaGraphResponse
