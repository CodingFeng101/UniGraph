import asyncio
import json
import re

from backend.common.core_layer.unigraph.module.schema_construction.related_retrieve import (
    batch_get_vectors,
    cosine_similarity,
)


def transform_dict(original_dict):
    """
    Normalize the definition dictionary to handle inconsistent LLM output formats

    Args:
        original_dict: Dictionary with potentially inconsistent format from LLM

    Returns:
        Normalized dictionary with consistent structure
    """
    new_dict = {}

    for key, value in original_dict.items():
        if isinstance(value, str):
            # Split value using regex to handle newlines and whitespace
            sub_items = re.split(r'\n\s+', value.strip())
            for item in sub_items:
                if ':' in item:
                    # Split each sub-item and its explanation
                    sub_key, sub_value = item.split(':', 1)
                    new_dict[sub_key.strip()] = sub_value.strip()
                else:
                    # If no colon, add original value directly
                    new_dict[key] = item.strip()
        else:
            new_dict[key] = value

    return new_dict


def extract_definition(response):
    """
    Extract definitions from response text without relying on identifiers

    Args:
        response: Raw text response containing definitions

    Returns:
        Dictionary of extracted definitions
    """
    definitions_text = response.strip()
    definition = {}

    # Process each line in the response
    for line in definitions_text.split('\n'):
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Process lines in key: value format
        if ':' in line:
            key_part, value_part = line.split(':', 1)
            key = key_part.strip()
            value = value_part.strip()
            # Add to dictionary if key doesn't exist
            if key not in definition:
                definition[key] = value
    # Return normalized definition dictionary
    return transform_dict(definition)


def get_new_entity_types_from_response(response):
    """
    Extract entity types and their instances from LLM response

    Args:
        response: Raw text response containing entity classifications

    Returns:
        Dictionary mapping entity types to their instances
    """
    try:
        entity_type_dict = {}

        # Process each line in the response
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Split entity type and entity list
            if ':' in line:
                type, entities_str = line.split(':', 1)
                type = type.strip().strip('*')

                # Extract entity instances
                entities = [e.strip(' "') for e in entities_str.split(',')]
                entities = [e for e in entities if e]  # Remove empty entities

                # Add to dictionary
                entity_type_dict[type] = entities

    except Exception as e:
        print('Error processing entities: ', e)
        raise
    return entity_type_dict


def get_new_relationship_types_from_response(response):
    """
    Extract relationship types and their instances from LLM response

    Args:
        response: Raw text response containing relationship classifications

    Returns:
        Dictionary mapping relationship types to their instances
    """
    try:
        relation_type_dict = {}

        # Process each line in the response
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Split relationship type and relationship list
            if ':' in line:
                type, relationships_str = line.split(':', 1)
                type = type.strip()

                # Extract relationship instances
                relationships = [rel.strip(' "') for rel in relationships_str.split(',')]
                relationships = [rel for rel in relationships if rel]  # Remove empty relationships

                # Add to dictionary
                relation_type_dict[type] = relationships

    except Exception as e:
        print('get_new_relationship_categories Error: ', e)
        raise  # Re-raise the caught exception

    return relation_type_dict


def convert_to_type_triples(instance_triples, entity_type_dict, relation_type_dict):
    """
    Convert instance triples to type triples with case-insensitive matching and deduplication

    Args:
        instance_triples: List of instance triples
        entity_type_dict: Dictionary mapping entity types to their instances
        relation_type_dict: Dictionary mapping relation types to their instances

    Returns:
        List of deduplicated type triples
    """
    try:

        def find_entity_type(entity_name):
            """Find entity type for given entity name (case-insensitive)"""
            target_lower = entity_name.lower()
            for entity_type, entities in entity_type_dict.items():
                # Compare lowercase versions
                if any(entity.lower() == target_lower for entity in entities):
                    return entity_type
            return None

        def find_relation_type(relation_name):
            """Find relation type for given relation name (case-insensitive with space handling)"""
            # Normalize relation name: trim + collapse spaces + lowercase
            normalized_relation = ' '.join(relation_name.strip().split()).lower()
            for relation_type, relations in relation_type_dict.items():
                # Compare normalized versions
                if any(' '.join(rel.strip().split()).lower() == normalized_relation for rel in relations):
                    return relation_type
            return None

        typed_triples = []
        seen_triples = set()  # For deduplication

        for triple in instance_triples:
            head_type = find_entity_type(triple['head'])
            tail_type = find_entity_type(triple['tail'])
            relation_type = find_relation_type(triple['relation'])

            if head_type and tail_type and relation_type:
                # Create deduplication key (case-insensitive with normalized spaces)
                triple_key = (
                    head_type,
                    triple['head'].lower(),
                    relation_type,
                    ' '.join(triple['relation'].strip().split()).lower(),
                    tail_type,
                    triple['tail'].lower(),
                )
                if triple_key not in seen_triples:
                    seen_triples.add(triple_key)
                    typed_triple = {
                        'DirectionalEntity': {'type': head_type, 'name': triple['head']},
                        'Relation': {'type': relation_type, 'name': triple['relation'].strip()},
                        'DirectedEntity': {'type': tail_type, 'name': triple['tail']},
                    }
                    typed_triples.append(typed_triple)

        return typed_triples

    except Exception as e:
        print(f'Error in convert_to_type_triples: {e}')
        raise


def extract_unique_entities_and_relations(triples):
    """
    Extract unique entities and relations from a list of triples

    Args:
        triples: List of triples to process

    Returns:
        Dictionary containing sorted lists of unique entities and relations
    """
    entities = set()
    relations = set()

    for item in triples:
        # Add head and tail entities
        entities.add(item['head'])
        entities.add(item['tail'])
        # Add relation (with whitespace trimmed)
        relations.add(item['relation'].strip())

    return {'entities': sorted(list(entities)), 'relations': sorted(list(relations))}


async def merge_type_dicts_with_semantic(dict1, dict2):
    """
    Merge two type dictionaries using semantic similarity between keys

    Args:
        dict1: First dictionary to merge (will be used as base)
        dict2: Second dictionary to merge

    Returns:
        Merged dictionary with duplicate values removed
    """
    # Collect all words that need vector representations
    all_words = list(dict1.keys()) + list(dict2.keys())

    # Batch get vector representations for all words to minimize API calls
    word_vectors = await batch_get_vectors(all_words)

    # Pre-compute vectors for dict1 keys
    dict1_vectors = {k: word_vectors[k] for k in dict1.keys()}

    # Initialize result dictionary with dict1 contents
    merged = dict1.copy()
    unmatched_keys = set(dict2.keys())  # Track keys from dict2 that haven't been matched

    # Process each key from dict2 concurrently with rate limiting
    semaphore = asyncio.Semaphore(100)  # Limit concurrent operations

    async def process_item(key2, values2):
        async with semaphore:
            # Find most similar key in dict1
            max_similarity = 0
            best_match = None

            # Calculate similarity between key2 and each key in dict1
            for key1, vec1 in dict1_vectors.items():
                vec2 = word_vectors[key2]
                similarity = cosine_similarity(vec1, vec2)

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = key1

            # Only consider matches with similarity > 0.85
            if max_similarity > 0.85:
                unmatched_keys.discard(key2)
                return best_match, values2, None
            else:
                return None, None, (key2, values2)

    # Create processing tasks for all items in dict2
    tasks = [process_item(k, v) for k, v in dict2.items()]

    # Process results as they complete
    for coro in asyncio.as_completed(tasks):
        best_match, values_to_merge, new_item = await coro

        if best_match:
            # Merge values into existing key from dict1
            merged[best_match].extend(values_to_merge)
        elif new_item:
            # Add new key-value pair to merged dictionary
            key, values = new_item
            merged[key] = values.copy()

    # Remove duplicate values from merged dictionary
    return {k: list(set(v)) for k, v in merged.items()}


def delete_irrelevant_definitions(kg_schema, definition_dict):
    """
    Filter definitions dictionary to only include types that exist in the knowledge graph schema

    Args:
        kg_schema: JSON string representing the knowledge graph schema
        definition_dict: Dictionary of type definitions to filter

    Returns:
        Filtered dictionary containing only relevant definitions
    """
    # Parse the JSON schema into a Python dictionary
    schema_data = json.loads(kg_schema)
    relevant_definitions = {}

    # Collect all node and edge types from the schema
    existing_types = set()

    # Extract node types
    for node in schema_data['nodes']:
        existing_types.add(node['type'])

    # Extract edge/relationship types
    for edge in schema_data['edges']:
        existing_types.add(edge['type'])

    # Only keep definitions for types that exist in the schema
    for type_name, type_definition in definition_dict.items():
        if type_name in existing_types:
            relevant_definitions[type_name] = type_definition

    return relevant_definitions


def get_entity_type_attributes_from_response(response):
    # 按行分割输入字符串
    lines = response.split('\n')

    entity_type_attribute_dict = {}

    for line in lines:
        if '：' in line:  # 处理中文冒号
            key, value_part = line.split('：', 1)
            # 统一替换中文顿号为逗号，然后按逗号分割
            values = [v.strip() for v in re.split('，|、', value_part)]
            entity_type_attribute_dict[key.strip()] = values
        elif ':' in line:  # 处理英文冒号
            key, value_part = line.split(':', 1)
            # 统一替换中文顿号为逗号，然后按逗号分割
            values = [v.strip() for v in re.split(',|、', value_part)]
            entity_type_attribute_dict[key.strip()] = values

    return entity_type_attribute_dict


def transform_triplets_to_schema(triplets_dict, entity_types, relation_types, entity_attributes):
    """
    将三元组字典转换为符合规范的schema列表

    参数:
        triplets_dict: 三元组-源文本字典
        entity_types: 实体类型字典（实体类型 -> [实体名]）
        relation_types: 关系类型字典（关系类型 -> [谓词]）
        entity_attributes: 实体类型 -> 属性列表

    返回:
        schema结构列表，每项包含entity type、relation type、source
    """
    result = []

    # 创建实体名称 → 实体类型的映射
    entity_name_to_type = {}
    for etype, enames in entity_types.items():
        for name in enames:
            entity_name_to_type[name.strip()] = etype

    # 创建谓词名称 → 关系类型的映射
    relation_name_to_type = {}
    for rtype, rnames in relation_types.items():
        for name in rnames:
            relation_name_to_type[name.strip()] = rtype

    for triplet, source_text in triplets_dict.items():
        try:
            left, relation, right = [part.strip(' ()"\'') for part in triplet.strip('()').split(',')]
        except ValueError:
            continue  # 跳过格式不正确的

        # 尝试映射为类型名
        left_type = entity_name_to_type.get(left)
        right_type = entity_name_to_type.get(right)
        relation_type = relation_name_to_type.get(relation)

        # 若任一项未匹配到类型名，则跳过该三元组
        if not all([left_type, relation_type, right_type]):
            continue

        # 查找属性
        left_attrs = entity_attributes.get(left_type, [])
        right_attrs = entity_attributes.get(right_type, [])

        schema_entry = {
            'schema': {
                'DirectionalEntityType': {'Name': left_type, 'Attributes': left_attrs},
                'RelationType': relation_type,
                'DirectedEntityType': {'Name': right_type, 'Attributes': right_attrs},
            },
            'source': {triplet: source_text},
        }

        result.append(schema_entry)

    return result


def extract_triples_and_strings(input_str):
    """
    提取以三元组字符串为键的字典 + 实体和关系集合字符串。

    示例输入行格式：
    (实体1, 关系, 实体2): 描述
    """
    Triple_source_dict = {}
    entities = set()
    relations = set()

    for line in input_str.strip().split('\n'):
        line = line.strip()
        if not line or ':' not in line:
            continue

        triple_str_raw, description = line.split(':', 1)
        triple_str = triple_str_raw.strip()
        Triple_source_dict[triple_str] = description.strip()

        # 用正则从三元组字符串中提取实体和关系（容忍中英文逗号）
        match = re.match(r'\(\s*([^,，]+?)\s*[,，]\s*([^,，]+?)\s*[,，]\s*([^)]+?)\s*\)', triple_str)
        if match:
            e1, rel, e2 = match.groups()
            entities.update([e1, e2])
            relations.add(rel)

    entity_string = ','.join(entities)
    relation_string = ','.join(relations)

    return Triple_source_dict, entity_string, relation_string


def deduplicate_schema(schema_list):
    """
    去重逻辑：按 (head_type, relation_type, tail_type) 三元组去重，
    保留该组中最后一个非空 source 的字典（如果没有非空 source 则保留最后一个）
    """
    from collections import defaultdict

    grouped = defaultdict(list)

    # 按照三元组分组
    for item in schema_list:
        schema = item['schema']
        head = schema['DirectionalEntityType']['Name']
        rel = schema['RelationType']
        tail = schema['DirectedEntityType']['Name']
        key = (head, rel, tail)
        grouped[key].append(item)

    deduped = []
    for group in grouped.values():
        # 优先保留最后一个非空 source，如果没有非空 source，保留最后一个
        for item in reversed(group):
            if item['source']:
                deduped.append(item)
                break
        else:
            deduped.append(group[-1])  # 全是空的，就保留最后一个

    return deduped


def is_chinese_more_than_english(text: str) -> bool:
    """
    判断文本中中文字符是否比英文字符多

    参数:
        text (str): 要分析的文本

    返回:
        bool: 如果中文字符多，返回 True，否则返回 False
    """
    chinese_count = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_count = len(re.findall(r'[A-Za-z]', text))

    return chinese_count > english_count
