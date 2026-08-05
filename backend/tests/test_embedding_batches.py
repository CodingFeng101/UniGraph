import _env  # noqa: F401  # isort: skip
import asyncio
from types import SimpleNamespace

from backend.common.core_layer.unigraph.module.sapperrag.index.graph.attribute_embedding import AttributeEmbedder


def _entities(count: int):
    return [
        SimpleNamespace(name=f'entity-{index}', attributes={'kind': 'test'}, attributes_embedding=[])
        for index in range(count)
    ]


def test_entities_are_embedded_in_batches() -> None:
    class FakeEmbedder(AttributeEmbedder):
        def __init__(self):
            super().__init__(max_concurrent=1, batch_size=2)
            self.batch_lengths = []

        async def _request_vectors(self, texts, api_key, base_url, model):
            self.batch_lengths.append(len(texts))
            return [[float(index)] for index, _ in enumerate(texts)]

    embedder = FakeEmbedder()
    entities = _entities(5)
    result = asyncio.run(embedder.add_attribute_vectors(entities, 'key', 'url', 'model'))

    assert sorted(embedder.batch_lengths) == [1, 2, 2]
    assert all(entity.attributes_embedding for entity in result)


def test_failed_large_batch_is_split_without_skipping_entities() -> None:
    class SplittingEmbedder(AttributeEmbedder):
        def __init__(self):
            super().__init__(max_concurrent=1, batch_size=4)

        async def _request_vectors(self, texts, api_key, base_url, model):
            if len(texts) > 1:
                raise RuntimeError('provider batch limit')
            return [[1.0]]

    entities = _entities(4)
    result = asyncio.run(SplittingEmbedder().add_attribute_vectors(entities, 'key', 'url', 'model'))

    assert [entity.attributes_embedding for entity in result] == [[1.0], [1.0], [1.0], [1.0]]
