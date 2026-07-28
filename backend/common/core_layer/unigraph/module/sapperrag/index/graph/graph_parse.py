import json

from ...model.entity import Entity
from ...model.relationship import Relationship


class KGProcessor:
    def __init__(self):
        self.source = None
        self.entity_dict = {}

    def process_entity(self, entity_data: dict) -> str:
        """
        处理实体，分配 UUID（如果尚未处理），并返回实体 ID

        :param entity_data: 实体数据
        :return: 实体 ID
        """
        entity_key = json.dumps(entity_data, sort_keys=True, ensure_ascii=False)
        if entity_key not in self.entity_dict:
            self.entity_dict[entity_key] = {
                'id': entity_data.get('id'),
                'attributes': KGProcessor.remove_unrelated_attributes(entity_data.get('Attributes')),  # 去除垃圾属性
                'name': entity_data.get('Name'),
                'type': entity_data.get('Type'),
            }
        return self.entity_dict[entity_key]['id']

    def process_data(self, kg_data) -> tuple:
        """处理数据，将实体和关系存储到各自的列表中"""
        relations = []
        for item in kg_data:
            directional_entity = item.get('DirectionalEntity')
            directed_entity = item.get('DirectedEntity')
            relation = item.get('Relation')

            source_id = self.process_entity(directional_entity) if directional_entity else None
            target_id = self.process_entity(directed_entity) if directed_entity else None

            if relation:
                relations.append(
                    Relationship(
                        id=relation.get('id'),
                        source=source_id,
                        target=target_id,
                        type=relation.get('Type'),
                        name=relation.get('Name'),
                        attributes=relation.get('Attributes', {}),
                    )
                )

        entities = [Entity.from_dict(entity_data) for entity_data in self.entity_dict.values()]
        return entities, relations

    @staticmethod
    def remove_unrelated_attributes(attributes: dict) -> dict:
        attributes = {
            key: value
            for key, value in attributes.items()
            if key != 'index' and (isinstance(value, str) and value.lower() != 'unknown')
        }
        return attributes


def transform_data(entities, relationships):
    """
    将实体和关系数据转换为特定格式。

    :param entities: 实体数据列表
    :param relationships: 关系数据列表
    """
    entity_dict = {e['uuid']: e for e in entities}
    transformed_data = []

    for rel in relationships:
        directional_entity = entity_dict.get(rel['source_entity_uuid'], {})
        directed_entity = entity_dict.get(rel['target_entity_uuid'], {})
        transformed_item = {
            'DirectionalEntity': {
                'id': directional_entity.get('uuid', 'Unknown'),
                'Type': directional_entity.get('type', 'Unknown'),
                'Name': directional_entity.get('name', 'Unknown'),
                'Attributes': json.loads(directional_entity.get('attributes', '{}')),
            },
            'Relation': {
                'id': rel.get('uuid', 'Unknown'),
                'Type': rel.get('type', 'Unknown'),
                'Name': rel.get('name', 'Unknown'),
            },
            'DirectedEntity': {
                'id': directed_entity.get('uuid', 'Unknown'),
                'Type': directed_entity.get('type', 'Unknown'),
                'Name': directed_entity.get('name', 'Unknown'),
                'Attributes': json.loads(directed_entity.get('attributes', '{}')),
            },
        }
        transformed_data.append(transformed_item)

    return transformed_data
