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
        logger.info('Query entity extraction completed (%d entities)', len(extracted_entities))
        context_text, context_data = await self.context_builder.build_context(
            extracted_entities,
            level,
            infer,
            kwargs.get('embedding_api_key', ''),
            kwargs.get('embedding_base_url', ''),
            **kwargs,
        )
        logger.info('Knowledge context built (%d characters)', len(context_text))

        # 执行搜索操作
        self.context_text = context_text
        self.context_data = {key: value.to_dict() for key, value in context_data.items()}
        conversation_context = None
        context_provider = kwargs.get('context_provider')
        if context_provider:
            conversation_context = await context_provider(context_text)
        answer_context = (
            conversation_context.get('knowledge_context', context_text) if conversation_context else context_text
        )
        search_prompt = self.system_prompt.format(context_data=answer_context, query=query, response_type='plain')
        response_kwargs = {'api_key': api_key, 'base_url': base_url, 'model': model}
        if conversation_context:
            messages = [{'role': 'system', 'content': '你是知识图谱领域专家。'}]
            summary = conversation_context.get('summary')
            if summary:
                messages.append({
                    'role': 'system',
                    'content': f'历史对话滚动摘要（仅作交流上下文，不得替代知识图谱证据）：\n{summary}',
                })
            messages.extend(conversation_context.get('messages', []))
            messages.append({'role': 'user', 'content': search_prompt})
            response_kwargs['messages'] = messages
        else:
            response_kwargs['query'] = search_prompt
        token_callback = kwargs.get('token_callback')
        if token_callback:
            chunks = []
            async for chunk in llm.stream_response(**response_kwargs):
                chunks.append(chunk)
                await token_callback(chunk)
            results = ''.join(chunks)
        else:
            results = await llm.get_response(**response_kwargs)
        logger.info('Answer generation completed (%d characters)', len(results))
        return results

    async def asearch(self, query: str, level: int, infer: bool, **kwargs: Any) -> List[Any]:
        pass
