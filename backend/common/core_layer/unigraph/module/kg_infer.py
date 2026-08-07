import asyncio
import random
from typing import Dict, List, Tuple

from celery import Task
from tqdm import tqdm

from backend.common.task_progress import scaled_progress, should_report, task_progress
from backend.core.conf import settings

from ..ai_unit.executor.ai_executor import AIExecutor


class SemanticKGInfer:
    def __init__(self):
        self.ai_executor = AIExecutor()

    async def _process_mask_triple(
        self,
        masked_triple: Tuple,
        type_triple: Tuple,
        entity_type_attributes: Dict,
        api_key: str,
        base_url: str,
        model: str,
    ):
        """
        处理遮盖三元组
        """
        result = await self.ai_executor.execute(
            self,
            masked_triple=masked_triple,
            entity_type_attributes=entity_type_attributes,
            type_triple=type_triple,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        return result

    @staticmethod
    def _get_kg_attribute_keys(triple_index: int, kg: List) -> Dict:
        """
        : param triple_index: 三元组索引
        : param kg: KG
        : return: 实体类型-属性键列表 字典
        获取指定索引下三元组的属性键，还是以类型作为键
        """
        attribute_keys = dict()
        target_triple = kg[triple_index]  # 获取被推理三元组
        target_triple['DirectedEntity']['Attributes'].pop('index', None)
        target_triple['DirectionalEntity']['Attributes'].pop('index', None)
        attribute_keys[target_triple['DirectionalEntity']['Type']] = list(
            target_triple['DirectionalEntity']['Attributes'].keys()
        )
        attribute_keys[target_triple['DirectedEntity']['Type']] = list(
            target_triple['DirectedEntity']['Attributes'].keys()
        )
        return attribute_keys

    @staticmethod
    def _fix_attributes(mask_triple_index: int, triple: Dict, infer_triple: Dict):
        """
        补全未经推理实体的属性
        : param mask_triple_index: 遮盖元素的索引 0->DirectionalEntity, 2->DirectedEntity
        : param triple: KG中的三元组
        : param infer_triple: 推理后的三元组
        : return: 补全属性后的三元组
        """
        if mask_triple_index == 0:  # 补全DirectedEntity的属性
            infer_triple['DirectedEntity']['Attributes'] = triple['DirectedEntity']['Attributes']
        if mask_triple_index == 1:  # 补全两个实体的属性
            infer_triple['DirectedEntity']['Attributes'] = triple['DirectedEntity']['Attributes']
            infer_triple['DirectionalEntity']['Attributes'] = triple['DirectionalEntity']['Attributes']
        elif mask_triple_index == 2:  # 补全DirectionalEntity的属性
            infer_triple['DirectionalEntity']['Attributes'] = triple['DirectionalEntity']['Attributes']
        return infer_triple

    @staticmethod
    def random_slice(lst, slice_length):
        """
        Randomly slice a list
        """
        if slice_length > len(lst):
            return 'Error: slice length is greater than list length.'
        start = random.randint(0, len(lst) - slice_length)
        return lst[start : start + slice_length]

    async def infer_kg(
        self,
        kg: List,
        api_key: str,
        base_url: str,
        model: str,
        task_client: Task,
    ):
        """
        Inference KG with real-time progress updates
        :param kg: Knowledge Graph to be inferred
        :param api_key: API key for the inference service
        :param base_url: Base URL for the inference service
        :param model: Model to use for inference
        :param task_client: Task client for managing tasks
        :return: Inferred knowledge graph
        """
        # Prepare masked KG and type KG
        masked_kg = []
        type_kg = []
        for triple in kg:
            directional_e_mask_triple = ('?', triple['Relation']['Name'], triple['DirectedEntity']['Name'])
            relation_mask_triple = (triple['DirectionalEntity']['Name'], '?', triple['DirectedEntity']['Name'])
            directed_e_mask_triple = (triple['DirectionalEntity']['Name'], triple['Relation']['Name'], '?')
            masked_kg.append([directional_e_mask_triple, relation_mask_triple, directed_e_mask_triple])
            type_kg.append((
                triple['DirectionalEntity']['Type'],
                triple['Relation']['Type'],
                triple['DirectedEntity']['Type'],
            ))

        # Initialize progress bar
        progress_bar = tqdm(total=len(kg) * 3, desc='Inferencing KG')  # 3 tasks per triple

        # Process inference tasks with real-time updates
        infer_kg = []
        tasks = []
        inference_slots = asyncio.Semaphore(settings.LLM_MAX_CONCURRENCY)

        async def process_with_progress(
            masked_triple, type_triple, attributes, api_key, base_url, model, index, index_
        ):
            try:
                async with inference_slots:
                    result = await asyncio.wait_for(
                        self._process_mask_triple(masked_triple, type_triple, attributes, api_key, base_url, model),
                        timeout=120,
                    )
                return result, index, index_
            finally:
                progress_bar.update(1)  # Update progress bar when task completes
                if should_report(progress_bar.n, progress_bar.total):
                    task_progress(
                        task_client,
                        '正在推理缺失实体与关系',
                        scaled_progress(progress_bar.n, progress_bar.total, 18, 72),
                        detail=f'已完成 {progress_bar.n}/{progress_bar.total} 个推理单元',
                        metrics={'units_done': progress_bar.n, 'units_total': progress_bar.total},
                    )

        for index, masked_triple_list in enumerate(masked_kg):
            type_triple = type_kg[index]
            entity_type_attributes = self._get_kg_attribute_keys(index, kg)
            if not entity_type_attributes:
                progress_bar.update(3)  # Skip this triple (3 tasks)
                task_progress(
                    task_client,
                    '跳过无法推理的三元组',
                    scaled_progress(progress_bar.n, progress_bar.total, 18, 72),
                    detail=f'已检查 {progress_bar.n}/{progress_bar.total} 个推理单元',
                    metrics={'units_done': progress_bar.n, 'units_total': progress_bar.total},
                )
                continue

            for index_, one_masked_triple in enumerate(masked_triple_list):
                task = process_with_progress(
                    one_masked_triple, type_triple, entity_type_attributes, api_key, base_url, model, index, index_
                )
                tasks.append(task)

        # Process results as they complete
        for future in asyncio.as_completed(tasks):
            result, index, index_ = await future
            if result:
                infer_triple = [self._fix_attributes(index_, kg[index], result_triple) for result_triple in result]
                infer_kg.extend(infer_triple)

        progress_bar.close()
        return infer_kg
