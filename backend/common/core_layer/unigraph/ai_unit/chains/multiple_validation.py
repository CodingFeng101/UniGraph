# from core.app.api.v1.api import api_router
import re
from typing import Tuple

from ...web_search.search_pipeline import SearchAndScrapePipeLine
from ...web_search.web_source_selector import WebSourceSelector
from ..llm.response_getter import ResponseGetter
from ..query_template.validation_templates import (
    ClaimTemplate,
    EntityKnowledgeTemplate,
    GenerateOptionTemplate,
    GenerationTemplate,
    JudgementTemplate,
)


async def run_knowledge_extraction(entity: str, ai_response_getter: ResponseGetter, api_key: str, base_url: str) -> str:
    """
    运行知识提取
    """
    return ai_response_getter.get_response(
        query=EntityKnowledgeTemplate.render_template(entity=entity), api_key=api_key, base_url=base_url
    )


async def run_claim_validation(
    ai_response_getter: ResponseGetter,
    inferred_triple: Tuple,
    api_key: str,
    base_url: str,
):
    """
    运行断言验证
    """
    directional_e, relation, directed_e = inferred_triple
    # get entity domain knowledge
    directional_e_domain_knowledge = await run_knowledge_extraction(
        directional_e,
        ai_response_getter,
        api_key,
        base_url,
    )
    directed_e_domain_knowledge = await run_knowledge_extraction(
        directed_e,
        ai_response_getter,
        api_key,
        base_url,
    )
    domain_knowledge = '\n'.join([directional_e_domain_knowledge, directed_e_domain_knowledge])
    # render claim template
    query = ClaimTemplate.render_template(domain_knowledge=domain_knowledge, inferred_triple=inferred_triple)
    # get response
    response = await ai_response_getter.get_response(
        query=query,
        api_key=api_key,
        base_url=base_url,
    )

    return True if 'correct' in response.lower() else False


async def run_judgement_validation(
    ai_response_getter: ResponseGetter, inferred_triple: Tuple, api_key: str, base_url: str
):
    """
    运行判断验证
    """
    choices = await ai_response_getter.get_response(
        query=GenerateOptionTemplate.render_template(f'{inferred_triple[0]}, {inferred_triple[2]}'),
        api_key=api_key,
        base_url=base_url,
    )
    query = JudgementTemplate.render_template(
        infer_triple=f'({inferred_triple[0]}, ?, {inferred_triple[2]})',
        choices=', '.join([choices, inferred_triple[1]]),
    )
    response = await ai_response_getter.get_response(
        query=query,
        api_key=api_key,
        base_url=base_url,
    )
    return True if response == inferred_triple[1] else False


async def run_generation_validation(
    ai_response_getter: ResponseGetter, inferred_triple: Tuple, api_key: str, base_url: str
):
    """
    运行生成验证
    """
    query = GenerationTemplate.render_template(inferred_triple)
    response = await ai_response_getter.get_response(
        query=query,
        api_key=api_key,
        base_url=base_url,
    )

    return True if response.lower() != 'no' else False


def mixed_language_sentence_segmenter(web_content: list):
    """
    处理混合语言的文本，使用标点符号进行句子分割。
    Args:
        web_content (str): 输入文本，可能包含中英、法德混合句子。
    Returns:
        List[str]: 分句后的句子列表。
    """
    # 匹配常见的中英法德标点符号，作为句子分割的依据
    rag_web_content_list = []
    for web_source in web_content:
        url = web_source['url']
        whole_content = web_source['content']
        sentence_endings = re.compile(r'(?<=[.!?！？。])\s*')
        sentences = sentence_endings.split(whole_content)
        rag_web_content_list.extend([{'content': sentence, 'url': url} for sentence in sentences])

    # 过滤掉空白句子，并去掉首尾多余空格
    return rag_web_content_list


async def run_validation(
    ai_response_getter: ResponseGetter = None,
    inferred_triple: Tuple = None,
    api_key: str = None,
    base_url: str = None,
):
    """
    参数待定，应该是单个验证三元组，这里防止验证逻辑的执行
    仅验证单个三元组

    """
    # first run web search and scrape pipeline
    search_context = SearchAndScrapePipeLine()  # ensure config is correct
    search_result = await search_context.run(' AND '.join(inferred_triple))  # bool search -> dict

    related_paragraphs = WebSourceSelector.select_sentences(
        mixed_language_sentence_segmenter(search_result), inferred_triple
    )

    if related_paragraphs:
        return True, related_paragraphs
    else:
        if (
            await run_claim_validation(ai_response_getter, inferred_triple, api_key, base_url)
            and await run_judgement_validation(ai_response_getter, inferred_triple, api_key, base_url)
            and await run_generation_validation(ai_response_getter, inferred_triple, api_key, base_url)
        ):
            return True, related_paragraphs  # related paragraphs is empty
        else:
            return False, related_paragraphs
