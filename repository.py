from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi_cache.decorator import cache

from database.models import Users, AccountStatus
from schemas import UserCreate, UserRead, UserUpdate, CreateAdminUser
from config.logger import db_error_logger, db_logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
class AuthRepository:
    @classmethod
    async def add_user(cls, user: UserCreate, session: AsyncSession) -> int:
        user_model = user.model_dump()
        user_model['password'] = get_password_hash(user.password)
        query = insert(Users).values(**user_model).returning(Users)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        db_logger.info(f"user: {user.email} created")
        await session.commit()
        return user
    @classmethod
    @cache(expire=timedelta(minutes=5), namespace="users")
    async def find_user_by_email(cls, email: str, session: AsyncSession):
        query = select(Users).where(Users.email==email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            db_logger.info(f"user: {user.email} is found")
            return UserRead.model_validate(user)
        db_logger.warning(f"user with email: {email} is not found")
        return None
    @classmethod
    @cache(expire=timedelta(minutes=5), namespace="users")
    async def find_user_by_id(cls, id: int, session: AsyncSession):
        query = select(Users).where(Users.id==id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            db_logger.info(f"user: {user.email} is found")
            return UserRead.model_validate(user)
        db_logger.warning(f"user with id: {id} is not found")
        raise HTTPException(status_code=404, detail="user not found")
    @classmethod
    async def update_user(cls, user_id: int, new_user_data: UserUpdate, session: AsyncSession) -> int:
        user_model = new_user_data.model_dump(exclude_unset=True)
        if user_model["password"]:
            user_model['password'] = get_password_hash(new_user_data.password)
        query = update(Users).where(Users.id==user_id).values(**user_model).returning(Users)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        db_logger.info(f"updated account data for user with id: {user_id}")
        await session.commit()
        return user
    @classmethod
    async def update_account_status(cls, user_id: int, status: AccountStatus, session: AsyncSession) -> int:
        query = update(Users).where(Users.id==user_id).values(status=status).returning(Users)
        result = await session.execute(query)
        updated_user = result.scalar_one_or_none()
        db_logger.info(f"updated account status for user with id: {user_id}")
        await session.commit()
        return updated_user
    @classmethod
    async def add_admin_user(cls, user: dict, session: AsyncSession) -> int:
        user['password'] = get_password_hash(user['password'])
        query = insert(Users).values(**user).returning(Users.email)
        result = await session.execute(query)
        admin_user = result.scalar_one_or_none()
        db_logger.info(f"created admin user: {admin_user}")
        await session.commit()
    