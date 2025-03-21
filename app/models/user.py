from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel


@dataclass
class User(BaseModel):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    full_name: Mapped[str]
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[str] = mapped_column(
        Enum('user', 'admin', name='user_roles'), default='user'
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
