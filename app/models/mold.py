from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CHAR, UUID, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import MoldStatusEnum, PriorityEnum

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.operation import Operation, OperationAssociation
    from app.models.part import Part
    from app.models.user import User


@dataclass
class Mold(BaseModel):
    __tablename__ = 'molds'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(CHAR(30), unique=True)
    delivery_date: Mapped[datetime]
    priority: Mapped[PriorityEnum] = mapped_column(
        Enum(PriorityEnum), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[MoldStatusEnum] = mapped_column(
        Enum(MoldStatusEnum), nullable=False
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

    operations: Mapped[list['Operation']] = relationship(
        secondary='operation_association',
        primaryjoin='and_(Mold.id == foreign(OperationAssociation.item_id), '
        'OperationAssociation.item_type == "Mold")',
        secondaryjoin=(
            'and_(OperationAssociation.operation_id == foreign(Operation.id), '
            'OperationAssociation.item_type == "Mold")'
        ),
        viewonly=True,
    )

    operation_associations: Mapped[list['OperationAssociation']] = relationship(
        primaryjoin='and_(Mold.id == foreign(OperationAssociation.item_id), '
        'OperationAssociation.item_type == "Mold")',
        backref='mold',
        cascade='all, delete-orphan',
    )


# Quando um Mold for deletado, o User e o Customer não devem ser afetados.
# Quando um User ou Customer for deletado, a referência no Mold deve ser nula.
