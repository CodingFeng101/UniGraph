import asyncio
from unittest.mock import AsyncMock

from backend.app.kgbase.api.v1.kgbase import knowledge_graph as knowledge_graph_api


def test_background_question_persists_assistant_message(monkeypatch) -> None:
    response = {
        'results': '后台回答',
        'context_data': {'Entities': [{'id': 'entity-1', 'name': '实体'}]},
    }
    run_question = AsyncMock(return_value=(response, 'test-model'))
    append_message = AsyncMock(return_value={'message_uuid': 'assistant-message'})

    monkeypatch.setattr(knowledge_graph_api, '_run_knowledge_question', run_question)
    monkeypatch.setattr(knowledge_graph_api.chat_library_service, 'append_message', append_message)
    monkeypatch.setattr(knowledge_graph_api, 'task_progress', lambda *args, **kwargs: None)
    monkeypatch.setattr(
        knowledge_graph_api,
        'task_result',
        lambda task, message, *, data, detail, metrics: {'data': data, 'message': message},
    )

    result = asyncio.run(
        knowledge_graph_api.ask_knowledge_graph_task.run(
            uuid='graph-1',
            user_uuid='user-1',
            user_token='token-1',
            obj_data={
                'message': '问题',
                'chat_library_uuid': 'chat-1',
                'current_message_uuid': 'user-message',
                'effort': 'High',
            },
        )
    )

    saved = append_message.await_args.kwargs
    assert saved['uuid'] == 'chat-1'
    assert saved['user_uuid'] == 'user-1'
    assert saved['obj'].content == '后台回答'
    assert saved['obj'].model_name == 'test-model'
    assert saved['obj'].sources == response['context_data']
    assert result['data']['assistant_message_uuid'] == 'assistant-message'
