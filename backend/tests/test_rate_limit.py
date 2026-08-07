import asyncio
from types import SimpleNamespace

from backend.common.rate_limit import RouteCompatibleRateLimiter
from fastapi_limiter import FastAPILimiter


class FakeRedis:
    async def evalsha(self, *_args):
        return 0


def test_rate_limiter_does_not_inspect_fastapi_route_objects() -> None:
    original = (
        FastAPILimiter.redis,
        FastAPILimiter.prefix,
        FastAPILimiter.lua_sha,
        FastAPILimiter.identifier,
    )
    FastAPILimiter.redis = FakeRedis()
    FastAPILimiter.prefix = 'test-limiter'
    FastAPILimiter.lua_sha = 'sha'

    async def identifier(_request):
        return '127.0.0.1:/knowg/v1/auth/captcha'

    FastAPILimiter.identifier = identifier
    request = SimpleNamespace(method='GET', app=SimpleNamespace(routes=[SimpleNamespace()]))

    try:
        asyncio.run(RouteCompatibleRateLimiter(times=5, seconds=10)(request, SimpleNamespace()))
    finally:
        (
            FastAPILimiter.redis,
            FastAPILimiter.prefix,
            FastAPILimiter.lua_sha,
            FastAPILimiter.identifier,
        ) = original
