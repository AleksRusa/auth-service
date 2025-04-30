from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from database.models import RoleEnum

class UserBase(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    role: RoleEnum
    balance: float
    created_at: datetime

