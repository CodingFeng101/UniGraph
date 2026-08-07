import pandas as pd
from backend.common.core_layer.unigraph.module.sapperrag.retriver.structured_search.local_search.search import (
    _context_records,
)


def test_context_records_builds_bounded_retrieval_progress_payload() -> None:
    frame = pd.DataFrame([
        {'id': index, 'entity_type': '模块', 'entity_name': f'实体 {index}', 'text': f'说明 {index}'}
        for index in range(3)
    ])

    payload = _context_records({'Entities': frame}, 'Entities', limit=2)

    assert payload == {
        'source_type': 'Entities',
        'total': 3,
        'items': [
            {'id': '0', 'entity_type': '模块', 'entity_name': '实体 0', 'text': '说明 0'},
            {'id': '1', 'entity_type': '模块', 'entity_name': '实体 1', 'text': '说明 1'},
        ],
        'truncated': True,
    }
