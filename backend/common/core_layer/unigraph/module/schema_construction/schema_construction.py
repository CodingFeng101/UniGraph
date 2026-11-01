from pathlib import Path

from jinja2 import Template

from backend.common.core_layer.unigraph.ai_unit.llm.response_getter import GenericResponseGetter
from backend.common.core_layer.unigraph.file.file_loader import FileLoader
from backend.common.core_layer.unigraph.module.schema_construction.utils import (
    deduplicate_schema,
    extract_definition,
    extract_triples_and_strings,
    get_entity_type_attributes_from_response,
    get_new_entity_types_from_response,
    get_new_relationship_types_from_response,
    is_chinese_more_than_english,
    merge_type_dicts_with_semantic,
    transform_triplets_to_schema,
)


class SchemaConstruction:
    def __init__(self, kg_schema, definition):
        self.kg_schema = kg_schema
        self.definition = definition
        self.suggestion = ''
        # 更新架构时，已有的类型是新实例优先归入的类别；先放进字典，语义合并时才能对齐到它们，
        # 否则新类型自成一体，更新后的架构会和原架构断开
        self.existing_entity_types = sorted({
            entity['Name']
            for item in kg_schema
            for entity in (item['schema'].get('DirectionalEntityType'), item['schema'].get('DirectedEntityType'))
            if entity and entity.get('Name')
        })
        self.existing_relation_types = sorted({
            item['schema']['RelationType'] for item in kg_schema if item['schema'].get('RelationType')
        })
        self.excluded_entity_types = []  # 专家删除（不需要）的实体类型，抽取时不再生成
        self.entity_type_dict = {name: [] for name in self.existing_entity_types}  # 实体类型及其实例
        self.relation_type_dict = {name: [] for name in self.existing_relation_types}  # 关系类型及其实例

    @staticmethod
    def load_prompt(filename: str) -> str:
        prompt_path = Path(__file__).resolve().parent / 'prompt' / filename
        return prompt_path.read_text(encoding='utf-8')

    async def chatresponse(self, prompt, api_key, base_url, model):
        response = await GenericResponseGetter.get_response(
            query=prompt,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        return response

    # 从各种文件中读取分割后的数据
    @classmethod
    def file_load(cls, file_path_list):
        """
        从各种类型的文件中读取文本
        """
        chunks = []
        tool = FileLoader()
        for file_path in file_path_list:
            content = tool.load(file_path)
            chunks.extend([chunk for chunk in content[0].values()])
        return chunks

    async def extract_from_path(
        self,
        file_path_list: list,
        aim: str,
        info: dict,
        directional_suggestion: str,
        api_key: str,
        base_url: str,
        model: str,
        embedding_api_key: str,
        embedding_base_url: str,
        embedding_model: str,
        progress_callback=None,
    ) -> object:
        # 输入参数
        # 1. path:提取文件的文件路径
        # 2. aim:构建知识图谱的核心目标（应用）
        # 3. info:字典形式为{"add_entity": [], "del_entity": []}，每个列表中填相应的增删类别
        # 将新的增删信息添加到总的增删信息中
        self.excluded_entity_types = [name for name in (info or {}).get('del_entity', []) if name]
        chunks = SchemaConstruction.file_load(file_path_list)
        # 过滤掉空的文本块
        filter_chunks = [chunk for chunk in chunks if chunk]
        # 判断输入文本是中文还是英文
        language = 'Chinese' if is_chinese_more_than_english(filter_chunks[0][0]) else 'English'
        total_texts = sum(len(chunk) for chunk in filter_chunks)
        processed_texts = 0
        for chunk in filter_chunks:
            for text in chunk:
                await self.extract_kg_schema(
                    text,
                    aim,
                    directional_suggestion,
                    language,
                    api_key,
                    base_url,
                    model,
                    embedding_api_key,
                    embedding_base_url,
                    embedding_model,
                )
                processed_texts += 1
                if progress_callback:
                    progress_callback('extract', processed_texts, total_texts, len(self.kg_schema))
        # 对schema中的元素进行去重
        self.kg_schema = deduplicate_schema(self.kg_schema)
        # 过滤掉 source 为空字典的元素
        self.kg_schema = [i for i in self.kg_schema if i.get('source') != {}]
        definition_total = len(self.pending_definitions(self.entity_type_dict)) + len(
            self.pending_definitions(self.relation_type_dict)
        )
        if progress_callback:
            progress_callback('definitions', 0, definition_total, len(self.kg_schema))
        await self.type_definition(language, api_key=api_key, base_url=base_url, model=model)
        if progress_callback:
            progress_callback('definitions', definition_total, definition_total, len(self.kg_schema))
        return self.kg_schema, self.definition

    def pending_definitions(self, type_dict):
        """已有定义的类型（更新时沿用的原架构类型）不再重新定义"""
        return [(key, values) for key, values in type_dict.items() if key not in self.definition]

    # 对实体类型和关系类型进行定义
    async def type_definition(self, language, api_key, base_url, model: str):
        """
        Generate definitions for entity and relation types in batches of 10 (no progress bar)

        Args:
            api_key: API key for LLM service
            base_url: Base URL for API endpoint
            model: LLM model name
        """

        # ========= 实体类型定义（每10个键一批） =========
        entity_items = self.pending_definitions(self.entity_type_dict)
        for i in range(0, len(entity_items), 10):
            batch = entity_items[i : i + 10]

            # 拼接当前批次的输入字符串
            batch_str = '\n'.join(f'{key}: {", ".join(values)}' for key, values in batch)

            # 加载实体类型定义的提示词模板
            entity_type_define_prompt = Template(self.load_prompt('entity_type_define_agent.txt'))
            # 渲染提示词，填入实体类型字典字符串
            entity_type_define_prompt = entity_type_define_prompt.render(entity_type_dict_string=batch_str)

            # 调用大模型生成定义
            entity_type_define_response = await self.chatresponse(entity_type_define_prompt, api_key, base_url, model)

            # 解析响应并更新定义
            self.definition.update(extract_definition(entity_type_define_response))

        # ========= 关系类型定义（每10个键一批） =========
        relation_items = self.pending_definitions(self.relation_type_dict)
        for i in range(0, len(relation_items), 10):
            batch = relation_items[i : i + 10]

            # 拼接当前批次的输入字符串
            batch_str = '\n'.join(f'{key}: {", ".join(values)}' for key, values in batch)

            # 加载关系类型定义的提示词模板
            relation_type_define_prompt = Template(self.load_prompt('relation_type_define_agent.txt'))
            # 渲染提示词，填入关系类型字典字符串
            relation_type_define_prompt = relation_type_define_prompt.render(
                relation_type_dict_string=batch_str, language=language
            )

            # 调用大模型生成定义
            relation_type_define_response = await self.chatresponse(
                relation_type_define_prompt, api_key, base_url, model
            )

            # 解析响应并更新定义
            self.definition.update(extract_definition(relation_type_define_response))

    async def extract_kg_schema(
        self,
        text,
        aim,
        directional_suggestion,
        language,
        api_key,
        base_url,
        model: str,
        embedding_api_key: str,
        embedding_base_url: str,
        embedding_model: str,
    ):
        extract_triples_from_text_prompt = Template(self.load_prompt('extract_triples_from_text_agent.txt'))

        # 第一次调用大模型
        extract_triples_from_text_prompt = extract_triples_from_text_prompt.render(
            text=text, aim=aim, directional_suggestion=directional_suggestion, language=language
        )

        extract_triples_from_text_response = await self.chatresponse(
            extract_triples_from_text_prompt, api_key, base_url, model
        )

        # 从文本中提取三元组以及实体和关系
        Triple_source_dict, entity_string, relation_string = extract_triples_and_strings(
            extract_triples_from_text_response
        )

        entity_classify_prompt = Template(self.load_prompt('entity_classify_agent.txt'))

        entity_classify_prompt = entity_classify_prompt.render(
            entity_string=entity_string,
            language=language,
            existing_types=', '.join(self.existing_entity_types),
            excluded_types=', '.join(self.excluded_entity_types),
        )

        entity_classify_response = await self.chatresponse(entity_classify_prompt, api_key, base_url, model=model)
        # 专家删除的类型即使模型仍然输出也丢弃；其中的实体没有类型，相关三元组随之不进入架构
        new_entity_types = {
            name: entities
            for name, entities in get_new_entity_types_from_response(response=entity_classify_response).items()
            if name not in self.excluded_entity_types
        }

        # 更新实体类型字典
        if not self.kg_schema:
            self.entity_type_dict = new_entity_types
        else:
            temp_entity_type_dict = new_entity_types
            self.entity_type_dict = await merge_type_dicts_with_semantic(
                self.entity_type_dict,
                temp_entity_type_dict,
                embedding_api_key=embedding_api_key,
                embedding_base_url=embedding_base_url,
                embedding_model=embedding_model,
            )

        relation_classify_prompt = Template(self.load_prompt('relation_classify_agent.txt'))
        relation_classify_prompt = relation_classify_prompt.render(
            relation_string=relation_string, language=language, existing_types=', '.join(self.existing_relation_types)
        )

        relation_classify_response = await self.chatresponse(relation_classify_prompt, api_key, base_url, model=model)
        # 更新关系类型字典
        if not self.kg_schema:
            self.relation_type_dict = get_new_relationship_types_from_response(response=relation_classify_response)
        else:
            temp_relation_type_dict = get_new_relationship_types_from_response(response=relation_classify_response)
            self.relation_type_dict = await merge_type_dicts_with_semantic(
                self.relation_type_dict,
                temp_relation_type_dict,
                embedding_api_key=embedding_api_key,
                embedding_base_url=embedding_base_url,
                embedding_model=embedding_model,
            )
        entity_type_string = '，'.join(self.entity_type_dict.keys())
        attribute_reasoning_prompt = Template(self.load_prompt('attribute_reasoning.txt'))
        attribute_reasoning_prompt = attribute_reasoning_prompt.render(
            entity_type_string=entity_type_string, language=language
        )
        attribute_reasoning_response = await self.chatresponse(
            attribute_reasoning_prompt, api_key, base_url, model=model
        )
        entity_type_attribute_dict = get_entity_type_attributes_from_response(response=attribute_reasoning_response)

        kg_schema = transform_triplets_to_schema(
            Triple_source_dict, self.entity_type_dict, self.relation_type_dict, entity_type_attribute_dict
        )
        self.kg_schema.extend(kg_schema)
