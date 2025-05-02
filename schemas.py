from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr

from database.models import RoleEnum

class UserAuth(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class UserCreate(UserAuth):
    pass

class UserRead(UserAuth):
    id: int
    role: RoleEnum
    balance: float
    created_at: datetime

