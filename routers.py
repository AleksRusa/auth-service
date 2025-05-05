from typing import Optional

from fastapi import APIRouter, Depends, Response, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database.models import AccountStatus
from database.database import get_db
from schemas import UserCreate, UserAuth, UserUpdate
from repository import AuthRepository
from auth import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token, 
    set_token_cookie, TokenType,
    get_current_user,
    get_current_admin_user)

router = APIRouter()

@router.post("/register")
async def create_user(
    response: Response,
    user: UserCreate,
    session: AsyncSession = Depends(get_db)
):
    existed_user = await AuthRepository.find_user_by_email(user.email, session)
    if existed_user:
        raise HTTPException(status_code=400, detail="user with this email already exists")
    new_user = await AuthRepository.add_user(user, session)
    # TODO: раскомментировать логику создания токена при регистрации
    # access_token = await create_access_token({"sub": str(new_user.id), "role": str(new_user.role)})
    # refresh_token = await create_refresh_token({"sub": str(new_user.id)})
    # await set_token_cookie(response, TokenType.ACCESS, access_token)
    # await set_token_cookie(response, TokenType.REFRESH, refresh_token)
    return {"message": "Вы успешно зарегистрированы"}

@router.post("/login")
async def create_tokens(response: Response, user_data: UserAuth, session: AsyncSession = Depends(get_db)):
    user = await authenticate_user(email=user_data.email, password=user_data.password, session=session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detatil="неверная почта либо пароль")
    access_token = await create_access_token({"sub": str(user.id)})
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
    new_access_token = await create_access_token({"sub": str(user_from_token.id)})
    await set_token_cookie(response, TokenType.ACCESS, new_access_token)
    return {'new_access_token': new_access_token}

@router.get("/user_info/")
async def get_user_info(request: Request, user_id: Optional[int] = None, session: AsyncSession = Depends(get_db)):
    if user_id:
        admin_user = await get_current_admin_user(request, session)
        user = await AuthRepository.find_user_by_id(user_id, session)
        return user
    else:
        user_from_token = await get_current_user(request, TokenType.ACCESS, session)
        return user_from_token

@router.patch("/update_user/")
async def update_user_info(
    request: Request, 
    user_update_data: UserUpdate, 
    user_id: Optional[int] = None,
    session: AsyncSession = Depends(get_db)
    ): 
    # проверка прав на изменение пользователя
    if user_id:
        admin_user = await get_current_admin_user(request, session)
    # проверка существования пользователя
    check_user_exists = await AuthRepository.find_user_by_id(user_id, session)
    if not check_user_exists:
        raise HTTPException(status_code=404, detail="user not found")
    # если email уже существует
    if user_update_data.email:
        existed_user = await AuthRepository.find_user_by_email(user_update_data.email, session)
    if existed_user:
        raise HTTPException(status_code=400, detail="email already exists")
    new_user_data = await AuthRepository.update_user(user_id, user_update_data, session)
    return new_user_data

# banned может сделать только admin
@router.patch("/update/account_status/")
async def delete_user(
    request: Request, 
    status: AccountStatus, 
    user_id: Optional[int] = None, 
    session: AsyncSession = Depends(get_db)
    ):
    if status == AccountStatus.BANNED or user_id:
        admin_user = await get_current_admin_user(request, session)
        if status == AccountStatus.BANNED:
            raise HTTPException(status_code=403, detail="you can not ban yourselt")
    user = await get_current_user(request, TokenType.ACCESS, session)
    new_user_data = await AuthRepository.update_account_status(user.id, status, session)
    return new_user_data
    