from fastapi import APIRouter, Depends, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas import UserCreate, UserAuth

from repository import AuthRepository
from auth import authenticate_user, create_access_token

router = APIRouter()

@router.post("/auth/register")
async def create_user(
    user: UserCreate = Depends(),
    session: AsyncSession = Depends(get_db)
):
    new_user_id = await AuthRepository.add_user(user, session)
    return {"user_id": new_user_id}

@router.post("/auth/login")
async def create_token(response: Response, user_data: UserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detatil="неверная почта либо пароль")
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="user_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}

@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}