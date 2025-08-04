from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CHAR, UUID, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.material_part import MaterialPart
    from app.models.part import Part


@dataclass
class Material(BaseModel):
    __tablename__ = 'materials'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=True)
    stock_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    lead_time: Mapped[str] = mapped_column(String(10))
    part_associations: Mapped[list['MaterialPart']] = relationship(
        back_populates='material', cascade='all, delete-orphan'
    )

    parts: Mapped[list['Part']] = relationship(
        secondary='material_part', back_populates='materials', viewonly=True
    )
