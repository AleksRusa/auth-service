from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from routers import router as auth_router
from database.database import create_tables, delete_tables

#добавить создание таблиц
#добавить развертку через docker-conmpose

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("Таблицы созданы")
    yield
    await delete_tables()
    print("База данных очищена")

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
