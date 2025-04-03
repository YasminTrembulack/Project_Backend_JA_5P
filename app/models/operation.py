from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CHAR, UUID, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import OpStatusEnum

if TYPE_CHECKING:
    from app.models.machine import Machine


class OperationAssociation(BaseModel):
    __tablename__ = 'operation_association'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    item_type: Mapped[str] = mapped_column(
        Enum('Part', 'Mold', name='item_type_enum'), nullable=False
    )
    status: Mapped[OpStatusEnum] = mapped_column(Enum(OpStatusEnum), nullable=False)

    operation_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('operations.id'), nullable=False
    )
    item_id: Mapped[UUID] = mapped_column(CHAR(36), nullable=False)
    operation: Mapped['Operation'] = relationship(
        back_populates='operation_associations'
    )
    __mapper_args__ = {
        'polymorphic_identity': 'operation_association',
        'polymorphic_on': item_type,
    }


@dataclass
class Operation(BaseModel):
    __tablename__ = 'operations'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    op_type: Mapped[str] = mapped_column(String(255))
    machine_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('machines.id', ondelete='SET NULL'), nullable=True
    )

    machine: Mapped['Machine'] = relationship(
        'Machine', back_populates='operations', passive_deletes=True
    )

    operation_associations: Mapped[list['OperationAssociation']] = relationship(
        back_populates='operation', cascade='all, delete-orphan'
    )
