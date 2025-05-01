import enum
from datetime import datetime

from sqlalchemy import Enum, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import EmailStr

from database.database import Base


class RoleEnum(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    