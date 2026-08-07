import asyncio

from backend.common.core_layer.unigraph.module.schema_construction.schema_construction import SchemaConstruction


def test_extract_reports_definition_progress_for_relation_types(monkeypatch) -> None:
    construction = SchemaConstruction(kg_schema=[], definition={})
    progress = []

    monkeypatch.setattr(SchemaConstruction, 'file_load', lambda _: [['example text']])

    async def extract_schema(*args, **kwargs) -> None:
        construction.entity_type_dict = {'Person': ['Alice']}
        construction.relation_type_dict = {'knows': ['Alice knows Bob']}

    async def define_types(*args, **kwargs) -> None:
        return None

    monkeypatch.setattr(construction, 'extract_kg_schema', extract_schema)
    monkeypatch.setattr(construction, 'type_definition', define_types)

    asyncio.run(
        construction.extract_from_path(
            file_path_list=['example.txt'],
            aim='test',
            info={},
            directional_suggestion='',
            api_key='key',
            base_url='https://example.com/v1',
            model='model',
            embedding_api_key='embedding-key',
            embedding_base_url='https://embedding.example.com/v1',
            embedding_model='embedding-model',
            progress_callback=lambda *args: progress.append(args),
        )
    )

    assert ('definitions', 0, 2, 0) in progress
    assert ('definitions', 2, 2, 0) in progress
