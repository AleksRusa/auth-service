from enum import Enum
from typing import Optional
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import EmailStr
from fastapi import Depends, Request, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_auth_data
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
        auth_data = get_auth_data()
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


async def authenticate_user(email: EmailStr, password: str, session: AsyncSession):
    user = await AuthRepository.find_user(email, session)
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        return None
    return user

async def get_token(request: Request, token_type: TokenType):
    token = request.cookies.get(f'user_{token_type.value}_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")
    return token

async def get_current_user(request: Request, token_type: TokenType, session: AsyncSession):
    token = await get_token(request, token_type)
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    
    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='token has been expired')
    
    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User_id is not found')
    user = await AuthRepository.find_user_by_id(int(user_id), session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return user

#проверить правильно ли указана праверка на роль пользователя
# async def get_current_admin_user(request: Request):
#     current_user = get_current_user(request, token_type = TokenType.ACCESS, session)
#     if current_user.role == "ADMIN":
#         return current_user
#     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас недостаточно прав доступа")
    