from typing import Any, cast

import pandas as pd

from ...index.graph.graph_parse import KGProcessor
from ...utils import num_tokens


def build_entity_context(
    selected_entities,
    human_read_id: int,
    token_encoder,
    context_name='Entities',
    column_delimiter: str = '|',
    max_tokens: int = 8000,
):
    """
    构建实体上下文

    :param selected_entities: 匹配到的实体列表
    :param human_read_id: 人类可读的ID
    :param token_encoder: token编码器
    :param context_name: 上下文名称
    :param column_delimiter: 列分隔符
    :param max_tokens: 最大token数
    :return: 上下文文本，上下文数据，人类可读的ID
    """
    # 添加上下文标题
    current_context_text = f'-----{context_name}-----' + '\n'
    current_token = 0

    # 添加表头
    header = ['id', 'entity_type', 'entity_name', 'text']
    current_context_text += column_delimiter.join(header) + '\n'
    all_context_records = [header]

    # 依据匹配的实体列表中实体的顺序进行排序
    for entity in selected_entities:
        entity.attributes['name'] = entity.name
        attributes = ' '.join([
            f'{k}: {v}' for k, v in KGProcessor.remove_unrelated_attributes(entity.attributes).items()
        ])
        new_context = [str(human_read_id), entity.type, entity.name, attributes]

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
