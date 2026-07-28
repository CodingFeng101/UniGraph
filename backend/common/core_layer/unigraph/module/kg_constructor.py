import asyncio
import logging
import os
from typing import Dict, List, Tuple

from celery import Task
from tqdm import tqdm

from backend.common.task_progress import scaled_progress, should_report, task_progress

from ..ai_unit.executor.ai_executor import AIExecutor
from ..file.file_loader import FileLoader

logger = logging.getLogger(__name__)


class SemanticKGConstructor:
    def __init__(self, kg_schema: List, schema_definition: Dict):
        self.kg_schema = self._convert_schema2old_format(kg_schema)
        # self.kg_schema = kg_schema
        self.schema_definition = schema_definition
        self.file_loader = FileLoader()
        self.ai_executor = AIExecutor()

    @staticmethod
    def _convert_schema2old_format(schema_data):
        """
        将新格式的schema数据转换为旧格式，保持功能不变
        """
        old_schema_data = []
        for type_triple in schema_data:
            try:
                old_schema = type_triple['schema']
                old_schema_data.append(old_schema)
            except KeyError:
                continue

        return old_schema_data

    async def _process_chunk(
        self,
        chunk,
        api_key: str,
        base_url: str,
        model: str,
    ):
        """
        处理文本块
        """
        result = await self.ai_executor.execute(
            self,
            chunk=chunk,
            kg_schema=self.kg_schema,
            schema_definition=self.schema_definition,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        return result

    async def extract_kg(
        self,
        dir_path: str,
        api_key: str,
        base_url: str,
        model: str,
        task_client: Task,
    ) -> Tuple[List, List, List]:
        """
        提取指定类型文件的KG
        """
        # Create index:content dictionary && structure KG
        all_index_content = dict()
        structure_kg = list()
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                # 读取文件内容
                index_content, structure_kg_ = self.file_loader.load(file_path)
                all_index_content.update(index_content)
                structure_kg.extend(structure_kg_)

        # 将文本字典解包，遍历每个键值对并对值进行类型判断，如果是列表则将其并入当前文本总列表中
        all_chunks = []
        for key, value in all_index_content.items():
            if isinstance(value, list):
                all_chunks.extend(value)
            else:
                all_chunks.append(value)

        logger.info(f'Extracting KG with {len(all_chunks)} chunks')  # debug提取所得

        if not structure_kg:
            structure_kg.append({'message': 'No structure KG extracted'})  # No structure KG extracted=
        kg = list()
        triple_sources = list()

        # 创建任务列表
        tasks = [self._process_chunk(chunk, api_key, base_url, model) for chunk in all_chunks]

        # 使用tqdm创建进度条
        with tqdm(total=len(tasks), desc=f'Processing text chunks count {len(all_chunks)}') as pbar:
            # 使用as_completed实时获取完成的任务
            for completed_task in asyncio.as_completed(tasks):
                triples, triple_source = await completed_task
                if triples:  # 确保非空值被添加进容器中
                    kg.extend(triples)
                if triple_source:
                    triple_sources.extend(triple_source)
                # 每完成一个任务就更新进度条
                pbar.update(1)
                if should_report(pbar.n, pbar.total):
                    task_progress(
                        task_client,
                        '正在抽取实体与关系',
                        scaled_progress(pbar.n, pbar.total, 18, 62),
                        detail=f'已分析 {pbar.n}/{pbar.total} 个文档片段，累计得到 {len(kg)} 条三元组',
                        metrics={'chunks_done': pbar.n, 'chunks_total': pbar.total, 'triples': len(kg)},
                    )

        return kg, structure_kg, triple_sources
