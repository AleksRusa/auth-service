import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase 

from database.config import settings

class Base(DeclarativeBase):
    pass

DATABASE_URL=os.getenv("AUTH_DATABASE_URL") or settings.AUTH_DATABASE_URL

async_engine = create_async_engine(url=DATABASE_URL, echo=False)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def delete_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def get_db():
    async with async_session() as session:
        yield session
        