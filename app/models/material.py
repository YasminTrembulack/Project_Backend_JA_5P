from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    pass


@dataclass
class Material(BaseModel):
    __tablename__ = 'materials'

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=True)
    stock_quantity: Mapped[float] = mapped_column(Float, nullable=False)
