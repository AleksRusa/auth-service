from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr

from database.models import RoleEnum, AccountStatus

class UserAuth(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class UserCreate(UserAuth):
    pass

class UserRead(UserAuth):
    id: int
    balance: float
    role: RoleEnum
    status: AccountStatus
    created_at: datetime

class UserUpdate(UserAuth):
    email: Optional[EmailStr]
    password: Optional[str]
    

