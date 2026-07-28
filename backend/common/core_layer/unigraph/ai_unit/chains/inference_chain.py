import random
from hashlib import sha256
from typing import Dict, Tuple

from ..llm.response_getter import ResponseGetter
from ..query_template.inference_templates import (
    InferredElementAttributeInferenceTemplate,
    MaskedTripleInferenceTemplate,
)
from ..response_parser.inference_parser import (
    InferredEntityAttributeInferenceResponseParser,
    MaskedTripleInferenceResponseParser,
)
from .base_instruction import BaseInstruction


class InferenceInstruction1(BaseInstruction):
    async def execute(
        self,
        ai_response_getter: ResponseGetter,
        masked_triple: str,
        element_type: str,
        index: int,
        entity_type_attributes: Dict,
        api_key: str,
        base_url: str,
        model: str,
    ):

        # 执行masked三元组不全与结果解析
        query = MaskedTripleInferenceTemplate.render_template(
            masked_triple=masked_triple,
            element_type=element_type,
        )
        response = await ai_response_getter.get_response(
            query=query,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        ins1_output = MaskedTripleInferenceResponseParser.parse(
            response
        )  # ins1_output_triples_dict, ins1_output_entities
        if self.next_instruction:
            if not ins1_output[0]:
                # 如果解析三元组为空，直接返回
                return False
            return await self.next_instruction.execute(
                ai_response_getter=ai_response_getter,
                ins1_output=ins1_output,
                element_type=element_type,
                index=index,
                entity_type_attributes=entity_type_attributes,
                api_key=api_key,
                base_url=base_url,
                model=model,
            )


class InferenceInstruction2(BaseInstruction):
    async def execute(
        self,
        ai_response_getter: ResponseGetter,
        ins1_output: Tuple,
        element_type: str,
        index: int,
        entity_type_attributes: Dict,
        api_key: str,
        base_url: str,
        model: str,
    ):
        """
        :param ai_response_getter: ResponseGetter
        :param ins1_output: Tuple
        :param element_type: str
        :param index: int  决定取哪个实体的属性键列表
        :param entity_type_attributes: Dict
        :param api_key: str
        :param base_url: str
        :param model: str
        :return: Tuple[]
        """
        if index == 1:  # 如果被推理元素是关系，则无需推理实体属性，直接返回空字典
            return ins1_output, {}
        if index == 0 or index == 2:  # 检查左，右实体类型属性列表是否为空。否则直接返回空属性字典
            if element_type in entity_type_attributes:
                if not entity_type_attributes[element_type]:
                    return ins1_output, {}
            else:
                return ins1_output, {}

        # 执行inferred实体属性推理与结果解析
        query = InferredElementAttributeInferenceTemplate.render_template(
            infer_triples=ins1_output[0],
            masked_index=index,
            element_type=element_type,
            entity_type_attributes=entity_type_attributes,
        )
        response = await ai_response_getter.get_response(
            query=query,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        ins2_output = InferredEntityAttributeInferenceResponseParser.parse(
            response
        )  # ins2_output_entities_attribute_dict
        if self.next_instruction:
            return await self.next_instruction.execute()
        else:
            return ins1_output, ins2_output


def random_slice(lst, slice_length):
    """
    对三元组的哈希值进行随机切片处理，控制其长度
    """
    if slice_length > len(lst):
        return 'Error: slice length is greater than list length.'
    start = random.randint(0, len(lst) - slice_length)
    return lst[start : start + slice_length]


async def run_inference_chain(
    ai_response_getter: ResponseGetter = None,
    masked_triple: Tuple = None,
    entity_type_attributes: Dict = None,
    type_triple: Tuple = None,
    api_key: str = None,
    base_url: str = None,
    model: str = None,
):
    """
    :param ai_response_getter: ResponseGetter
    :param masked_triple: Tuple
    :param entity_type_attributes: Entity types mapped to their attribute names.
    :param type_triple: Tuple
    :param api_key: str
    :param base_url: str
    :param model: str
    :return: KG
    """

    # 定位遮盖元素的元组索引：
    index = masked_triple.index('?')
    # masked三元组不全
    inference_instruction1 = InferenceInstruction1()
    # inferred实体属性推理
    inference_instruction2 = InferenceInstruction2()

    inference_instruction1.set_next(inference_instruction2)

    result = await inference_instruction1.execute(
        ai_response_getter=ai_response_getter,
        masked_triple=str(masked_triple),
        element_type=type_triple[index],
        index=index,
        entity_type_attributes=entity_type_attributes,
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    if not result:
        return []
    ins1_output, ins2_output = result

    instance_type_triple_pair_dict = {instance_triple: type_triple for instance_triple in ins1_output[0]}
    entity_attribute_dict = ins2_output

    # 整合输出内容，转换为KG
    kg_json_format = []

    # 分离三元组和类型三元组 -> 一对一的形式：
    for triples, type_triples in instance_type_triple_pair_dict.items():
        try:
            directional_entity, relation, directed_entity = triples
            directional_entity_type, relation_type, directed_entity_type = type_triples
            # 从实体属性字典中获取实体属性，如果没有则从类型属性字典中获取，并将属性值置为Unknown
            triple_hash = random_slice(
                sha256(f'({directional_entity}, {relation}, {directed_entity})'.encode('utf-8')).hexdigest(), 8
            )
            directional_entity_attributes = entity_attribute_dict.get(directional_entity, {})
            directed_entity_attributes = entity_attribute_dict.get(directed_entity, {})

            kg_json_format.append({
                'DirectionalEntity': {
                    'Type': directional_entity_type,
                    'Name': directional_entity,
                    'Attributes': directional_entity_attributes,
                },
                'Relation': {'Type': relation_type, 'Name': relation, 'Attributes': {}},
                'DirectedEntity': {
                    'Type': directed_entity_type,
                    'Name': directed_entity,
                    'Attributes': directed_entity_attributes,
                },
                'ID': triple_hash,
            })
        except Exception:
            continue
    return kg_json_format
