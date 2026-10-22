import redis

from api.config import settings


class RedisCache:
    def __init__(self) -> None:
        self.client = redis.from_url(settings.redis_url, decode_responses=True)

    def health(self) -> dict:
        try:
            pong = self.client.ping()
            return {"redis": "ok" if pong else "degraded"}
        except redis.RedisError:
            return {"redis": "unavailable"}
