from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CHAR, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.mold import Mold


@dataclass
class User(BaseModel):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    registration_number: Mapped[str] = mapped_column(String(50), unique=True)
    role: Mapped[str] = mapped_column(
        Enum('User', 'Editor', 'Admin', name='user_roles'), default='User'
    )

    molds_created: Mapped[list['Mold']] = relationship(
        'Mold', back_populates='created_by', passive_deletes=True
    )
