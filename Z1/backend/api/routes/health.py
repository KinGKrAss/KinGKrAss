from fastapi import APIRouter

from integrations.redis_client import RedisCache

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check() -> dict:
    return {"status": "ok", **RedisCache().health()}
