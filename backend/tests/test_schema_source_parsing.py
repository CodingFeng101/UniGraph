import _env  # noqa: F401  # isort: skip
from backend.app.kgbase.api.v1.kgbase.schema_graph import _collect_entity_sources, _parse_json_value


def schema_item(source):
    return {
        'schema': {
            'DirectionalEntityType': {'Name': 'Person'},
            'RelationType': 'works_at',
            'DirectedEntityType': {'Name': 'Company'},
        },
        'source': source,
    }


def test_collect_entity_sources_accepts_standard_triples() -> None:
    sources = _collect_entity_sources([
        schema_item({'(Alice, works_at, UniGraph)': 'Alice works at UniGraph'}),
        schema_item({'(Bob,works_at,OpenAI)': 'Bob works at OpenAI'}),
    ])

    assert sources == {
        'Person': ['Alice', 'Bob'],
        'Company': ['UniGraph', 'OpenAI'],
    }


def test_collect_entity_sources_falls_back_for_malformed_triples(caplog) -> None:
    sources = _collect_entity_sources([
        schema_item({'(Alice, works_at)': 'missing target'}),
        schema_item({'(Alice)': 'missing relation and target'}),
        schema_item({}),
        schema_item('not-a-mapping'),
    ])

    assert sources == {
        'Person': ['Person'],
        'Company': ['Company'],
    }
    assert 'Malformed schema source triple' in caplog.text
    assert 'Missing schema source mapping' in caplog.text


def test_collect_entity_sources_deduplicates_values() -> None:
    sources = _collect_entity_sources([
        schema_item({'(Alice, works_at, UniGraph)': 'first'}),
        schema_item({'(Alice, works_at, UniGraph)': 'second'}),
    ])

    assert sources == {'Person': ['Alice'], 'Company': ['UniGraph']}


def test_parse_json_value_accepts_json_empty_and_plain_text() -> None:
    assert _parse_json_value('{"name": "UniGraph"}', {}) == {'name': 'UniGraph'}
    assert _parse_json_value('["source"]', []) == ['source']
    assert _parse_json_value('', {}) == {}
    assert _parse_json_value(None, []) == []
    assert _parse_json_value('manual', []) == 'manual'
