import _env  # noqa: F401  # isort: skip
import asyncio
from types import SimpleNamespace

import pytest
from backend.app.admin.service import llm_model_service as llm_model_service_module
from backend.app.admin.service.llm_model_service import LlmModelService


class _FakeBegin:
    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    def begin(self):
        return _FakeBegin()

    async def execute(self, _statement):
        raise RuntimeError("(pymysql.err.OperationalError) Can't connect to MySQL server on '10.0.0.5'")

    async def rollback(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


def test_add_model_failure_message_does_not_leak_driver_details(monkeypatch) -> None:
    monkeypatch.setattr(llm_model_service_module, 'async_db_session', _FakeSession)

    obj = SimpleNamespace(provider_uuid='p-1', type='llm', status=1)
    with pytest.raises(ValueError) as excinfo:
        asyncio.run(LlmModelService.add(obj=obj, user_uuid='user-1'))

    message = str(excinfo.value)
    assert message == '创建模型失败，请稍后重试'
    assert 'pymysql' not in message
    assert '10.0.0.5' not in message
