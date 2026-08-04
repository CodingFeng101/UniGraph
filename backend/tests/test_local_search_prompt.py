from backend.common.core_layer.unigraph.module.sapperrag.retriver.structured_search.local_search.system_prompt import (
    LOCAL_SEARCH_SYSTEM_PROMPT,
)


def test_prompt_allows_disclosed_general_knowledge_fallback() -> None:
    assert 'answer from general knowledge instead of replying only that you do not know' in LOCAL_SEARCH_SYSTEM_PROMPT
    assert '未在当前知识图谱中找到足以回答该问题的相关信息' in LOCAL_SEARCH_SYSTEM_PROMPT


def test_prompt_keeps_general_knowledge_separate_from_graph_citations() -> None:
    assert (
        'Never attach a [Data: ...] citation to content based only on general knowledge' in LOCAL_SEARCH_SYSTEM_PROMPT
    )
    assert 'cite only the graph-backed part' in LOCAL_SEARCH_SYSTEM_PROMPT
