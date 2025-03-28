from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import CHAR, UUID, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import CamStatusEnum, PartStatusEnum

if TYPE_CHECKING:
    from app.models.mold import Mold


@dataclass
class Part(BaseModel):
    __tablename__ = 'parts'

    name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[PartStatusEnum] = mapped_column(
        Enum(PartStatusEnum), nullable=False
    )
    cam_status: Mapped[CamStatusEnum] = mapped_column(
        Enum(CamStatusEnum), nullable=False
    )

    # Referência ao molde que possui a peça
    mold_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('molds.id', ondelete='CASCADE'), nullable=False
    )
    mold: Mapped['Mold'] = relationship(
        'Mold', back_populates='mold_parts', passive_deletes=True
    )
