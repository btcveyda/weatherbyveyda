import asyncio
import json
import time
from typing import Any, Optional

from .config import settings


class InMemoryCache:
    def __init__(self):
        self._store: dict[str, tuple[float, str]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            expires_at, raw = item
            if time.time() > expires_at:
                del self._store[key]
                return None
            return json.loads(raw)

    async def set(self, key: str, value: Any, ttl: int):
        raw = json.dumps(value)
        expires_at = time.time() + ttl
        async with self._lock:
            self._store[key] = (expires_at, raw)


try:
    import redis.asyncio as aioredis
except Exception:
    aioredis = None


class RedisCache:
    def __init__(self, url: str):
        if aioredis is None:
            raise RuntimeError("redis.asyncio package is required for RedisCache")
        self._redis = aioredis.from_url(url)

    async def get(self, key: str) -> Optional[Any]:
        raw = await self._redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set(self, key: str, value: Any, ttl: int):
        await self._redis.set(key, json.dumps(value), ex=ttl)


_cache: Optional[Any] = None


def get_cache():
    global _cache
    if _cache is not None:
        return _cache
    if settings.REDIS_URL:
        try:
            _cache = RedisCache(settings.REDIS_URL)
            return _cache
        except Exception:
            pass
    _cache = InMemoryCache()
    return _cache
