from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import tiktoken

from ....retriver.context_builder.builders import LocalContextBuilder
from ....retriver.context_builder.community_context import build_community_context
from ....retriver.context_builder.entity_context import build_entity_context
from ....retriver.context_builder.entity_extraction import map_query_to_entities
from ....retriver.context_builder.relationship_context import build_relationship_context
from ....retriver.context_builder.source_context import build_source_context

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LocalSearchMixedContext(LocalContextBuilder):
    def __init__(self, entities, relationships, community_reports):
        self.entities = entities
        self.relationships = relationships
        self.community_reports = community_reports

    async def build_context(
        self, extracted_entities: list, level: int, infer: bool, api_key: str, base_url: str, **kwargs: Any
    ) -> Any:
        """
        构建查询上下文

        :param extracted_entities: 抽取到的实体列表
        :param level: 查询深度
        :param infer: 是否进行推理
        :param kwargs: 其他参数
        """
        token_encoder = tiktoken.get_encoding('cl100k_base')
        selected_entities = await map_query_to_entities(extracted_entities, self.entities, api_key, base_url, k=10)
        logger.info('已匹配到实体😊')

        human_read_id = 0  # 用于替换复杂的ID,方便模型溯源
        final_context = list[str]()
        final_context_data = dict[str, pd.DataFrame]()

        community_context, community_context_data, human_read_id = build_community_context(
            self.community_reports,
            selected_entities=selected_entities,
            token_encoder=token_encoder,
            human_read_id=human_read_id,
            user_level=level,
            infer=infer,
        )

        if community_context.strip() != '':
            final_context.append(str(community_context))
            final_context_data['Reports'] = community_context_data
        logger.info('社区文本已检索完成😊')

        entity_context, entity_context_data, human_read_id = build_entity_context(
            selected_entities, token_encoder=token_encoder, human_read_id=human_read_id
        )

        if entity_context.strip() != '':
            final_context.append(str(entity_context))
            final_context_data['Entities'] = entity_context_data
        logger.info('实体文本已检索完成😊')

        selected_relationships, relationship_context, relationship_context_data, human_read_id = (
            build_relationship_context(
                selected_entities=selected_entities,
                token_encoder=token_encoder,
                relationships=self.relationships,
                entities=self.entities,
                human_read_id=human_read_id,
            )
        )

        if relationship_context.strip() != '':
            final_context.append(str(relationship_context))
            final_context_data['Relationships'] = relationship_context_data
        logger.info('关系文本已检索完成😊')

        source_context, source_context_data, human_read_id = build_source_context(
            selected_relationships=selected_relationships, token_encoder=token_encoder, human_read_id=human_read_id
        )

        if source_context.strip() != '':
            final_context.append(str(source_context))
            final_context_data['Sources'] = source_context_data
        logger.info('来源文本已检索完成😊')

        return '\n\n'.join(final_context), final_context_data
