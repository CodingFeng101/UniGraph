from types import SimpleNamespace

import pytest
from backend.app.admin.service.llm_model_service import LlmModelService
from backend.app.kgbase.schema.knowledge_graph import AskKnowledgeGraphParam
from backend.common.core_layer.unigraph.ai_unit.llm.response_getter import GenericResponseGetter
from backend.common.core_layer.unigraph.module.sapperrag.retriver.context_builder.entity_extraction import (
    map_query_to_entities,
)
from backend.common.core_layer.unigraph.module.schema_construction.related_retrieve import batch_get_vectors


class _ExistingEmbeddingResult:
    @staticmethod
    def scalar_one_or_none():
        return 'existing-model-uuid'


class _EmbeddingDatabase:
    async def execute(self, _statement):
        return _ExistingEmbeddingResult()


@pytest.mark.asyncio
async def test_second_embedding_model_is_rejected() -> None:
    with pytest.raises(ValueError, match='每个用户只能配置一个嵌入模型'):
        await LlmModelService._ensure_single_embedding(
            _EmbeddingDatabase(),
            user_uuid='user-uuid',
        )


def test_qa_request_accepts_selected_llm_uuid() -> None:
    request = AskKnowledgeGraphParam(
        message='什么是知识图谱',
        user_token='token',
        llm_model_uuid='model-uuid',
    )

    assert request.llm_model_uuid == 'model-uuid'


@pytest.mark.asyncio
async def test_query_entity_embedding_uses_configured_embedding_model(monkeypatch) -> None:
    captured = {}

    async def fake_get_vector(self, *, query, api_key, base_url, model):
        captured.update(query=query, api_key=api_key, base_url=base_url, model=model)
        return [1.0, 0.0]

    monkeypatch.setattr(GenericResponseGetter, 'get_vector', fake_get_vector)
    entity = SimpleNamespace(id='entity-1', attributes_embedding=[1.0, 0.0])

    selected = await map_query_to_entities(
        ['测试实体'],
        [entity],
        'embedding-key',
        'https://embedding.example/v1',
        'text-embedding-model',
    )

    assert selected == [entity]
    assert captured == {
        'query': '测试实体',
        'api_key': 'embedding-key',
        'base_url': 'https://embedding.example/v1',
        'model': 'text-embedding-model',
    }


@pytest.mark.asyncio
async def test_query_entity_embedding_skips_invalid_stored_vectors(monkeypatch) -> None:
    async def fake_get_vector(self, *, query, api_key, base_url, model):
        return [1.0, 0.0]

    monkeypatch.setattr(GenericResponseGetter, 'get_vector', fake_get_vector)
    invalid = SimpleNamespace(id='invalid', name='无效实体', attributes_embedding=float('nan'))
    valid = SimpleNamespace(id='valid', name='有效实体', attributes_embedding=[1.0, 0.0])

    selected = await map_query_to_entities(
        ['有效实体'],
        [invalid, valid],
        'embedding-key',
        'https://embedding.example/v1',
        'text-embedding-model',
    )

    assert selected == [valid]


@pytest.mark.asyncio
async def test_schema_semantic_merge_uses_configured_embedding_model(monkeypatch) -> None:
    captured = []

    async def fake_get_vector(*, query, api_key, base_url, model):
        captured.append((query, api_key, base_url, model))
        return [1.0, 0.0]

    monkeypatch.setattr(GenericResponseGetter, 'get_vector', fake_get_vector)

    vectors = await batch_get_vectors(
        ['Person', 'Organization'],
        api_key='embedding-key',
        base_url='https://embedding.example/v1',
        model='embedding-model',
    )

    assert list(vectors) == ['Person', 'Organization']
    assert captured == [
        ('Person', 'embedding-key', 'https://embedding.example/v1', 'embedding-model'),
        ('Organization', 'embedding-key', 'https://embedding.example/v1', 'embedding-model'),
    ]
