from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum, String, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel


@dataclass
class User(BaseModel):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(
        CHAR(36), primary_key=True, default=uuid4
    )
    full_name: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    registration_number: Mapped[str] = mapped_column(String(50), unique=True)
    role: Mapped[str] = mapped_column(
        Enum('User', 'Editor', 'Admin', name='user_roles'), default='User'
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
