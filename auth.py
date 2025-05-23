from enum import Enum
from typing import Optional
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import EmailStr
from fastapi import Depends, Request, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from config.config import get_auth_data
from config.logger import logger
from repository import AuthRepository
from database.database import get_db
from schemas import UserRead


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_token_factory(expire: timedelta):
    async def create_token(data: dict) -> str:
        to_encode = data.copy()
        token_expire = datetime.now(timezone.utc) + expire
        to_encode.update({"exp": token_expire})
        # TODO: реализовать хранение секретов
        auth_data = get_auth_data()
        if not auth_data or 'secret_key' not in auth_data or 'algorithm' not in auth_data:
            raise ValueError("Auth data must contain 'secret_key' and 'algorithm'")
        encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
        return encode_jwt
    return create_token
    
create_access_token = create_token_factory(timedelta(minutes=30))
create_refresh_token = create_token_factory(timedelta(days=7))

async def set_token_cookie(response: Response, token_type: TokenType, token_value: str):
    cookie_params = {"key": f"user_{token_type.value}_token", "value": token_value, "httponly": True}
    if token_type == TokenType.REFRESH:
        cookie_params["path"] = "/auth/refresh"
    response.set_cookie(**cookie_params)

@cache(expire=100)
async def authenticate_user(email: EmailStr, password: str, session: AsyncSession):
    user = await AuthRepository.find_user_by_email(email, session)
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        logger.warning("Invalid email or password")
        return None
    return user

async def get_token(request: Request, token_type: TokenType):
    token = request.cookies.get(f'user_{token_type.value}_token')
    if not token:
        logger.error("token is not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{token_type.value}_token is not found")
    return token

@cache(expire=100)
async def get_current_user(request: Request, token_type: TokenType, session: AsyncSession):
    token = await get_token(request, token_type)
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        logger.error("token is not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    
    expire = payload.get('exp')
    user_id = payload.get('sub')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        logger.error(f"token for user with id - {user_id} is not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='token has been expired')
    
    user_id = payload.get('sub')
    if not user_id:
        logger.error(f"user_id is not found in token")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user_id is not found')
    user = await AuthRepository.find_user_by_id(int(user_id), session)
    if not user:
        logger.error("user in not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

# admin can ban users
async def get_current_admin_user(request: Request, session: AsyncSession):
    current_user = await get_current_user(request, TokenType.ACCESS, session)
    if current_user.role == "admin":
        logger.info(f"user with email - {current_user.email} is admin")
        return current_user
    logger.info(f"user with email - {current_user.email} is not admin")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас недостаточно прав доступа")
    