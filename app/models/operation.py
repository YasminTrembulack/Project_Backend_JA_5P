from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CHAR, UUID, VARCHAR, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.machine import Machine
    from app.models.operation_association import OperationAssociation


@dataclass
class Operation(BaseModel):
    __tablename__ = 'operations'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(VARCHAR(30))
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
