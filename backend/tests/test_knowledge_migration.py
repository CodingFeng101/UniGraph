import asyncio
from types import SimpleNamespace

from backend.app.kgbase.service import knowledge_graph_service as service_module
from backend.app.kgbase.service.knowledge_graph_service import KnowledgeGraphService


def test_infer_passes_schema_types_not_names(monkeypatch) -> None:
    # The inference prompt asks the model for an element of the masked side's type, so the
    # triples handed to it must carry the schema types rather than repeat the entity names.
    captured = {}

    async def fake_create_infer_kg(*, kg, **_kwargs):
        captured['kg'] = kg
        return {'infer_kg': [], 'web_source': [], 'triple_source': []}

    monkeypatch.setattr(service_module, 'create_infer_kg', fake_create_infer_kg)
    graph = SimpleNamespace(
        entities=[
            SimpleNamespace(uuid='a', name='VMC-1060', type='设备及部件实例', attributes='{}'),
            SimpleNamespace(uuid='b', name='主轴单元', type='数控机床部件', attributes='{}'),
        ],
        relationships=[
            SimpleNamespace(source_entity_uuid='a', target_entity_uuid='b', name='要求', type='要求'),
        ],
    )

    asyncio.run(KnowledgeGraphService.infer(knowledge_graph=graph, api_key='k', base_url='u', model='m', task_client=None))

    triple = captured['kg'][0]
    assert triple['DirectionalEntity'] == {'Name': 'VMC-1060', 'Type': '设备及部件实例', 'Attributes': {}}
    assert triple['DirectedEntity']['Type'] == '数控机床部件'
    assert triple['Relation']['Type'] == '要求'
