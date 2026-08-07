import asyncio
import json
import logging

from tqdm.asyncio import tqdm_asyncio

from .......unigraph.ai_unit.llm.response_getter import GenericResponseGetter
from .......unigraph.module.llm_output_checks import clamp_rating, strip_json_fences
from ....index.graph.promt.report_generate import REPORT_GENERATE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CommunityReportGenerator:
    def __init__(self, input_data):
        self.input_data = input_data
        self.prompt_template = REPORT_GENERATE

    async def _process_single_community(self, index, community_df, llm, max_retries, api_key, base_url, model):
        """
        带指数退避的重试机制处理单个社区

        :param index: 社区索引
        :param community_df: 社区数据
        :param llm: LLM对象
        :param max_retries: 最大重试次数
        :return: 处理后的社区索引和响应内容
        """

        backoff_factor = 1
        for attempt in range(max_retries):
            try:
                # 生成报告内容
                community = f'{community_df.title} ({community_df.id}): {community_df.full_content}'
                response = await llm.get_response(
                    query=self.prompt_template.format(input_text=community),
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                )

                # 处理响应结果
                clean_response = strip_json_fences(response)
                report_data = json.loads(clean_response)

                # 更新社区数据
                self.input_data[index].full_content = clean_response
                self.input_data[index].title = report_data.get('title', '')
                self.input_data[index].rating = clamp_rating(report_data.get('rating', 0))

                logger.info(f'Processing community {index}: {community_df.id}')
                return index, clean_response

            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f'Failed to process community {index}: {str(e)}')
                    raise
                await asyncio.sleep(backoff_factor * (2**attempt))
        return index, None

    async def generate_reports(
        self, max_retries=6, concurrent_tasks=50, api_key='', base_url='', model='', progress_callback=None
    ):
        """
        并发处理社区报告生成

        :param max_retries: 最大重试次数
        :param concurrent_tasks: 并发任务数
        """
        llm = GenericResponseGetter()
        semaphore = asyncio.Semaphore(concurrent_tasks)  # 控制并发量

        async def bounded_task(index, community, api_key, base_url, model):
            async with semaphore:
                return await self._process_single_community(
                    index, community, llm, max_retries, api_key, base_url, model
                )

        # 创建任务列表
        tasks = [
            bounded_task(index, community, api_key, base_url, model) for index, community in enumerate(self.input_data)
        ]

        # 使用带进度条的并发执行
        results = []
        try:
            total = len(tasks)
            for task in tqdm_asyncio.as_completed(tasks, desc='生成报告'):
                result = await task
                results.append(result)
                if progress_callback:
                    index, _ = result
                    progress_callback(len(results), total, self.input_data[index])
        except Exception as e:
            logger.critical(f'Critical error occurred: {str(e)}', exc_info=True)
            raise

        return self.input_data
