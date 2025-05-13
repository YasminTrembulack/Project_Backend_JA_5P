from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CHAR, UUID, VARCHAR, Date, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import ItemStatusEnum, PriorityEnum

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.operation import OperationAssociation
    from app.models.part import Part
    from app.models.user import User


@dataclass
class Mold(BaseModel):
    __tablename__ = 'molds'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(VARCHAR(30), unique=True)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    priority_updated_at: Mapped[date] = mapped_column(Date, nullable=True)
    delivery_date: Mapped[datetime]
    priority: Mapped[PriorityEnum] = mapped_column(
        Enum(PriorityEnum), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[ItemStatusEnum] = mapped_column(
        Enum(ItemStatusEnum), nullable=False
    )
    # '200x150x50 mm'  # Comprimento x Largura x Altura
    dimensions: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Referência ao usuário que criou o molde
    created_by_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True
    )
    created_by: Mapped['User'] = relationship(
        'User', back_populates='molds_created', passive_deletes=True
    )

    # Referência ao cliente associado ao molde
    customer_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('customers.id', ondelete='SET NULL'), nullable=True
    )
    customer: Mapped['Customer'] = relationship(
        'Customer', back_populates='molds', passive_deletes=True
    )
    mold_parts: Mapped[list['Part']] = relationship(
        'Part', back_populates='mold', passive_deletes=True
    )

    operation_associations: Mapped[list['OperationAssociation']] = relationship(
        primaryjoin=(
            'and_(foreign(OperationAssociation.item_id) == Mold.id, '
            "OperationAssociation.item_type == 'Mold')"
        ),
        back_populates='mold',
        cascade='all, delete-orphan',
        overlaps='operation_associations',
    )
