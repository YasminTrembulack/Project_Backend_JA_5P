from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CHAR, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.mold import Mold


@dataclass
class Customer(BaseModel):
    __tablename__ = 'customers'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(255))
    country_code: Mapped[str] = mapped_column(String(2))
    country_name: Mapped[str] = mapped_column(String(50))

    molds: Mapped[list['Mold']] = relationship(
        'Mold', back_populates='customer', passive_deletes=True
    )
