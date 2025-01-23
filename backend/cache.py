# cache.py
import redis
from typing import Optional
import json

class CacheService:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def get(self, key: str) -> Optional[dict]:
        value = self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: dict, expire: int = 3600):
        self.redis.setex(key, expire, json.dumps(value))
