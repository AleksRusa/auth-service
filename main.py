from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from starlette_exporter import PrometheusMiddleware, handle_metrics
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from config.logger import logger
from repository import AuthRepository 
from routers import router as auth_router
from database.database import create_tables, delete_tables, async_session, REDIS_URL
from database.models import RoleEnum

default_admin_user = {
  "email": "admin@example.com",
  "password": "admin",
  "role": RoleEnum.ADMIN
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    redis = await aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info(f"Redis cache initialized")
    async with async_session() as db_session:
        await AuthRepository.add_admin_user(default_admin_user, db_session)
    yield
    await redis.close()
    await delete_tables()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["auth-service"])

app.add_middleware(
    PrometheusMiddleware,
    app_name="api_monitoring",
    group_paths=True,
    skip_paths=[],
    buckets=[0.1, 0.3, 0.5, 0.7, 1.0, 2.5]
)
app.add_route("/metrics", handle_metrics)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    logger.info("App started")
