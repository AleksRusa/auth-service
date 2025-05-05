from fastapi import HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from database.models import Users, AccountStatus
from schemas import UserCreate, UserRead, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

class AuthRepository:
    # добавить обработку ошибок, email already exists
    @classmethod
    async def add_user(cls, user: UserCreate, session: AsyncSession) -> int:
        user_model = user.model_dump()
        user_model['password'] = get_password_hash(user.password)
        query = insert(Users).values(**user_model).returning(Users)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        await session.commit()
        return user
    @classmethod
    async def find_user(cls, email: str, session: AsyncSession):
        query = select(Users).where(Users.email==email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        return UserRead.model_validate(user)
    @classmethod
    async def find_user_by_id(cls, id: int, session: AsyncSession):
        query = select(Users).where(Users.id==id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        return UserRead.model_validate(user)
    @classmethod
    async def update_user(cls, user_id: int, new_user_data: UserUpdate, session: AsyncSession) -> int:
        user_model = new_user_data.model_dump(exclude_unset=True)
        if user_model["password"]:
            user_model['password'] = get_password_hash(new_user_data.password)
        query = update(Users).where(Users.id==user_id).values(**user_model).returning(Users)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        await session.commit()
        return user
    @classmethod
    async def find_user_by_email(cls, email: str, session: AsyncSession):
        query = select(Users).where(Users.email==email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        return user
    @classmethod
    async def update_account_status(cls, user_id: int, status: AccountStatus, session: AsyncSession) -> int:
        query = update(Users).where(Users.id==user_id).values(status=status).returning(Users)
        result = await session.execute(query)
        updated_user = result.scalar_one_or_none()
        await session.commit()
        return updated_user
    