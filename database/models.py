from enum import Enum as PyEnum
from datetime import datetime

from sqlalchemy import Enum as SqlEnum, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import EmailStr

from database.database import Base


class RoleEnum(str, PyEnum):
    USER = "user"
    ADMIN = "admin"

class AccountStatus(str, PyEnum):
    ACTIVE = "active"
    DELETED = "deleted"
    BANNED = "banned"

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[RoleEnum] = mapped_column(SqlEnum(RoleEnum), default=RoleEnum.USER, nullable=False)
    status: Mapped[AccountStatus] = mapped_column(SqlEnum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    