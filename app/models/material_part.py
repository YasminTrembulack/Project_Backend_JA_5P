from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CHAR, UUID, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import MaterialStatusEnum

if TYPE_CHECKING:
    from app.models.part import Part
    from app.models.material import Material


class MaterialPart(BaseModel):
    __tablename__ = 'material_part'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
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
    quantity: Mapped[float] = mapped_column(Float, default=1, nullable=False)

    material: Mapped['Material'] = relationship(back_populates='part_associations')
    part: Mapped['Part'] = relationship(back_populates='material_associations')
