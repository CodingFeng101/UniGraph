from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate


def rate_limiter(times: int, seconds: int) -> RateLimiter:
    """Build a route-scoped in-memory rate limiter."""
    return RateLimiter(limiter=Limiter(Rate(times, Duration.SECOND * seconds)))
