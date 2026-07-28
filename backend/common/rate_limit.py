from fastapi_limiter.depends import RateLimiter


def rate_limiter(times: int, seconds: int) -> RateLimiter:
    """Build a route-scoped Redis-backed rate limiter."""
    return RateLimiter(times=times, seconds=seconds)
