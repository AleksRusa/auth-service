from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import EmailStr
from fastapi import Depends, Request, HTTPException, status

from database.config import get_auth_data
from repository import AuthRepository
from database.database import get_db
from schemas import UserRead

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])


async def authenticate_user(email: EmailStr, password: str):
    user = await AuthRepository.find_user(email, session = Depends(get_db))
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        return None
    return user

async def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")
    return token

async def get_current_user(token: str = Depends(get_token)):
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
    user = await AuthRepository.find_user_by_id(user_id, session = Depends(get_db))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return user

#проверить правильно ли указана праверка на роль пользователя
async def get_current_admin_user(current_user: UserRead = Depends(get_current_user)):
    if current_user.role == "ADMIN":
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас недостаточно прав доступа")
    