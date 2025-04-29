import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

DATABASE_URL=os.getenv("AUTH_DATABASE_URL")

async_engine = create_async_engine(url=DATABASE_URL, echo=False)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session