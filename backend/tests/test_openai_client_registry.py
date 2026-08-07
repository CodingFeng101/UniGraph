import _env  # noqa: F401  # isort: skip
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from backend.common.clients.openai_client_registry import OpenAIClientRegistry
from backend.common.core_layer.unigraph.ai_unit.llm import response_getter as response_getter_module
from backend.common.core_layer.unigraph.ai_unit.llm.response_getter import GenericResponseGetter


class _FakeClient:
    def __init__(self) -> None:
        self.close = AsyncMock()


def test_registry_reuses_clients_and_closes_lru_entry(monkeypatch) -> None:
    created = []

    def create_client(_api_key, _base_url):
        client = _FakeClient()
        created.append(client)
        return client

    monkeypatch.setattr(OpenAIClientRegistry, '_create_client', staticmethod(create_client))
    registry = OpenAIClientRegistry(max_clients=2)

    async def scenario():
        first = await registry.get(api_key='secret-one', base_url='https://example.com/v1/')
        repeated = await registry.get(api_key='secret-one', base_url='https://example.com/v1')
        await registry.get(api_key='secret-two', base_url='https://example.com/v1')
        await registry.get(api_key='secret-three', base_url='https://example.com/v1')
        return first, repeated

    first, repeated = asyncio.run(scenario())

    assert first is repeated
    assert len(created) == 3
    created[0].close.assert_awaited_once()
    assert registry.size == 2


def test_batch_vectors_are_restored_to_input_order(monkeypatch) -> None:
    completion = SimpleNamespace(
        data=[
            SimpleNamespace(index=1, embedding=[2.0]),
            SimpleNamespace(index=0, embedding=[1.0]),
        ]
    )
    client = SimpleNamespace(embeddings=SimpleNamespace(create=AsyncMock(return_value=completion)))
    monkeypatch.setattr(response_getter_module.openai_client_registry, 'get', AsyncMock(return_value=client))

    vectors = asyncio.run(
        GenericResponseGetter.get_vectors(
            queries=['first', 'second'],
            model='embedding-model',
            api_key='test-key',
            base_url='https://example.com/v1',
        )
    )

    assert vectors == [[1.0], [2.0]]
    client.embeddings.create.assert_awaited_once_with(model='embedding-model', input=['first', 'second'])
