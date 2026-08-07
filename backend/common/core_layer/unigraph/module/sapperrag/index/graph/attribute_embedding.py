import asyncio
import logging

from backend.core.conf import settings

from .....ai_unit.llm.response_getter import GenericResponseGetter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AttributeEmbedder:
    def __init__(self, max_concurrent: int | None = None, batch_size: int | None = None):
        self.semaphore = asyncio.Semaphore(max_concurrent or settings.EMBEDDING_BATCH_CONCURRENCY)
        self.batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE

    @staticmethod
    def attributes_text(entity) -> str:
        attributes = dict(entity.attributes or {})
        attributes['name'] = entity.name
        return ' '.join(f'{key}: {value}' for key, value in attributes.items())

    async def _request_vectors(self, texts, api_key, base_url, model):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return await GenericResponseGetter.get_vectors(
                    queries=texts,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                )
            except Exception:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)
        return []

    async def _embed_with_split(self, texts, api_key, base_url, model):
        try:
            return await self._request_vectors(texts, api_key, base_url, model)
        except Exception:
            if len(texts) <= 1:
                raise
            middle = len(texts) // 2
            left, right = await asyncio.gather(
                self._embed_with_split(texts[:middle], api_key, base_url, model),
                self._embed_with_split(texts[middle:], api_key, base_url, model),
            )
            return [*left, *right]

    async def _process_batch(self, batch, api_key, base_url, model):
        async with self.semaphore:
            indexes = [index for index, _ in batch]
            texts = [self.attributes_text(entity) for _, entity in batch]
            vectors = await self._embed_with_split(texts, api_key, base_url, model)
            if len(vectors) != len(batch):
                raise RuntimeError(f'嵌入模型返回 {len(vectors)} 个向量，预期 {len(batch)} 个')
            return indexes, vectors

    async def add_attribute_vectors(self, entities, api_key, base_url, model, progress_callback=None):
        batches = [
            list(enumerate(entities))[start : start + self.batch_size]
            for start in range(0, len(entities), self.batch_size)
        ]
        tasks = [self._process_batch(batch, api_key, base_url, model) for batch in batches]
        completed = 0
        total = len(entities)
        failures = []

        for future in asyncio.as_completed(tasks):
            try:
                indexes, vectors = await future
                for index, vector in zip(indexes, vectors, strict=True):
                    entities[index].attributes_embedding = list(vector)
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, entities[index], None)
            except Exception as error:
                failures.append(error)
                logger.error('Embedding batch failed: %s', error)

        if failures:
            raise RuntimeError(f'{len(failures)} 个向量批次生成失败，请检查嵌入模型配置') from failures[0]

        return entities
