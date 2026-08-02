import logging

from .base_parser import ResponseParser

logger = logging.getLogger(__name__)


class EntityExtractionResponseParser(ResponseParser):
    @staticmethod
    def parse(response: str, **kwargs) -> dict:
        """
        解析实体及其类型提取的字符串
        :param response: 实体及其类型提取的字符串 -> e1: t1; e2: t2; e3: t3; ...
        :return: 解析后的实体类型字典 -> {e1: t1, e2: t2, e3: t3, ...}
        """
        # 去除转义字符 \n 和 \t
        entity_type_string = response.replace('\n', '').replace('\t', '')

        # 按照 ", " 分割字符串为条目列表
        entries = [entry.strip() for entry in entity_type_string.split(', ') if entry.strip()]

        # 创建一个空字典来存储解析结果
        entity_type_dict = {}

        # 迭代每一个条目并拆分为键值对
        for entry in entries:
            try:
                if ':' in entry:
                    entity, entity_type = entry.split(':', 1)
                    entity = entity.strip()
                    entity_type = entity_type.strip()
                    entity_type_dict[entity] = entity_type
            except (TypeError, ValueError):
                continue

        return entity_type_dict


class RelationExtractionResponseParser(ResponseParser):
    @staticmethod
    def parse(response: str, **kwargs):
        """
        解析关系三元组提取的字符串
        :param response: 关系三元组提取的字符串 -> (实体1(实体类型1), 关系, 实体2(实体类型2))=>'源文本'; ...
        :param entity_type_dict: 实体及其类型字典 -> {实体1: 实体类型1, 实体2: 实体类型2, ...}
        :return: 解析后的三元组字典 -> {(实体1, 关系, 实体2): (实体类型1, 关系类型, 实体类型2), ...}
                 提取的实体列表 -> [实体1, 实体2, ...]
                 提取的源文本字典 -> {实体1-关系-实体2: 源文本, ...}
        """

        entity_type_dict = kwargs.get('entity_type_dict', {})

        # 去除转义字符 \n 和 \t
        triples_string = response.replace('\n', '').replace('\t', '')

        # 使用 "&&" 分隔多个条目
        entries = triples_string.split('&&')

        # 创建空字典和列表来存储解析结果
        triples_dict = {}
        extracted_entities = []
        source_text_dict = {}

        # 迭代每一个条目
        for entry in entries:
            entry = entry.strip()  # 去掉条目两边的空白字符
            if not entry:
                continue  # 跳过空条目

            try:
                # 使用 "=>" 分隔实体关系部分和源文本部分
                if '=>' in entry:
                    entity_and_relation_part, source_text = entry.split('=>', 1)
                    source_text = source_text.strip().strip("'")  # 去掉源文本结尾的引号和空格

                    # 解析实体和关系部分
                    entity_and_relation_part = entity_and_relation_part.strip('() ')
                    entity_and_relation_parts = [part.strip() for part in entity_and_relation_part.split(',')]

                    # 确保格式正确，包含三个部分：实体1、关系、实体2
                    if len(entity_and_relation_parts) == 3:
                        # 分离实体和它们的类型
                        entity1, relation, entity2 = entity_and_relation_parts
                        entity1_name = entity1
                        entity2_name = entity2

                        if entity1_name not in entity_type_dict or entity2_name not in entity_type_dict:
                            continue

                        # 如果实体类型字典中没有找到实体类型，则直接跳过该条目
                        entity1_type = entity_type_dict.get(entity1_name, 'Unknown')
                        entity2_type = entity_type_dict.get(entity2_name, 'Unknown')

                        # 将关系本身作为关系类型
                        relation_type = relation.strip()

                        # 创建类型三元组
                        relation_key = (entity1_name, relation, entity2_name)
                        type_value = (entity1_type, relation_type, entity2_type)
                        triples_dict[relation_key] = type_value

                        # 将提取得实体添加进列表
                        extracted_entities.extend([entity1_name, entity2_name])

                        # 将源文本存入字典，以关系为键
                        key = f'{entity1_name}-{relation}-{entity2_name}'
                        source_text_dict[key] = source_text

            except Exception:
                logger.warning('Skipped an invalid extraction entry', exc_info=True)
        return triples_dict, list(set(extracted_entities)), source_text_dict


class AttributeExtractionResponseParser(ResponseParser):
    @staticmethod
    def parse(response: str, **kwargs):
        """
        解析实体属性提取的字符串
        :param response: 以分号分隔的实体属性字符串。
        :return: 解析后的实体字典 -> {e1: {attr1: value1, attr2: value2}, e2: {attr1: value1, attr2: value2}, ...}
        """
        # 去除不规则的空白字符 \n 和 \t
        cleaned_string = response.replace('\n', '').replace('\t', '')

        # 拆分整个字符串为以 ";" 分隔的条目
        entries = [entry.strip() for entry in cleaned_string.split('; ') if entry.strip()]

        # 创建一个空字典来存储解析结果
        entity_dict = {}

        # 迭代每一个条目并拆分为实体及其属性
        for entry in entries:
            try:
                entry = entry.strip()  # 去除前后空白字符
                if '(' in entry and ')' in entry:
                    entity_name, attributes = entry.split('(', 1)
                    entity_name = entity_name.strip()
                    attributes = attributes.strip(')').strip()
                    # 拆分属性对
                    attr_dict = {}
                    for attr in attributes.split('&&'):
                        if ':' in attr:
                            key, value = attr.split(':', 1)
                            attr_dict[key.strip()] = value.strip()
                    entity_dict[entity_name] = attr_dict
            except (TypeError, ValueError):
                continue

        return entity_dict
