from dataclasses import dataclass

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel


@dataclass
class User(BaseModel):
    __tablename__ = 'users'

    full_name: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    registration_number: Mapped[str] = mapped_column(String(50), unique=True)
    role: Mapped[str] = mapped_column(
        Enum('User', 'Editor', 'Admin', name='user_roles'), default='User'
    )
