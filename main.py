from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import config.logger
from repository import AuthRepository 
from routers import router as auth_router
from database.database import create_tables, delete_tables
from database.models import RoleEnum
from database.database import async_session

default_admin_user = {
  "email": "admin@example.com",
  "password": "admin",
  "role": RoleEnum.ADMIN
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("Таблицы созданы")
    async with async_session() as db_session:
        await AuthRepository.add_admin_user(default_admin_user, db_session)
    print("created admin user")
    yield
    await delete_tables()
    print("База данных очищена")

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["auth-service"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
