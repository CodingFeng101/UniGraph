from typing import Dict, List

from jinja2 import Template

from .base_template import InstructionTemplate


class MaskedTripleInferenceTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
[DEFINE AGENT: Triple Completion]
    [DEFINE PERSONA:]
        You are a professional expert in triplet completion, strictly following the given type definition.
    [END PERSONA]
    
    [DEFINE CONSTRAINTS]
        action integrity: Ensure that the completed triplet is factual, well founded, well deep, and meaningful.
        output format: The output should follow the format "(entity1, relationship, entity2) && ...", attention the final output without double quotes and must use the delimiter && to separate multiple entries. 
    [END CONSTRAINTS]
    
    [DEFINE INPUT]
        masked triple: ${ {{masked_triple}} }$
        type: ${ {{element_type}} }$
    [END INPUT]
    
    [DEFINE INSTRUCTION]
        [COMMAND-1 <apply-constraints> action integrity </apply-constraints> According to the provided type to replace '?' with appropriate elements and give three results.]
        [COMMAND-2 <apply-constraints> output format </apply-constraints> Use the specified format constraint to output your answer.]
    [END INSTRUCTION]
[END AGENT]
        """
        return Template(template)

    @staticmethod
    def render_template(masked_triple: str, element_type: str):
        return MaskedTripleInferenceTemplate.get_template().render(
            masked_triple=masked_triple, element_type=element_type
        )


class InferredElementAttributeInferenceTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
[DEFINE AGENT: Attribute Infer]
    [DEFINE PERSONA:]
        You are a professional attribute extraction expert, based on the given entities and attributes.
    [END PERSONA]
    
    [DEFINE CONSTRAINTS]
        action integrity: Only fill in attribute values that are confirmed to be correct, otherwise set to None. Speculation (such as manufacturer, speed, etc.) is prohibited, only accepted facts (such as CPU material being silicon) are allowed.
        output format: The output should follow the format "entity(attribute1: value1 && attribute2: None); ...", attention the final output without double quotes and must use the delimiter ; to separate multiple entries, and use delimiter && to separate multiple attributes. 
    [END CONSTRAINTS]
    
    [DEFINE INPUT]
        entities with attributes: ${ {{entities_with_attribute_keys}} }$
    [END INPUT]
    
    [DEFINE INSTRUCTION]
        [COMMAND-1 <apply-constraints> action integrity </apply-constraints> Base on your wide knowledge to infer all attributes of each entity in <REF> entities </REF> to construct 'attribute: value' pair.]
        [COMMAND-2 <apply-constraints> output format </apply-constraints> Use the specified format constraint to output your answer.]
    [END INSTRUCTION]
[END AGENT]
        """
        return Template(template)

    @staticmethod
    def render_template(infer_triples: List, masked_index: int, element_type: str, entity_type_attributes: Dict):
        entities_with_attribute_keys = InferredElementAttributeInferenceTemplate.parameter_conversion(
            infer_triples, masked_index, element_type, entity_type_attributes
        )
        return InferredElementAttributeInferenceTemplate.get_template().render(
            entities_with_attribute_keys=entities_with_attribute_keys
        )

    @staticmethod
    def parameter_conversion(infer_triples: List, masked_index: int, element_type: str, entity_type_attributes: Dict):
        """
        解析schema并得到类型(类型定义), ...
        """
        entity_with_attribute_keys = list()
        for instance_triple in infer_triples:
            try:
                inferred_entity = instance_triple[masked_index]  # index确定被推理元素的位置
                attributes = entity_type_attributes[element_type]
                entity_with_attribute_keys.append(f'{inferred_entity}({", ".join(attributes)})')
            except Exception:
                continue
        return ', '.join(entity_with_attribute_keys)
