import logging
from typing import Any, List

from .......unigraph.ai_unit.llm.response_getter import GenericResponseGetter
from ....retriver.context_builder.builders import LocalContextBuilder
from ....retriver.context_builder.entity_extraction import extract_entities_from_query
from ....retriver.structured_search.base import BaseSearch
from ....retriver.structured_search.local_search.system_prompt import LOCAL_SEARCH_SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LocalSearch(BaseSearch):
    """本地搜索类"""

    def __init__(
        self,
        context_builder: LocalContextBuilder,
        system_prompt: LOCAL_SEARCH_SYSTEM_PROMPT,
    ):
        super().__init__(context_builder=context_builder)
        self.system_prompt = system_prompt
        self.context_data = dict[str, dict]()
        self.context_text = ''

    async def search(self, query: str, level: int, infer: bool, api_key: str, base_url: str, model: str, **kwargs: Any):
        """
        执行搜索操作

        :param query: 用户输入的问题
        :param level: 查询深度
        :param infer: 是否进行推理
        :param kwargs: 其他参数
        :return: 查询结果
        """
        llm = GenericResponseGetter()
        extracted_entities = await extract_entities_from_query(query, llm, api_key, base_url, model)
        logger.info(f'实体{extracted_entities}抽取成功😊')
        context_text, context_data = await self.context_builder.build_context(
            extracted_entities, level, infer, api_key, base_url, **kwargs
        )
        logger.info(f'上下文{context_text}构建成功😊')

        # 执行搜索操作
        self.context_text = context_text
        self.context_data = {key: value.to_dict() for key, value in context_data.items()}
        search_prompt = self.system_prompt.format(context_data=context_text, query=query, response_type='plain')
        results = await llm.get_response(query=search_prompt, api_key=api_key, base_url=base_url, model=model)
        logger.info(f'搜索结果{results}获取成功😊')
        return results

    async def asearch(self, query: str, level: int, infer: bool, **kwargs: Any) -> List[Any]:
        pass
