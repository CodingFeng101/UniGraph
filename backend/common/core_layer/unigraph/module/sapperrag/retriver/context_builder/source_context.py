from typing import Any, cast

import pandas as pd

from ...model.relationship import Relationship
from ...utils import num_tokens


def build_source_context(
    selected_relationships: list[Relationship],
    human_read_id: int,
    token_encoder,
    column_delimiter: str = '|',
    max_tokens: int = 8000,
    context_name: str = 'Sources',
):
    """
    构建信息源上下文

    :param selected_relationships: 匹配到的关系列表
    :param human_read_id: 用于替换复杂的ID,方便模型溯源
    :param token_encoder: 分词器
    :param column_delimiter: 列分隔符
    :param max_tokens: 最大token数
    :param context_name: 上下文名称
    :return: 上下文文本, 上下文数据, human_read_id
    """
    if selected_relationships is None or len(selected_relationships) == 0:
        return '', {}, human_read_id
    # 添加上下文标题
    current_context_text = f'-----{context_name}-----' + '\n'
    current_token = 0

    # 添加表头
    header = ['id', 'text']
    current_context_text += column_delimiter.join(header) + '\n'
    all_context_records = [header]

    select_triple_sources = set()
    select_triple_sources.update(
        relationship.triple_source for relationship in selected_relationships if relationship.triple_source
    )

    # 提取每个实体对应的三元组的信息源
    for unit in select_triple_sources:
        new_context = [str(human_read_id), unit]
        new_context_text = column_delimiter.join(new_context) + '\n'

        current_context_text += new_context_text
        all_context_records.append(new_context)
        human_read_id += 1
        current_token += num_tokens(current_context_text, token_encoder)
        if current_token >= max_tokens:
            break

    if len(all_context_records) > 1:
        record_df = pd.DataFrame(all_context_records[1:], columns=cast('Any', all_context_records[0]))
    else:
        record_df = pd.DataFrame()

    return current_context_text, record_df, human_read_id
