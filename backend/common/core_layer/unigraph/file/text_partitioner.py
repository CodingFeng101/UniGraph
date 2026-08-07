import re
from typing import Dict, List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter


class LangChainSplitter:
    def __init__(self, partition_size: int, partition_overlap: int):
        self.partition_size = partition_size
        self.partition_overlap = partition_overlap

    def split(self, content):
        split_chunks = RecursiveCharacterTextSplitter(
            # 文本块适中调整
            chunk_size=self.partition_size,
            chunk_overlap=self.partition_overlap,
            strip_whitespace=True,
        ).split_text(content)
        index_content = {}
        for index, chunk in enumerate(split_chunks):
            index_content[index] = chunk
        return index_content


class MarkDownParser:
    @staticmethod
    def parse_md_content_to_index_dict(file_name: str, md_content: str):
        """
        尝试解析md文档内容，解析成index: content
        如果结果为空则代表输入的文本不包含任何md语法结构，转由LangChainSplitter处理为num_index: content
        同时注意，index: content中的content在TextPartitioner中会被进一步检测分割，因此LangChainSplitter是始终会被调用的
        """
        lines = md_content.split('\n')
        result = {}
        current_path = []

        # 解析md语法内容，解析成index: content
        for line in lines:
            if line.startswith('#'):
                # 计算标题的级别
                level = len(re.match(r'^#+', line).group())
                # 获取标题文本
                title = line.strip('#').strip()
                # 更新当前路径
                if level == 1:
                    current_path = [f'{file_name}->{title}']
                elif level == 2:
                    current_path = current_path[:1] + [title]
                elif level == 3:
                    current_path = current_path[:2] + [title]
            else:
                # 非标题行，属于当前路径的内容
                key = '->'.join(current_path)
                if key in result:
                    result[key] += f'\n{line.strip()}'
                else:
                    result[key] = line.strip()  # if not in result, add new key
        return result

    @staticmethod
    def parse_markdown_headings(markdown_text):
        headings = re.findall(r'^(#{1,6}) (.*)', markdown_text, re.MULTILINE)
        parsed_headings = []
        for level, heading in headings:
            parsed_headings.append((len(level), heading))
        return parsed_headings

    @staticmethod
    def generate_kg_triples(parsed_headings):
        triples = []
        stack = []
        for level, heading in parsed_headings:
            current_entity = heading
            while stack and stack[-1][0] >= level:
                stack.pop()
            if stack:
                parent = stack[-1][1]
                triples.append((parent, 'has', current_entity))
            stack.append((level, current_entity))
        return triples

    @staticmethod
    def convert_to_custom_triples(
        triples, index_content_dict, directional_type='内容', directed_type='内容', relation_type='包含'
    ):
        """
        将 RDF 三元组转换为指定格式的三元组结构。
        参数
        :param triples: list: 包含 RDF 三元组的列表。
        :param directional_type: str: 指定 DirectionalEntity 的类型。
        :param directed_type: str: 指定 DirectedEntity 的类型。
        :param relation_type: str: 指定 Relation 的类型。
        :param index_content_dict: dict: 包含 index: content
        return: list: 包含转换后格式的三元组列表。
        """
        # 解析index_content_dict，将键转为->分隔字符串的最后缀替换为新键，没->则不动该键
        new_index_content_dict = {}
        for key, value in index_content_dict.items():
            if '->' in key:
                new_key = key.split('->')[-1]
                new_index_content_dict[new_key] = value
            else:
                new_index_content_dict[key] = value

        # 构建结构KG
        converted_triples = []
        for triple in triples:
            directional_entity, relation, directed_entity = triple
            converted_triple = {
                'DirectionalEntity': {
                    'Type': directional_type,
                    'Name': directional_entity,
                    'Attributes': {'text': new_index_content_dict.get(directional_entity, '')},
                },
                'Relation': {'Type': relation_type, 'Name': relation, 'Attributes': {}},
                'DirectedEntity': {
                    'Type': directed_type,
                    'Name': directed_entity,
                    'Attributes': {'text': new_index_content_dict.get(directed_entity, '')},
                },
            }
            converted_triples.append(converted_triple)
        return converted_triples

    @staticmethod
    def parse_docx2index_content(file_name: str, md_content: str):
        """
        解析md文档，转成index: content
        """
        index_content_dict = MarkDownParser.parse_md_content_to_index_dict(file_name, md_content)
        # 优先进行md解析，如果为空则进行常规文本分割
        return index_content_dict

    @staticmethod
    def get_structure_kg(index_content_dict, md_content):
        # 解析md语法文本行，得到heading结构
        parsed_headings = MarkDownParser.parse_markdown_headings(md_content)
        # 生成KG
        triples = MarkDownParser.convert_to_custom_triples(
            MarkDownParser.generate_kg_triples(parsed_headings), index_content_dict
        )
        return triples


class TextPartitioner:
    def __init__(self):
        self.lang_chain_splitter = LangChainSplitter(partition_size=1500, partition_overlap=200)
        self.md_parser = MarkDownParser()

    def partition(self, content):
        """
        文本切割，针对包含特殊层级标题行的docx，需额外构建结构KG，否则该项为空，并且仅采用一层常规切割策略。
        :param content: 文件内容
        """
        return self.lang_chain_splitter.split(content)

    def pre_partition(self, file_name: str, content: str) -> Dict | Tuple[Dict, List]:
        """
        文本预切割，处理md文本中的标题行，转为以标题行为索引的文本块哈希表
        对纯文本内容进行切割，优先进行md解析 -> 检测并切割content
        否则直接对整个content切割
        """
        # md解析
        index_content_dict = self.md_parser.parse_docx2index_content(file_name, content)
        return index_content_dict

    def load_structure_kg(self, index_content_dict, content):
        """
        :param index_content_dict: 接收docx "标题索引: 标题拥有内容" 哈希表
        :param content: 文件内容
        """
        triples = self.md_parser.get_structure_kg(index_content_dict=index_content_dict, md_content=content)
        return triples
