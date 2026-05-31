from typing import Optional
import redis.asyncio as redis
from loguru import logger
from src.config import settings

_redis: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        try:
            _redis = redis.from_url(settings.redis_url, decode_responses=True)
            await _redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available ({e}), using in-memory fallback")
            _redis = None
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


class InMemoryCache:
    """Fallback when Redis is unavailable — NOT shared between workers"""

    def __init__(self):
        self._store: dict = {}
        self._ttls: dict = {}

    async def setex(self, key: str, seconds: int, value: str):
        self._store[key] = value
        from time import time
        self._ttls[key] = time() + seconds

    async def get(self, key: str) -> Optional[str]:
        from time import time
        expiry = self._ttls.get(key)
        if expiry and time() > expiry:
            self._store.pop(key, None)
            self._ttls.pop(key, None)
            return None
        return self._store.get(key)

    async def exists(self, key: str) -> bool:
        return await self.get(key) is not None

    async def delete(self, key: str):
        self._store.pop(key, None)
        self._ttls.pop(key, None)

    async def close(self):
        self._store.clear()
        self._ttls.clear()


_cache: InMemoryCache = InMemoryCache()


async def cache() -> redis.Redis | InMemoryCache:
    r = await get_redis()
    return r if r else _cache
