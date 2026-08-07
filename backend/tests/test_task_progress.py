import json

import pytest
from backend.common import task_progress
from backend.common.task_progress import TaskExecutionError, json_safe, task_error_result


class FakeRequest:
    id = 'task-id'


class FakeTask:
    request = FakeRequest()

    def update_state(self, *, state, meta) -> None:
        self.state = state
        self.meta = meta


def test_json_safe_converts_dictionary_views() -> None:
    payload = {'values': {'one': 1, 'two': 2}.values()}

    assert json_safe(payload) == {'values': [1, 2]}
    json.dumps(json_safe(payload))


def test_task_error_result_is_json_serializable(monkeypatch) -> None:
    task = FakeTask()
    payload = {'error': {'message': 'failed'}, 'details': {'one': 1}.values()}
    cached = {}
    monkeypatch.setattr(task_progress, '_cache_task_payload', lambda task_id, result: cached.update(result))

    with pytest.raises(TaskExecutionError, match='failed'):
        task_error_result(task, payload)

    assert task.state == 'FAILURE'
    assert cached['type'] == 'error'
    assert cached['message'] == 'failed'
    json.dumps(cached)
