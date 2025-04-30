from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Users
from schemas import UserCreate

class AuthRepository:
    @classmethod
    async def add_user(cls, user: UserCreate, session: AsyncSession) -> int:
        user_model = user.model_dump()
        query = insert(Users).values(**user_model).returning(Users.id)
        result = await session.execute(query)
        await session.commit()
        user_id = result.scalar_one()
        return user_id