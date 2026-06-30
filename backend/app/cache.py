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
        self._url = url
        self._redis = None

    async def _get_redis(self):
        if self._redis is None:
            self._redis = aioredis.from_url(self._url)
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        try:
            redis = await self._get_redis()
            raw = await redis.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int):
        try:
            redis = await self._get_redis()
            await redis.set(key, json.dumps(value), ex=ttl)
        except Exception:
            pass


_cache: Optional[Any] = None


def get_cache():
    global _cache
    if _cache is not None:
        return _cache
    if settings.REDIS_URL:
        try:
            _cache = RedisCache(settings.REDIS_URL)
            return _cache
        except Exception as e:
            print(f"Warning: Redis disabled, using in-memory cache: {e}")
    _cache = InMemoryCache()
    return _cache
