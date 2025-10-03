import redis.asyncio as redis
import json
from typing import Optional, Any

from app.config import settings

# Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client"""
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    client = await get_redis()
    value = await client.get(key)
    if value:
        return json.loads(value)
    return None


async def set_cache(key: str, value: Any, ttl: int = settings.cache_ttl):
    """Set value in cache with TTL"""
    client = await get_redis()
    await client.setex(key, ttl, json.dumps(value))


async def delete_cache(key: str):
    """Delete value from cache"""
    client = await get_redis()
    await client.delete(key)
