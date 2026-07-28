from typing import Any, Dict, List

from backend.common.core_layer.unigraph.module.sapperrag.index.graph.cli import GraphIndexer
from backend.common.core_layer.unigraph.module.sapperrag.index.graph.graph_parse import KGProcessor, transform_data
from backend.common.core_layer.unigraph.module.sapperrag.retriver.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
from backend.common.core_layer.unigraph.module.sapperrag.retriver.structured_search.local_search.search import (
    LocalSearch,
    logger,
)
from backend.common.core_layer.unigraph.module.sapperrag.retriver.structured_search.local_search.system_prompt import (
    LOCAL_SEARCH_SYSTEM_PROMPT,
)


async def build_index(
    entities: List[Dict[str, Any]],
    relationships: List[Dict[str, Any]],
    level: int,
    api_key: str,
    base_url: str,
    model: str,
    progress_callback=None,
) -> tuple:
    """
    构建局部与全局索引用于问答

    : param entities: 实体列表
    : param relationships: 关系列表
    : param level: 索引深度
    : return: 实体列表, 社区报告列表
    """
    # 将实体和关系转换为KG格式(这里是一个格式的转换器)
    kg_data = transform_data(entities, relationships)
    logger.info('KG数据转换成功😊')

    # 对实体和关系的解析从KG中
    kg_processor = KGProcessor()
    entities, relationships = kg_processor.process_data(kg_data)
    logger.info('KG数据解析成功😊')

    # 构建索引
    indexer = GraphIndexer()
    entities, community_reports = await indexer.build_index(
        entities, relationships, level, api_key, base_url, model, progress_callback=progress_callback
    )
    logger.info('索引构建成功😊')
    return entities, community_reports


async def query_kg(
    query: str,
    entities: list,
    relationships: list,
    community_reports: list,
    level: int,
    infer: bool = False,
    api_key: str = '',
    base_url: str = '',
    model: str = '',
) -> tuple:
    """
    初始化搜索器

    :param query: 用户输入的问题
    :param entities: 实体列表
    :param relationships: 关系列表
    :param community_reports: 社区报告列表
    :param level: 查询深度
    :param infer: 是否进行推理
    :return: 查询结果
    """
    context_builder = LocalSearchMixedContext(entities, relationships, community_reports)
    search_engine = LocalSearch(context_builder, LOCAL_SEARCH_SYSTEM_PROMPT)
    logger.info('搜索器初始化成功😊')
    results = await search_engine.search(query, level, infer, api_key, base_url, model)
    logger.info(f'上下文:{results}😊')

    return results, search_engine.context_text, search_engine.context_data
