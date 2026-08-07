import asyncio
import logging
import random
from hashlib import sha256
from typing import Dict, List, Tuple

from ..llm.response_getter import ResponseGetter
from ..query_template.extraction_templates import (  # 添加溯源智能体模板
    AttributeExtractionTemplate,
    EntityExtractionTemplate,
    RelationExtractionTemplate,
    RelationTypeMatchTemplate,
    TriplesTracingTemplate,
)
from ..response_parser.extraction_parser import (
    AttributeExtractionResponseParser,
    EntityExtractionResponseParser,
    RelationExtractionResponseParser,
)
from .base_instruction import BaseInstruction

logger = logging.getLogger(__name__)


class ExtractionInstruction1(BaseInstruction):
    async def execute(
        self,
        ai_response_getter: ResponseGetter,
        chunk: str,
        kg_schema: List,
        schema_definition: Dict,
        api_key: str,
        base_url: str,
        model: str,
    ):
        """
        参数三件套，为整条责任链的起始参数
        :param ai_response_getter: 响应获取器
        :param chunk: 待提取的文本
        :param kg_schema: 知识图谱的schema
        :param schema_definition: 知识图谱的schema定义
        :param api_key: API密钥
        :param base_url: API基础URL
        :param model: 模型名称
        :return: 下一步责任链的执行结果
        """
        # 执行实体提取与结果解析
        query = EntityExtractionTemplate.render_template(
            kg_schema=kg_schema, schema_definition=schema_definition, text_chunk=chunk
        )  # 生成步骤请求
        response = await ai_response_getter.get_response(
            query=query, api_key=api_key, base_url=base_url, model=model
        )  # 获取响应

        ins1_output = EntityExtractionResponseParser.parse(response)  # 解析响应

        ins1_output = (ins1_output,)  # 统一参数容器类型为元组，以便run_chain函数分辨参数集和
        if self.next_instruction:
            if not ins1_output[0]:
                return False  # 无法提取实体，终止chain的运行
            return await self.next_instruction.execute(
                ai_response_getter=ai_response_getter,
                ins1_output=ins1_output,
                chunk=chunk,
                kg_schema=kg_schema,
                schema_definition=schema_definition,
                api_key=api_key,
                base_url=base_url,
                model=model,
            )


class ExtractionInstruction2(BaseInstruction):
    async def execute(
        self,
        ai_response_getter: ResponseGetter,
        ins1_output: Tuple,
        chunk: str,
        kg_schema: List,
        schema_definition: Dict,
        api_key: str,
        base_url: str,
        model: str,
    ):
        query = RelationExtractionTemplate.render_template(
            entity_type_dict=ins1_output[0], kg_schema=kg_schema, schema_definition=schema_definition, text_chunk=chunk
        )

        # 所得三元组集合字符串
        response = await ai_response_getter.get_response(
            query=query,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        # 无需解析，直接进行下一步。
        ins2_output = response
        # 执行三元组提取与结果解析
        if self.next_instruction:
            if not ins2_output:
                return False
            return await self.next_instruction.execute(
                ai_response_getter=ai_response_getter,
                ins1_output=ins1_output,
                ins2_output=ins2_output,
                chunk=chunk,
                kg_schema=kg_schema,
                schema_definition=schema_definition,
                api_key=api_key,
                base_url=base_url,
                model=model,
            )


class ExtractionInstruction3(BaseInstruction):
    async def execute(
        self,
        ai_response_getter: ResponseGetter,
        ins1_output: Tuple,
        ins2_output: str,
        chunk: str,
        kg_schema: List,
        schema_definition: Dict,
        api_key: str,
        base_url: str,
        model: str,
    ):
        # 执行三元组溯源与结果解析
        query = TriplesTracingTemplate.render_template(triples_set=ins2_output, text_chunk=chunk)

        # 执行三元组类型匹配
        query_ = RelationTypeMatchTemplate.render_template(
            triples=ins2_output, kg_schema=kg_schema, schema_definition=schema_definition
        )

        # 使用asyncio.gather并行执行两个请求
        response, response_ = await asyncio.gather(
            ai_response_getter.get_response(
                query=query,
                api_key=api_key,
                base_url=base_url,
                model=model,
            ),
            ai_response_getter.get_response(
                query=query_,
                api_key=api_key,
                base_url=base_url,
                model=model,
            ),
        )

        ins3_output = RelationExtractionResponseParser.parse(
            response=response, entity_type_dict=ins1_output[0]
        )  # 实体属性嵌套字典entity_attribute_dict

        def parse_match_result(response):
            """
            解析字符串(e1, r, e2): type && ... 为字典{ r: type, ... }
            """

            match_string = response.replace('\n', '').replace('\t', '')
            # 使用 "&&" 分隔多个条目
            entries = match_string.split('&&')
            # 创建空字典来存储解析结果
            match_dict = {}
            # 迭代每一个条目
            for entry in entries:
                try:
                    if ':' in entry:
                        triples, entity_type = entry.split(':', 1)
                        # 得到三元组中的关系(e1, r, e2)中的r
                        triples = triples.strip()
                        relation = triples.split(',')[1].strip()  # 提取关系
                        # 将关系和类型存入字典
                        match_dict[relation] = entity_type.strip()
                    else:
                        # 如果没有冒号，可能是错误的格式，跳过
                        continue
                except (IndexError, ValueError):
                    continue
            return match_dict

        ins3_output_ = parse_match_result(response_)  # 实体属性嵌套字典entity_attribute_dict
        ins3_output = (ins3_output, ins3_output_)  # 统一参数容器类型为元组，以便run_chain函数分辨参数集和

        if self.next_instruction:
            return await self.next_instruction.execute(
                ai_response_getter=ai_response_getter,
                ins1_output=ins1_output,
                ins2_output=ins3_output,
                chunk=chunk,
                kg_schema=kg_schema,
                api_key=api_key,
                base_url=base_url,
                model=model,
            )
        else:
            return ins2_output, ins3_output


class ExtractionInstruction4(BaseInstruction):
    async def execute(
        self,
        ai_response_getter: ResponseGetter,
        ins1_output: Tuple,
        ins2_output: Tuple,
        chunk: str,
        kg_schema: List,
        api_key: str,
        base_url: str,
        model: str,
    ):
        # 执行属性提取与结果解析
        query = AttributeExtractionTemplate.render_template(
            text_chunk=chunk, kg_schema=kg_schema, extracted_entities_dict=ins1_output[0]
        )
        response = await ai_response_getter.get_response(
            query=query,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        ins3_output = AttributeExtractionResponseParser.parse(response)  # 实体属性嵌套字典entity_attribute_dict
        ins3_output = (ins3_output,)  # 统一参数容器类型为元组，以便run_chain函数分辨参数集和
        if self.next_instruction:
            return await self.next_instruction.execute()
        else:
            return ins1_output, ins2_output, ins3_output


def random_slice(lst, slice_length):
    """
    对三元组的哈希值进行随机切片处理，控制其长度
    """
    if slice_length > len(lst):
        return 'Error: slice length is greater than list length.'
    start = random.randint(0, len(lst) - slice_length)
    return lst[start : start + slice_length]


async def run_extraction_chain(
    ai_response_getter: ResponseGetter = None,
    chunk: str = '',
    kg_schema: List = None,
    schema_definition: Dict = None,
    api_key: str = None,
    base_url: str = None,
    model: str = None,
):
    """
    参数待定，是为chain的起始参数
    """
    # 实体提取
    extraction_instruction1 = ExtractionInstruction1()
    # 三元组提取
    extraction_instruction2 = ExtractionInstruction2()
    # 溯源提取
    extraction_instruction3 = ExtractionInstruction3()
    # 属性提取
    extraction_instruction4 = ExtractionInstruction4()

    # 构建责任链
    extraction_instruction1.set_next(extraction_instruction2)
    extraction_instruction2.set_next(extraction_instruction3)
    extraction_instruction3.set_next(extraction_instruction4)

    # 获取异步结果
    result = await extraction_instruction1.execute(
        ai_response_getter=ai_response_getter,
        chunk=chunk,
        kg_schema=kg_schema,
        schema_definition=schema_definition,
        api_key=api_key,
        base_url=base_url,
        model=model,
    )
    if not result:  # 如果无法确定任何关系，直接返回空值
        return [], {}  # 分别是kg_json_format和source_row_list
    ins1_output, ins2_output, ins3_output = result

    instance_type_triple_pair_dict = ins2_output[0][0]
    relation_type_dict = ins2_output[1]
    entity_attribute_dict = ins3_output[0]
    source_text_dict = ins2_output[0][2]

    # 得到类型对应的属性，防止有些实体没有属性
    schema_type_attributes = {}
    for schema in kg_schema:
        schema_type_attributes[schema['DirectionalEntityType']['Name']] = {
            k: 'Unknown' for k in schema['DirectionalEntityType']['Attributes']
        }
        schema_type_attributes[schema['DirectedEntityType']['Name']] = {
            k: 'Unknown' for k in schema['DirectedEntityType']['Attributes']
        }

    # 整合输出内容，转换为KG
    kg_json_format = []  # KG
    source_row_list = []  # TripleSource

    # 分离三元组和类型三元组 -> 一对一的形式：
    for triples, type_triples in instance_type_triple_pair_dict.items():
        try:
            directional_entity, relation, directed_entity = triples
            triple_hash = random_slice(
                sha256(f'({directional_entity}, {relation}, {directed_entity})'.encode('utf-8')).hexdigest(), 8
            )
            # 添加source数据行
            source_row_list.append({
                'ID': triple_hash,
                'TripleSource': source_text_dict[f'{directional_entity}-{relation}-{directed_entity}'],
            })
            directional_entity_type, relation_type, directed_entity_type = type_triples
            # 从实体属性字典中获取实体属性，如果没有则从类型属性字典中获取，并将属性值置为Unknown
            directional_entity_attributes = entity_attribute_dict.get(
                directional_entity, schema_type_attributes.get(directional_entity, {})
            )
            directed_entity_attributes = entity_attribute_dict.get(
                directed_entity, schema_type_attributes.get(directed_entity, {})
            )

            kg_json_format.append({
                'DirectionalEntity': {
                    'Type': directional_entity_type,
                    'Name': directional_entity,
                    'Attributes': directional_entity_attributes,
                },
                'Relation': {
                    'Type': relation_type_dict.get(relation, relation_type),
                    'Name': relation,
                    'Attributes': {},
                },
                'DirectedEntity': {
                    'Type': directed_entity_type,
                    'Name': directed_entity,
                    'Attributes': directed_entity_attributes,
                },
                'ID': triple_hash,
            })
        except Exception:
            continue
    return kg_json_format, source_row_list
