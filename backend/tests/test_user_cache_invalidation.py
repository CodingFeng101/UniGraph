import _env  # noqa: F401  # isort: skip
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from backend.app.admin.service import user_service as user_service_module
from backend.app.admin.service.user_service import UserService
from backend.core.conf import settings


class _FakeSessionContext:
    async def __aenter__(self):
        return SimpleNamespace()

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeRedis:
    def __init__(self):
        self.deleted_prefixes: list[str] = []
        self.deleted_keys: list[str] = []

    async def delete_prefix(self, key: str) -> None:
        self.deleted_prefixes.append(key)

    async def delete(self, key: str) -> None:
        self.deleted_keys.append(key)


def _patch_common(monkeypatch, target_user):
    fake_redis = _FakeRedis()
    monkeypatch.setattr(user_service_module, 'async_db_session', SimpleNamespace(begin=_FakeSessionContext))
    monkeypatch.setattr(user_service_module, 'redis_client', fake_redis)
    monkeypatch.setattr(
        user_service_module,
        'user_dao',
        SimpleNamespace(
            get_with_relation=AsyncMock(return_value=target_user),
            update_role=AsyncMock(),
            update_dept=AsyncMock(),
        ),
    )
    return fake_redis


def _request():
    return SimpleNamespace(user=SimpleNamespace(id=1, uuid='admin-uuid', username='admin'))


def test_update_roles_clears_target_user_caches_not_admin(monkeypatch) -> None:
    target = SimpleNamespace(id=42, uuid='target-uuid')
    fake_redis = _patch_common(monkeypatch, target)
    monkeypatch.setattr(
        user_service_module, 'role_dao', SimpleNamespace(get=AsyncMock(return_value=SimpleNamespace(id=7)))
    )

    asyncio.run(UserService.update_roles(request=_request(), username='target', obj=SimpleNamespace(roles=[7])))

    assert fake_redis.deleted_prefixes == [f'{settings.PERMISSION_REDIS_PREFIX}:target-uuid']
    assert fake_redis.deleted_keys == [f'{settings.JWT_USER_REDIS_PREFIX}:42']


def test_update_depts_clears_target_user_caches_not_admin(monkeypatch) -> None:
    target = SimpleNamespace(id=42, uuid='target-uuid')
    fake_redis = _patch_common(monkeypatch, target)
    monkeypatch.setattr(
        user_service_module, 'dept_dao', SimpleNamespace(get=AsyncMock(return_value=SimpleNamespace(id=3)))
    )

    asyncio.run(UserService.update_depts(request=_request(), username='target', obj=SimpleNamespace(depts=[3])))

    assert fake_redis.deleted_prefixes == [f'{settings.PERMISSION_REDIS_PREFIX}:target-uuid']
    assert fake_redis.deleted_keys == [f'{settings.JWT_USER_REDIS_PREFIX}:42']
