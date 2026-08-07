import _env  # noqa: F401  # isort: skip

import asyncio

import pytest
from backend.app.kgbase.service import index_persistence_service as module


class _Rows(list):
    pass


class _Transaction:
    def __init__(self, session):
        self.session = session
        self.exception_type = None

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exception_type, _exception, _traceback):
        self.exception_type = exception_type


class _SessionFactory:
    def __init__(self, session):
        self.transaction = _Transaction(session)

    def begin(self):
        return self.transaction


class _Session:
    def __init__(self, entity_ids, fail_on_embedding_batch=None):
        self.entity_ids = entity_ids
        self.community_batches = []
        self.embedding_batches = []
        self.fail_on_embedding_batch = fail_on_embedding_batch

    async def execute(self, statement, values=None):
        sql = str(statement)
        if sql.startswith('SELECT') and 'knowledge_entity' in sql:
            return _Rows((index + 1, entity_uuid) for index, entity_uuid in enumerate(self.entity_ids))
        if sql.startswith('SELECT') and 'community' in sql:
            communities = [item for batch in self.community_batches for item in batch]
            return _Rows((index + 1, item['uuid']) for index, item in enumerate(communities))
        if values and getattr(getattr(statement, 'table', None), 'name', None) == 'community':
            self.community_batches.append(values)
        if values and getattr(getattr(statement, 'table', None), 'name', None) == 'uni_embedding':
            self.embedding_batches.append(values)
            if len(self.embedding_batches) == self.fail_on_embedding_batch:
                raise RuntimeError('database write failed')
        return _Rows()


def _entities(count):
    return [
        {'id': f'entity-{index}', 'attributes_embedding': [float(index)], 'community_ids': []} for index in range(count)
    ]


def test_embeddings_are_written_in_bounded_batches(monkeypatch) -> None:
    entities = _entities(501)
    session = _Session([entity['id'] for entity in entities])
    session_factory = _SessionFactory(session)
    monkeypatch.setattr(module, 'async_db_session', session_factory)

    asyncio.run(
        module.index_persistence_service.replace(
            knowledge_graph_uuid='graph-id',
            community_reports=[],
            entities=entities,
        )
    )

    assert [len(batch) for batch in session.embedding_batches] == [250, 250, 1]
    assert all(item.get('created_time') is not None for batch in session.embedding_batches for item in batch)
    assert session_factory.transaction.exception_type is None


def test_communities_are_written_with_a_creation_time(monkeypatch) -> None:
    session = _Session([])
    session_factory = _SessionFactory(session)
    monkeypatch.setattr(module, 'async_db_session', session_factory)

    asyncio.run(
        module.index_persistence_service.replace(
            knowledge_graph_uuid='graph-id',
            community_reports=[{'id': 'community-1', 'title': '社区报告'}],
            entities=[],
        )
    )

    assert len(session.community_batches) == 1
    assert session.community_batches[0][0].get('created_time') is not None
    assert session_factory.transaction.exception_type is None


def test_batch_failure_leaves_the_transaction_to_roll_back(monkeypatch) -> None:
    entities = _entities(251)
    session = _Session([entity['id'] for entity in entities], fail_on_embedding_batch=2)
    session_factory = _SessionFactory(session)
    monkeypatch.setattr(module, 'async_db_session', session_factory)

    with pytest.raises(RuntimeError, match='database write failed'):
        asyncio.run(
            module.index_persistence_service.replace(
                knowledge_graph_uuid='graph-id',
                community_reports=[],
                entities=entities,
            )
        )

    assert session_factory.transaction.exception_type is RuntimeError
