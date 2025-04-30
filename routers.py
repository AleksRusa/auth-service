from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas import UserCreate

from repository import AuthRepository

router = APIRouter()

@router.post("auth/register")
async def create_user(
    user: UserCreate = Depends(),
    session: AsyncSession = Depends(get_db)
):
    new_user_id = await AuthRepository.add_user(user)
    return new_user_id

@router.post("auth/login")
async def create_token():
    pass

@router.post("auth/verify_token")
async def verify_token():
    pass