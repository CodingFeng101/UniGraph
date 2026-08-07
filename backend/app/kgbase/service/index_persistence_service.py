from __future__ import annotations

import json
from collections.abc import Callable

from sqlalchemy import delete, insert, select

from backend.app.kgbase.model import Community, Embedding, KnowledgeEntity, community_entity_map
from backend.database.db_mysql import async_db_session, uuid4_str
from backend.utils.timezone import timezone

ProgressCallback = Callable[[str, int, int], None]


def _chunks(values: list[dict], size: int = 250):
    for start in range(0, len(values), size):
        yield values[start : start + size]


def _text(value) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value if value is not None else {}, ensure_ascii=False)


class IndexPersistenceService:
    @staticmethod
    async def replace(
        *,
        knowledge_graph_uuid: str,
        community_reports: list[dict],
        entities: list[dict],
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        async with async_db_session.begin() as db:
            created_time = timezone.now()
            await db.execute(delete(Community).where(Community.knowledge_graph_uuid == knowledge_graph_uuid))

            community_values = []
            external_to_uuid = {}
            for report in community_reports:
                community_uuid = uuid4_str()
                external_to_uuid[str(report.get('id'))] = community_uuid
                community_values.append({
                    'uuid': community_uuid,
                    'knowledge_graph_uuid': knowledge_graph_uuid,
                    'title': _text(report.get('title', '')),
                    'content': _text(report.get('full_content', '')),
                    'level': _text(report.get('level', '')),
                    'rating': _text(report.get('rating', '')),
                    'attributes': _text(report.get('attributes', '')),
                    'created_time': created_time,
                })

            completed = 0
            for batch in _chunks(community_values):
                await db.execute(insert(Community), batch)
                completed += len(batch)
                if progress_callback:
                    progress_callback('communities', completed, len(community_values))

            community_id_by_external = {}
            if external_to_uuid:
                rows = await db.execute(
                    select(Community.id, Community.uuid).where(Community.uuid.in_(external_to_uuid.values()))
                )
                database_id_by_uuid = {uuid: database_id for database_id, uuid in rows}
                community_id_by_external = {
                    external_id: database_id_by_uuid[uuid] for external_id, uuid in external_to_uuid.items()
                }

            entity_uuids = [str(entity.get('id')) for entity in entities if entity.get('id')]
            entity_rows = await db.execute(
                select(KnowledgeEntity.id, KnowledgeEntity.uuid).where(KnowledgeEntity.uuid.in_(entity_uuids))
            )
            entity_id_by_uuid = {uuid: database_id for database_id, uuid in entity_rows}
            missing_entities = sorted(set(entity_uuids) - set(entity_id_by_uuid))
            if missing_entities:
                raise RuntimeError(f'索引包含 {len(missing_entities)} 个数据库中不存在的实体')

            if entity_uuids:
                await db.execute(delete(Embedding).where(Embedding.knowledge_entity_uuid.in_(entity_uuids)))

            embedding_values = [
                {
                    'uuid': uuid4_str(),
                    'knowledge_entity_uuid': str(entity['id']),
                    'vector': json.dumps(entity.get('attributes_embedding') or []),
                    'created_time': created_time,
                }
                for entity in entities
                if entity.get('id')
            ]
            completed = 0
            for batch in _chunks(embedding_values):
                await db.execute(insert(Embedding), batch)
                completed += len(batch)
                if progress_callback:
                    progress_callback('embeddings', completed, len(embedding_values))

            relationship_values = []
            seen_relations = set()
            for entity in entities:
                entity_uuid = str(entity.get('id') or '')
                entity_id = entity_id_by_uuid.get(entity_uuid)
                for external_community_id in entity.get('community_ids') or []:
                    community_id = community_id_by_external.get(str(external_community_id))
                    relation = (community_id, entity_id)
                    if not community_id or not entity_id or relation in seen_relations:
                        continue
                    seen_relations.add(relation)
                    relationship_values.append({
                        'community_id': community_id,
                        'knowledge_entity_id': entity_id,
                    })

            completed = 0
            for batch in _chunks(relationship_values):
                await db.execute(insert(community_entity_map), batch)
                completed += len(batch)
                if progress_callback:
                    progress_callback('relations', completed, len(relationship_values))


index_persistence_service = IndexPersistenceService()
