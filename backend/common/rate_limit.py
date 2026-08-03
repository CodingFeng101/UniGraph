import redis as pyredis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from starlette.requests import Request
from starlette.responses import Response


class RouteCompatibleRateLimiter(RateLimiter):
    """Rate limiter that does not inspect FastAPI's private route objects."""

    async def __call__(self, request: Request, response: Response):
        if not FastAPILimiter.redis:
            raise RuntimeError('FastAPILimiter.init must be called during application startup')

        identifier = self.identifier or FastAPILimiter.identifier
        callback = self.callback or FastAPILimiter.http_callback
        rate_key = await identifier(request)
        key = f'{FastAPILimiter.prefix}:{rate_key}:{request.method}'
        try:
            pexpire = await self._check(key)
        except pyredis.exceptions.NoScriptError:
            FastAPILimiter.lua_sha = await FastAPILimiter.redis.script_load(FastAPILimiter.lua_script)
            pexpire = await self._check(key)
        if pexpire != 0:
            return await callback(request, response, pexpire)


def rate_limiter(times: int, seconds: int) -> RouteCompatibleRateLimiter:
    """Build a route-scoped Redis-backed rate limiter."""
    return RouteCompatibleRateLimiter(times=times, seconds=seconds)
