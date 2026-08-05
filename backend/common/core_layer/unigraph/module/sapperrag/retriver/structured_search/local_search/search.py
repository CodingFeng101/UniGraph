import logging
from typing import Any, List

from .......unigraph.ai_unit.llm.response_getter import GenericResponseGetter
from ....retriver.context_builder.builders import LocalContextBuilder
from ....retriver.context_builder.entity_extraction import extract_entities_from_query
from ....retriver.structured_search.base import BaseSearch
from ....retriver.structured_search.local_search.system_prompt import LOCAL_SEARCH_SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _context_records(context_data: dict, source_type: str, limit: int = 24) -> dict:
    frame = context_data.get(source_type)
    records = frame.to_dict(orient='records') if frame is not None else []
    normalized = [
        {str(key): '' if value is None else str(value) for key, value in record.items()} for record in records[:limit]
    ]
    return {
        'source_type': source_type,
        'total': len(records),
        'items': normalized,
        'truncated': len(records) > limit,
    }


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
        progress_callback = kwargs.get('progress_callback')
        if progress_callback:
            labels = {
                'Entities': ('实体检索完成', '个实体'),
                'Relationships': ('关系检索完成', '条关系'),
                'Sources': ('信息源检索完成', '条原文片段'),
                'Reports': ('社区报告检索完成', '份社区报告'),
            }
            for source_type in ('Entities', 'Relationships', 'Sources', 'Reports'):
                payload = _context_records(context_data, source_type)
                if not payload['total']:
                    continue
                message, unit = labels[source_type]
                suffix = '，仅展示前 24 条' if payload['truncated'] else ''
                await progress_callback(
                    message,
                    f'本次检索到 {payload["total"]} {unit}{suffix}',
                    payload,
                )
        conversation_context = None
        context_provider = kwargs.get('context_provider')
        if context_provider:
            conversation_context = await context_provider(context_text)
        answer_context = (
            conversation_context.get('knowledge_context', context_text) if conversation_context else context_text
        )
        question_context = conversation_context.get('question_context', '') if conversation_context else ''
        answer_query = f'{query}{question_context}'
        search_prompt = self.system_prompt.format(
            context_data=answer_context,
            query=answer_query,
            response_type='plain',
        )
        response_kwargs = {'api_key': api_key, 'base_url': base_url, 'model': model}
        if conversation_context:
            messages = [{'role': 'system', 'content': '你是知识图谱领域专家。'}]
            summary = conversation_context.get('summary')
            if summary:
                messages.append({
                    'role': 'system',
                    'content': (
                        '历史对话滚动摘要（用于理解指代和延续上下文；'
                        f'其中用户明确提供的信息可以作为对话上下文，但不得伪装成知识图谱证据）：\n{summary}'
                    ),
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
