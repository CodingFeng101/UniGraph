import _env  # noqa: F401  # isort: skip

from backend.app.task.service.task_service import TaskService


class FakeRedis:
    def __init__(self, existing: set[str] | None = None) -> None:
        self.existing = existing or set()

    def exists(self, key: str) -> bool:
        return key in self.existing

    def lrange(self, *_args):
        return []

    def hvals(self, *_args):
        return []


def test_newly_submitted_task_is_known_before_started_result_exists(monkeypatch) -> None:
    uid = 'new-task'
    result_redis = FakeRedis({TaskService._task_submission_key(uid)})
    broker_redis = FakeRedis()
    clients = iter((result_redis, broker_redis))
    monkeypatch.setattr(TaskService, '_get_redis_client', lambda _db: next(clients))

    assert TaskService.is_task_known(uid) is True


def test_expired_task_without_result_or_broker_message_is_unknown(monkeypatch) -> None:
    clients = iter((FakeRedis(), FakeRedis()))
    monkeypatch.setattr(TaskService, '_get_redis_client', lambda _db: next(clients))

    assert TaskService.is_task_known('expired-task') is False
