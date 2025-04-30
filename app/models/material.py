from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CHAR, UUID, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import MaterialStatusEnum

if TYPE_CHECKING:
    from app.models.part import Part


class MaterialPart(BaseModel):
    __tablename__ = 'material_part'

    material_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('materials.id'), primary_key=True
    )
    part_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('parts.id'), primary_key=True
    )
    status: Mapped[MaterialStatusEnum] = mapped_column(
        Enum(MaterialStatusEnum), nullable=False
    )
    expected_delivery_date: Mapped[datetime] = mapped_column(nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    material: Mapped['Material'] = relationship(back_populates='part_associations')
    part: Mapped['Part'] = relationship(back_populates='material_associations')


@dataclass
class Material(BaseModel):
    __tablename__ = 'materials'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(CHAR(20), unique=True)
    description: Mapped[str] = mapped_column(String(255))
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=True)
    stock_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    lead_time: Mapped[str] = mapped_column(String(10))
    part_associations: Mapped[list['MaterialPart']] = relationship(
        back_populates='material', cascade='all, delete-orphan'
    )

    parts: Mapped[list['Part']] = relationship(
        secondary='material_part', back_populates='materials', viewonly=True
    )
