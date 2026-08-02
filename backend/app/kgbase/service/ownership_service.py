from sqlalchemy import select

from backend.app.kgbase.model import (
    KgBase,
    KnowledgeEntity,
    KnowledgeGraph,
    KnowledgeRelationship,
    SchemaEntity,
    SchemaGraph,
    SchemaRelationship,
)
from backend.common.exception.errors import NotFoundError
from backend.database.db_mysql import async_db_session


class OwnershipService:
    @staticmethod
    async def _require(statement, message: str) -> None:
        async with async_db_session() as db:
            if (await db.execute(statement.limit(1))).scalar_one_or_none() is None:
                raise NotFoundError(msg=message)

    @classmethod
    async def require_kg_base(cls, *, user_uuid: str, uuid: str | None = None, pk: int | None = None) -> None:
        statement = select(KgBase.id).where(KgBase.user_uuid == user_uuid)
        statement = statement.where(KgBase.uuid == uuid) if uuid is not None else statement.where(KgBase.id == pk)
        await cls._require(statement, '知识库不存在')

    @classmethod
    async def require_schema_graph(cls, *, user_uuid: str, uuid: str | None = None, pk: int | None = None) -> None:
        statement = (
            select(SchemaGraph.id)
            .join(KgBase, SchemaGraph.kg_base_uuid == KgBase.uuid)
            .where(KgBase.user_uuid == user_uuid)
        )
        statement = (
            statement.where(SchemaGraph.uuid == uuid) if uuid is not None else statement.where(SchemaGraph.id == pk)
        )
        await cls._require(statement, '知识架构不存在')

    @classmethod
    async def require_schema_graph_in_kg_base(
        cls, *, user_uuid: str, schema_graph_uuid: str | None, kg_base_uuid: str | None
    ) -> None:
        statement = (
            select(SchemaGraph.id)
            .join(KgBase, SchemaGraph.kg_base_uuid == KgBase.uuid)
            .where(
                KgBase.user_uuid == user_uuid,
                SchemaGraph.uuid == schema_graph_uuid,
                SchemaGraph.kg_base_uuid == kg_base_uuid,
            )
        )
        await cls._require(statement, '知识架构不存在')

    @classmethod
    async def require_knowledge_graph(cls, *, user_uuid: str, uuid: str | None = None, pk: int | None = None) -> None:
        statement = (
            select(KnowledgeGraph.id)
            .join(KgBase, KnowledgeGraph.kg_base_uuid == KgBase.uuid)
            .where(KgBase.user_uuid == user_uuid)
        )
        statement = (
            statement.where(KnowledgeGraph.uuid == uuid)
            if uuid is not None
            else statement.where(KnowledgeGraph.id == pk)
        )
        await cls._require(statement, '知识图谱不存在')

    @classmethod
    async def require_schema_entity(cls, *, user_uuid: str, uuid: str | None = None, pk: int | None = None) -> None:
        statement = (
            select(SchemaEntity.id)
            .join(SchemaGraph, SchemaEntity.schema_graph_uuid == SchemaGraph.uuid)
            .join(KgBase, SchemaGraph.kg_base_uuid == KgBase.uuid)
            .where(KgBase.user_uuid == user_uuid)
        )
        statement = (
            statement.where(SchemaEntity.uuid == uuid) if uuid is not None else statement.where(SchemaEntity.id == pk)
        )
        await cls._require(statement, '实体类型不存在')

    @classmethod
    async def require_schema_entity_in_graph(
        cls, *, user_uuid: str, entity_uuid: str | None, schema_graph_uuid: str | None
    ) -> None:
        statement = (
            select(SchemaEntity.id)
            .join(SchemaGraph, SchemaEntity.schema_graph_uuid == SchemaGraph.uuid)
            .join(KgBase, SchemaGraph.kg_base_uuid == KgBase.uuid)
            .where(
                KgBase.user_uuid == user_uuid,
                SchemaEntity.uuid == entity_uuid,
                SchemaEntity.schema_graph_uuid == schema_graph_uuid,
            )
        )
        await cls._require(statement, '实体类型不存在')

    @classmethod
    async def require_schema_relationship(
        cls, *, user_uuid: str, uuid: str | None = None, pk: int | None = None
    ) -> None:
        statement = (
            select(SchemaRelationship.id)
            .join(SchemaGraph, SchemaRelationship.schema_graph_uuid == SchemaGraph.uuid)
            .join(KgBase, SchemaGraph.kg_base_uuid == KgBase.uuid)
            .where(KgBase.user_uuid == user_uuid)
        )
        statement = (
            statement.where(SchemaRelationship.uuid == uuid)
            if uuid is not None
            else statement.where(SchemaRelationship.id == pk)
        )
        await cls._require(statement, '关系类型不存在')

    @classmethod
    async def require_knowledge_entity(cls, *, user_uuid: str, uuid: str | None = None, pk: int | None = None) -> None:
        statement = (
            select(KnowledgeEntity.id)
            .join(KnowledgeGraph, KnowledgeEntity.knowledge_graph_uuid == KnowledgeGraph.uuid)
            .join(KgBase, KnowledgeGraph.kg_base_uuid == KgBase.uuid)
            .where(KgBase.user_uuid == user_uuid)
        )
        statement = (
            statement.where(KnowledgeEntity.uuid == uuid)
            if uuid is not None
            else statement.where(KnowledgeEntity.id == pk)
        )
        await cls._require(statement, '实体不存在')

    @classmethod
    async def require_knowledge_entity_in_graph(
        cls, *, user_uuid: str, entity_uuid: str | None, knowledge_graph_uuid: str | None
    ) -> None:
        statement = (
            select(KnowledgeEntity.id)
            .join(KnowledgeGraph, KnowledgeEntity.knowledge_graph_uuid == KnowledgeGraph.uuid)
            .join(KgBase, KnowledgeGraph.kg_base_uuid == KgBase.uuid)
            .where(
                KgBase.user_uuid == user_uuid,
                KnowledgeEntity.uuid == entity_uuid,
                KnowledgeEntity.knowledge_graph_uuid == knowledge_graph_uuid,
            )
        )
        await cls._require(statement, '实体不存在')

    @classmethod
    async def require_knowledge_relationship(
        cls, *, user_uuid: str, uuid: str | None = None, pk: int | None = None
    ) -> None:
        statement = (
            select(KnowledgeRelationship.id)
            .join(KnowledgeGraph, KnowledgeRelationship.knowledge_graph_uuid == KnowledgeGraph.uuid)
            .join(KgBase, KnowledgeGraph.kg_base_uuid == KgBase.uuid)
            .where(KgBase.user_uuid == user_uuid)
        )
        statement = (
            statement.where(KnowledgeRelationship.uuid == uuid)
            if uuid is not None
            else statement.where(KnowledgeRelationship.id == pk)
        )
        await cls._require(statement, '关系不存在')


ownership_service = OwnershipService()
