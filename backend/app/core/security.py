from fastapi import Request, HTTPException
from .redis import redis_client


async def rate_limit(request: Request, limit: int = 30, window: int = 60):
    """Sliding window rate limiter using Redis."""
    key = f"rl:{request.client.host}:{request.url.path}"
    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, window)
    if current > limit:
        raise HTTPException(status_code=429, detail="Too many requests")