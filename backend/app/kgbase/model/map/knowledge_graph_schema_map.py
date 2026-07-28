from sqlalchemy import Column, ForeignKey, Table

from backend.common.model import MappedBase

# Association Tables for Many-to-Many relationships
knowledge_graph_schema_map = Table(
    'knowledge_graph_schema_map',
    MappedBase.metadata,
    Column('knowledge_graph_id', ForeignKey('knowledge_graph.id'), primary_key=True),
    Column('schema_graph_id', ForeignKey('schema_graph.id'), primary_key=True),
)
