import json
from typing import Dict, List

from jinja2 import Template

from .base_template import InstructionTemplate


class EntityExtractionTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
[DEFINE AGENT: Entity Extractor]
    [DEFINE PERSONA:]
        You are an expert in extracting entities that meet the type definition from the text provided by the user based on the entity type.
    [END PERSONA]
    
    [DEFINE INPUT]
        documentation: ${ {{text_chunk}} }$
        entity types with definition: ${ {{entity_types_definitions}} }$
    [END INPUT]
    
    [DEFINE CONSTRAINTS]
        action integrity: Ensure the integrity of the extracted entities within their original text.
        output format: The output should follow the format "entity: entity type, ...", attention the final output without double quotes and must use the delimiter , to separate multiple entries. 
    [END CONSTRAINTS]
    
    [DEFINE INSTRUCTION]
        [COMMAND-1 <apply-constraints> action integrity </apply-constraints> Extract all entities in the given <REF> documentation </REF> that meet the given <REF> entity types with definition </REF>.]
        [COMMAND-2 Check and confirm that the extracted entities comply with the type definition, and extract comprehensively]
        [COMMAND-3 <apply-constraints> output format </apply-constraints> Use the specified format constraint to output your answer.]
    [END INSTRUCTION]
[END AGENT]
        """
        return Template(template)

    @staticmethod
    def render_template(kg_schema: List, schema_definition: Dict, text_chunk: str):
        entity_types_definitions = EntityExtractionTemplate.parameter_conversion(kg_schema, schema_definition)
        return EntityExtractionTemplate.get_template().render(
            text_chunk=text_chunk, entity_types_definitions=entity_types_definitions
        )

    @staticmethod
    def parameter_conversion(kg_schema: List, schema_definition: Dict):
        """
        解析schema并得到类型(类型定义), ...
        """
        entity_types = []
        for schema in kg_schema:
            for key, value in schema.items():
                try:
                    if key in ['DirectionalEntityType', 'DirectedEntityType']:
                        entity_types.append(f'{value["Name"]}({schema_definition[value["Name"]]})')
                except KeyError:
                    # schema本身存在类型定义缺失
                    continue
        # 对entity_types进行去重
        entity_types = list(set(entity_types))
        return ', '.join(entity_types)


class RelationExtractionTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
[DEFINE AGENT: Triples Extractor]
    [DEFINE PERSONA:]
        You are an expert in using the given relationships and entities to construct triples.
    [END PERSONA]
    
    [DEFINE INPUT]
        entities: ${ {{entities}} }$
        documentation: ${ {{text_chunk}} }$
    [END INPUT]
    
    [DEFINE CONSTRAINTS]
        entity restriction: The entities contained in the triples you output can only come from the given <REF> entities </REF>.
        comprehensive constraint: Fully utilize all <REF> entities </REF>, thoroughly explore the relationships between entities, and avoid any omissions.
        output format: The output should follow the format "(entity1, relationship, entity2) && ...", attention the final output without double quotes and must use the delimiter && to separate multiple entries.
    [END CONSTRAINTS]
    
    [DEFINE INSTRUCTION]
        [COMMAND-1 <apply-constraints> entity restriction, comprehensive constraint </apply-constraints> Based on the <REF> entities </REF>, infer and extract relationship from <REF> documentation </REF> to construct triples.]
        [COMMAND-2 Check and confirm that the semantics and logical order of the triples are consistent with the <REF> documentation </REF>, and the entities in the triples come from the provided <REF> entities </REF>]
        [COMMAND-3 <apply-constraints> output format </apply-constraints> Use the specified format constraint to output your answer.]
    [END INSTRUCTION]
[END AGENT]
"""
        return Template(template)

    @staticmethod
    def render_template(entity_type_dict: Dict, text_chunk: str, kg_schema: List, schema_definition: Dict):
        entities_set, relation_types_definitions = RelationExtractionTemplate.parameter_conversion(
            entity_type_dict, kg_schema, schema_definition
        )
        # 默认关系类型作为关系
        return RelationExtractionTemplate.get_template().render(
            entities=entities_set, text_chunk=text_chunk, relation_definitions=relation_types_definitions
        )

    @staticmethod
    def parameter_conversion(entity_type_dict: Dict, kg_schema: List, schema_definition: Dict):
        """
        解析schema并得到类型(类型定义), ...
        """
        entities_with_type = list()
        for entity, entity_type in entity_type_dict.items():
            # entities_with_type.append(f"{entity}({entity_type})")
            entities_with_type.append(entity)

        relation_types_definitions = []
        for schema in kg_schema:
            try:
                for key, value in schema.items():
                    if key == 'RelationType':
                        relation_types_definitions.append(f'{value}({schema_definition[value]})')
            except KeyError:
                # schema本身存在问题，直接跳过该类型
                continue
        # 对relation_types_definitions进行去重
        relation_types_definitions = list(set(relation_types_definitions))
        return ', '.join(entities_with_type), ', '.join(relation_types_definitions)


class TriplesTracingTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
[DEFINE AGENT: Triples Tracer]
    [DEFINE PERSONA:]
        You are an expert in tracing triples.
    [END PERSONA]
        
    [DEFINE INPUT]
        triples_set: ${ {{triples_set}} }$
        documentation: ${ {{text_chunk}} }$
    [END INPUT]
    
    [DEFINE CONSTRAINTS]
        semantic association: The source information corresponding to each triples must be consistent with the meaning expressed by the triples.
        output format: The output should follow the format "(entity1, relationship, entity2)=>'source information' && ...", attention the final output without double quotes and must use the delimiter && to separate multiple entries.
    [END CONSTRAINTS]
    
    [DEFINE INSTRUCTION]
        [COMMAND-1 Read each triples in <REF> triples_set </REF> and understand its semantics.]
        [COMMAND-2 <apply-constraints> semantic association </apply-constraints> Extract all sentences related to the triples as source information based on the provided documentation.]
        [COMMAND-3 <apply-constraints> output format </apply-constraints> Use the specified format constraint to output your answer.]
    [END INSTRUCTION]
[END AGENT]
        """
        return Template(template)

    @staticmethod
    def render_template(triples_set: str, text_chunk: str):
        return TriplesTracingTemplate.get_template().render(triples_set=triples_set, text_chunk=text_chunk)


class RelationTypeMatchTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
[DEFINE AGENT: Relationship type match]
    [DEFINE PERSONA:]
        You are an expert in matching the relationship types of the triples.
    [END PERSONA]
        
    [DEFINE INPUT]
        triples: ${ {{triples}} }$
        relationship types: ${ {{relation_types}} }$
    [END INPUT]
    
    [DEFINE CONSTRAINTS]
        semantic constraint: The matched relationship type needs to maintain semantic consistency with the relationship of the triples.
        output format: The output should follow the format "(entity1, relationship, entity2): relationship type && ...", attention the final output without double quotes and must use the delimiter && to separate multiple entries.
    [END CONSTRAINTS]
    
    [DEFINE INSTRUCTION]
        [COMMAND-1 <apply-constraints> semantic constraint </apply-constraints> Based on the <REF> relationship types </REF>, match semantically closest relationship type for relationship in triples]
        [COMMAND-2 <apply-constraints> output format </apply-constraints> Use the specified format constraint to output your answer.]
    [END INSTRUCTION]
[END AGENT]
        """
        return Template(template)

    @staticmethod
    def render_template(triples: str, kg_schema: List, schema_definition: Dict):
        relation_types = RelationTypeMatchTemplate.parameter_conversion(kg_schema, schema_definition)
        return RelationTypeMatchTemplate.get_template().render(triples=triples, relation_types=relation_types)

    @staticmethod
    def parameter_conversion(kg_schema: List, schema_definition: Dict):
        """
        解析schema并得到类型(类型定义), ...
        """
        relation_types = []
        for schema in kg_schema:
            for key, value in schema.items():
                try:
                    if key == 'RelationType':
                        relation_types.append(f'{value}({schema_definition[value]})')
                except KeyError:
                    # schema本身存在问题，直接跳过该类型
                    continue
        # 对relation_types进行去重
        relation_types = list(set(relation_types))
        return ', '.join(relation_types)


class AttributeExtractionTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
[DEFINE AGENT: Attribute Extractor]
    [DEFINE PERSONA:]
        You are a professional attribute extraction expert, based on the given entities and attributes.
    [END PERSONA]
        
    [DEFINE INPUT]
        documentation: ${ {{text_chunk}} }$
        entities with attributes: ${ {{entities_with_attribute_keys}} }$
    [END INPUT]
    
    [DEFINE CONSTRAINTS]
        action integrity: Ensure that every attribute of each entity is extracted and assigned, and assign None to attributes that do not exist in the documentation.
        output format: The output should follow the format "entity(attribute1: value1 && attribute2: None); ...", attention the final output without double quotes and must use the delimiter ; to separate multiple entries, and use delimiter && to separate multiple attributes. 
    [END CONSTRAINTS]
    
    [DEFINE INSTRUCTION]
        [COMMAND-1 <apply-constraints> action integrity </apply-constraints> Based on the <REF> documentation </REF> to extract the values corresponding to all attributes of each entity in <REF> entities </REF> to construct 'attribute: value' pair.]
        [COMMAND-2 <apply-constraints> output format </apply-constraints> Use the specified format constraint to output your answer.]
    [END INSTRUCTION]
[END AGENT]
        """
        return Template(template)

    @staticmethod
    def render_template(text_chunk: str, kg_schema: List, extracted_entities_dict: Dict):
        entities_with_attribute_keys = AttributeExtractionTemplate.parameter_conversion(
            kg_schema, extracted_entities_dict
        )
        return AttributeExtractionTemplate.get_template().render(
            text_chunk=text_chunk, entities_with_attribute_keys=entities_with_attribute_keys
        )

    @staticmethod
    def parameter_conversion(kg_schema: List, extracted_entities_dict: Dict):
        """
        解析schema并得到类型(类型定义), ...
        """
        entities_with_type = list()
        type_attributes_dict = dict()
        for schema in kg_schema:
            for k, v in schema.items():
                if k in ['DirectionalEntityType', 'DirectedEntityType']:
                    type_attributes_dict[v['Name']] = json.loads(v['Attributes'])
        for entity, entity_type in extracted_entities_dict.items():
            try:
                attribute_keys = type_attributes_dict[entity_type]
                if attribute_keys:
                    entities_with_type.append(f'{entity}({", ".join(attribute_keys)})')
            except KeyError:
                continue
        return ', '.join(entities_with_type)
