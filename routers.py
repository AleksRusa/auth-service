from fastapi import APIRouter, Depends, Response, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas import UserCreate, UserAuth
from repository import AuthRepository
from auth import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token, 
    set_token_cookie, TokenType,
    get_current_user)

router = APIRouter()

@router.post("/register")
async def create_user(
    response: Response,
    user: UserCreate,
    session: AsyncSession = Depends(get_db)
):
    new_user = await AuthRepository.add_user(user, session)
    access_token = await create_access_token({"sub": str(new_user.id), "role": str(new_user.role)})
    refresh_token = await create_refresh_token({"sub": str(new_user.id)})
    await set_token_cookie(response, TokenType.ACCESS, access_token)
    await set_token_cookie(response, TokenType.REFRESH, refresh_token)
    return {"message": "Вы успешно зарегистрированы"}

@router.post("/login")
async def create_tokens(response: Response, user_data: UserAuth, session: AsyncSession = Depends(get_db)):
    user = await authenticate_user(email=user_data.email, password=user_data.password, session=session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detatil="неверная почта либо пароль")
    access_token = await create_access_token({"sub": str(user.id), "role": str(user.role)})
    refresh_token = await create_refresh_token({"sub": str(user.id)})
    await set_token_cookie(response, TokenType.ACCESS, access_token)
    await set_token_cookie(response, TokenType.REFRESH, refresh_token)
    return {'access_token': access_token, 'refresh_token': refresh_token}

@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key="user_access_token")
    response.delete_cookie(key="user_refresh_token", path="/auth/refresh")
    return {'message': 'Пользователь успешно вышел из системы'}

@router.post("/refresh")
async def refresh_token(request: Request, response: Response, session: AsyncSession = Depends(get_db)):
    user_from_token = await get_current_user(request, TokenType.REFRESH, session)
    new_access_token = await create_access_token({"sub": str(user_from_token.id), "role": user_from_token.role})
    await set_token_cookie(response, TokenType.ACCESS, new_access_token)
    return {'new_access_token': new_access_token}
    