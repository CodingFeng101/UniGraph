import json
import logging

import pandas as pd

from ..model.community import Community
from ..model.entity import Entity
from ..model.relationship import Relationship

logger = logging.getLogger(__name__)


def load_entities(csv_file_path: str = None, communities=None, entities=None, df: pd.DataFrame = None) -> list:
    """
    从 CSV 文件或 DataFrame 加载实体

    :param csv_file_path: CSV 文件路径
    :param communities: 社区列表
    :param entities: 实体列表
    :param df: DataFrame
    :return: 实体列表
    """
    if communities is None:
        if df is None:
            df = pd.read_csv(csv_file_path)

        dataclass_list = []
        try:
            for _, row in df.iterrows():
                dataclass_list.append(
                    Entity(
                        id=row.get('id', ''),
                        type=row.get('type', ''),
                        name=row.get('name', ''),
                        community_ids=row.get('community_ids', ''),
                        attributes=json.loads(row['attributes'].replace("'", '"'))
                        if isinstance(row['attributes'], str)
                        else row.get('attributes', ''),
                        attributes_embedding=json.loads(row['attributes_embedding'])
                        if isinstance(row['attributes_embedding'], str)
                        else row.get('attributes_embedding', []),
                    )
                )
        except json.JSONDecodeError:
            logger.warning('Skipped entity rows with invalid JSON', exc_info=True)

        return dataclass_list
    # 这种情况主要是为了存入社区与社区内实体的对应关系
    else:
        entity_to_communities = {entity.id: [] for entity in entities}

        for community in communities:
            for community_entity_id in community.entity_ids:
                if community_entity_id in entity_to_communities:
                    entity_to_communities[community_entity_id].append(community.id)

        for entity in entities:
            entity.community_ids = entity_to_communities[entity.id]

    return entities


def load_relationships(csv_file_path: str = None, df: pd.DataFrame = None) -> list:
    """
    从 CSV 文件或 DataFrame 加载关系

    :param csv_file_path: CSV 文件路径
    :param df: DataFrame
    :return: 关系列表
    """
    if df is None:
        df = pd.read_csv(csv_file_path)

    dataclass_list = []
    for _, row in df.iterrows():
        dataclass_list.append(
            Relationship(
                id=row.get('id', ''),
                source=row.get('source', ''),
                target=row.get('target', ''),
                type=row.get('type', ''),
                name=row.get('name', ''),
                attributes=row.get('attributes', ''),
                triple_source=row.get('triple_source', ''),
            )
        )
    return dataclass_list


def load_community(csv_file_path: str = None, df: pd.DataFrame = None) -> list:
    """
    从 CSV 文件或 DataFrame 加载社区

    :param csv_file_path: CSV 文件路径
    :param df: DataFrame
    :return: 社区列表
    """
    if df is None:
        df = pd.read_csv(csv_file_path)

    dataclass_list = []
    for _, row in df.iterrows():
        dataclass_list.append(
            Community(
                id=row.get('id', ''),
                title=row.get('title', ''),
                level=row.get('level', ''),
                entity_ids=row.get('entity_ids', []),
                rating=row.get('rating', ''),
                full_content=row.get('full_content', ''),
            )
        )
    return dataclass_list
