from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Users
from schemas import UserCreate, UserRead

class AuthRepository:
    @classmethod
    async def add_user(cls, user: UserCreate, session: AsyncSession) -> int:
        user_model = user.model_dump()
        query = insert(Users).values(**user_model).returning(Users.id)
        result = await session.execute(query)
        await session.commit()
        user_id = result.scalar_one()
        return {"message": "Вы успешно зарегистрированы"}
    @classmethod
    async def find_user(cls, email: str, session: AsyncSession):
        query = select(Users).where(Users.email==email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        return UserRead.model_validate(user)