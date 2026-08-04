import asyncio
import logging

import numpy as np
from tqdm.asyncio import tqdm_asyncio

from .....ai_unit.llm.response_getter import GenericResponseGetter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AttributeEmbedder:
    def __init__(self, max_concurrent=100):
        self.semaphore = asyncio.Semaphore(max_concurrent)  # 控制并发量

    @staticmethod
    async def embed_attributes(text_embeder, attributes, api_key, base_url, model):
        """
        带指数退避重试的嵌入方法

        :param text_embeder: 文本嵌入器
        :param attributes: 实体的属性字典
        :return: 嵌入向量
        """
        max_retries = 3
        backoff_factor = 1

        for attempt in range(max_retries):
            try:
                attributes_text = ' '.join(f'{k}: {v}' for k, v in attributes.items())
                response = await text_embeder.get_vector(
                    query=attributes_text,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                )
                logger.info(f'Embedding generated successfully: {attributes_text}')
                return np.array(response)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f'Embedding generation failed: {str(e)}')
                    raise
                await asyncio.sleep(backoff_factor * (2**attempt))
        return np.array([])

    async def _process_single_entity(self, index, entity, embeder, api_key, base_url, model):
        """
        处理单个实体的异步任务

        :param index: 实体的索引
        :param entity: 实体对象
        :return: 实体索引和可能的错误
        """
        async with self.semaphore:  # 控制并发量
            try:
                # 创建属性副本避免修改原始数据
                attributes = entity.attributes.copy()
                attributes['name'] = entity.name

                # 获取嵌入向量
                vector = await AttributeEmbedder.embed_attributes(embeder, attributes, api_key, base_url, model)

                # 更新实体数据
                entity.attributes_embedding = vector.tolist()
                return index, None
            except Exception as e:
                return index, e
            finally:
                del attributes['name']

    async def add_attribute_vectors(self, entities, api_key, base_url, model, progress_callback=None):
        """
        并发处理所有实体

        :param entities: 实体列表
        :return: 处理后的实体列表
        """
        # 创建任务列表
        embeder = GenericResponseGetter()
        tasks = [
            self._process_single_entity(idx, entity, embeder, api_key, base_url, model)
            for idx, entity in enumerate(entities)
        ]

        # 使用带进度条的并发执行
        progress_bar = tqdm_asyncio.as_completed(tasks, desc='嵌入实体')

        completed = 0
        total = len(tasks)
        failures = []
        for future in progress_bar:
            index, error = await future
            completed += 1
            if error:
                failures.append((index, error))
                logger.error(f'Error processing entity {index}: {str(error)}')
            if progress_callback:
                progress_callback(completed, total, entities[index], error)

        if failures:
            raise RuntimeError(f'{len(failures)}/{total} 个实体向量生成失败，请检查嵌入模型配置')

        return entities
