import asyncio

from backend.common.core_layer.unigraph.module.schema_construction.schema_construction import SchemaConstruction
from jinja2 import Template


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


def test_update_seeds_existing_types_and_keeps_their_definitions(monkeypatch) -> None:
    kg_schema = [
        {
            'schema': {
                'DirectionalEntityType': {'Name': '设备', 'Attributes': []},
                'RelationType': '发生',
                'DirectedEntityType': {'Name': '故障', 'Attributes': []},
            },
            'source': {},
        }
    ]
    construction = SchemaConstruction(kg_schema=kg_schema, definition={'设备': 'd', '故障': 'f', '发生': 'r'})

    assert construction.entity_type_dict == {'故障': [], '设备': []}
    assert construction.relation_type_dict == {'发生': []}

    construction.entity_type_dict['报警代码'] = ['EX1012']
    prompts = []

    async def respond(prompt, *args) -> str:
        prompts.append(prompt)
        return '报警代码: 设备报警时显示的代码'

    monkeypatch.setattr(construction, 'chatresponse', respond)
    asyncio.run(construction.type_definition('Chinese', api_key='key', base_url='https://example.com/v1', model='m'))

    assert len(prompts) == 1
    assert '报警代码: EX1012' in prompts[0]
    assert '设备: ' not in prompts[0]
    assert construction.definition['设备'] == 'd'


def test_classify_prompts_offer_existing_categories_only_on_update() -> None:
    for filename, key in (
        ('entity_classify_agent.txt', 'entity_string'),
        ('relation_classify_agent.txt', 'relation_string'),
    ):
        template = Template(SchemaConstruction.load_prompt(filename))

        update = template.render(**{key: 'x'}, language='Chinese', existing_types='设备, 故障')
        create = template.render(**{key: 'x'}, language='Chinese', existing_types='')

        assert 'already has these' in update
        assert '设备, 故障' in update
        assert 'already has these' not in create


def test_classification_drops_categories_the_expert_removed(monkeypatch) -> None:
    construction = SchemaConstruction(kg_schema=[], definition={})
    construction.excluded_entity_types = ['日期']
    prompts = []
    responses = iter([
        '(设备, 发布于, 2026年6月20日): 发布日期：2026年6月20日\n(主轴, 出现, 过热): 主轴电机过热',
        '设备: 设备, 主轴\n日期: 2026年6月20日\n故障: 过热',
        '发生: 出现\n发布: 发布于',
        '设备: 型号\n故障: 故障代码',
    ])

    async def respond(prompt, *args, **kwargs) -> str:
        prompts.append(prompt)
        return next(responses)

    monkeypatch.setattr(construction, 'chatresponse', respond)
    asyncio.run(
        construction.extract_kg_schema(
            'text', 'aim', '', 'Chinese', 'key', 'https://example.com/v1', 'm', 'k', 'https://example.com/v1', 'e'
        )
    )

    assert 'removed these entity categories as irrelevant: 日期' in prompts[1]
    assert '日期' not in construction.entity_type_dict
    names = {item['schema']['DirectedEntityType']['Name'] for item in construction.kg_schema}
    assert names == {'故障'}
