from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from database.models import Users
from schemas import UserCreate, UserRead

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