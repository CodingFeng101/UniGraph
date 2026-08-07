import json
import logging
from typing import Any

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from backend.common.core_layer.unigraph.ai_unit.llm.response_getter import GenericResponseGetter

# from ........app.core.config import settings
from ..structured_search.local_search.system_prompt import EXTRACT_ENTITIES_FROM_QUERY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def extract_entities_from_query(query, llm, api_key, base_url, model, max_retries=3) -> Any:
    """
    从查询中抽取实体

    :param query: 用户输入的问题
    :param llm: 大语言模型
    :param max_retries: 最大重试次数
    :return: 抽取的实体列表
    """
    extract_prompt = EXTRACT_ENTITIES_FROM_QUERY.render(query=query)

    for attempt in range(max_retries):
        try:
            extract_entities = await llm.get_response(
                query=extract_prompt, api_key=api_key, base_url=base_url, model=model
            )
            logger.debug(f'Attempt {attempt}: LLM response - {extract_entities}')
            extract_entities_list = json.loads(extract_entities)
            return extract_entities_list
        except json.JSONDecodeError as e:
            logger.error(f'Attempt {attempt}: Failed to parse JSON response - {e}')
            if attempt < max_retries - 1:
                continue
    return [f'{query}']


async def map_query_to_entities(extracted_entities, all_entities, api_key, base_url, model, k=10):
    embeder = GenericResponseGetter()
    if extracted_entities:
        entities_list = []
        for extracted_entity in extracted_entities:
            extracted_entity_embed = await embeder.get_vector(
                query=extracted_entity,
                api_key=api_key,
                base_url=base_url,
                model=model,
            )
            extracted_entity_embed = np.array(extracted_entity_embed)
            # 确保entity_embed是二维数组
            if extracted_entity_embed.ndim == 1:
                extracted_entity_embed = extracted_entity_embed.reshape(1, -1)
            similarities = []
            # 计算查询与所有实体之间的相似度
            for entity in all_entities:
                entity_embed = np.asarray(entity.attributes_embedding, dtype=float)
                if entity_embed.ndim == 0 or entity_embed.size == 0 or not np.isfinite(entity_embed).all():
                    continue

                # 确保entity_embed是二维数组
                if entity_embed.ndim == 1:
                    entity_embed = entity_embed.reshape(1, -1)
                if entity_embed.shape[1] != extracted_entity_embed.shape[1]:
                    continue

                similarity = cosine_similarity(extracted_entity_embed, entity_embed)[0][0]
                similarities.append((entity, similarity))
            entities_list.extend(similarities)
        if not entities_list:
            normalized_queries = [str(item).strip().lower() for item in extracted_entities if str(item).strip()]
            lexical_matches = [
                entity
                for entity in all_entities
                if any(
                    query in str(getattr(entity, 'name', '')).lower()
                    or str(getattr(entity, 'name', '')).lower() in query
                    for query in normalized_queries
                )
            ]
            return lexical_matches[:k] or list(all_entities)[:k]

        entities_list.sort(key=lambda x: x[1], reverse=True)
        top_k_entities = [entity for entity, similarity in entities_list[:k]]
        unique_top_k_entities = list({entity.id: entity for entity in top_k_entities}.values())

        return unique_top_k_entities
    return []
