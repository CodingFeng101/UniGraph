import csv
import json
import os
from typing import Dict, List, Tuple

from .content_getter import FileContentGetterFactory
from .text_partitioner import TextPartitioner


class FileLoader:
    """
    加载Docx、PDF、TXT文本内容，并尝试解析为结构化KG
    必要结果为index: content
    """

    def __init__(self):
        self.text_partitioner = TextPartitioner()
        self.file_content_getter_factory = FileContentGetterFactory()

    def load(self, file_path: str) -> Dict | Tuple[Dict, List]:
        """
        加载文件内容，尝试解析为结构化KG
        :param file_path: 文件路径
        return: index-content 可选(index kg.json)
        """
        # 读取文件内容
        content = self.read_file(file_path)

        # 预切割，尝试得到 文档标题索引文本块哈希表
        md_index_content_dict = self.pre_partition(content, os.path.basename(file_path))

        # 若不包含md内容，则直接普通切割并返回
        if not md_index_content_dict:
            return self.partition(content), []  # 结构KG为空

        # 否则解析结构kg并返回
        else:
            structure_kg = self.text_partitioner.load_structure_kg(
                index_content_dict=md_index_content_dict, content=content
            )
            index_content_dict = {}
            # 注意这种情况下，每个标题索引对应的文本块可能会超tokens，需要再进行切割
            for heading_index, index_content in md_index_content_dict.items():
                num_index_content_dict = self.text_partitioner.partition(content=index_content)
                chunks = list(num_index_content_dict.values())
                index_content_dict[heading_index] = chunks

            return index_content_dict, structure_kg

    def read_file(self, file_path: str) -> str:
        """
        读取文件内容
        :param file_path: 文件路径
        """
        content_getter = self.file_content_getter_factory.create(file_path)
        return content_getter.get_content(file_path)

    def partition(self, content: str) -> Dict | Tuple[Dict, List]:
        """
        分割文本内容
        """
        return self.text_partitioner.partition(content=content)

    def load_structure_kg(self, index_content_dict, content):
        return self.text_partitioner.load_structure_kg(index_content_dict=index_content_dict, content=content)

    def pre_partition(self, content, file_name):
        return self.text_partitioner.pre_partition(file_name, content)


class FileStorage:
    @staticmethod
    def store_kg(file_kg_data: List, store_dir_path: str, file_name):
        """
        存储文件KG数据
        """
        try:
            with open(os.path.join(store_dir_path, file_name), 'w', encoding='utf-8') as f:
                json.dump(file_kg_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f'Error: {e}')

    @staticmethod
    def store_kg_source(kg_source: List[Dict], store_dir_path: str, file_name, csv_header: List = None):
        """
        存储文件KG数据源
        """
        if not csv_header:
            csv_header = ['ID', 'TripleSource']

        with open(os.path.join(store_dir_path, file_name), mode='w', newline='', encoding='utf-8') as fo:
            # 定义字段名
            fields = csv_header if csv_header else ['ID', 'TripleSource']
            dic_writer = csv.DictWriter(fo, fieldnames=fields)
            # 写入表头：
            dic_writer.writeheader()
            # 写入数据行：
            for triple_source in kg_source:
                dic_writer.writerow(triple_source)
