from uuid import uuid4

from sqlalchemy import CHAR, UUID, String
from app.models.base_model import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship



class FileEntityBase(BaseModel):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    responsible: Mapped[str] = mapped_column(String(100), nullable=True)
    path: Mapped[str] = mapped_column(String(255), nullable=True)
