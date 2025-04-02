from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import CHAR, UUID, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import OpStatusEnum

if TYPE_CHECKING:
    from app.models.machine import Machine
    from app.models.mold import Mold
    from app.models.part import Part


class OperationAssociation(BaseModel):
    __tablename__ = 'operation_association'

    operation_id: Mapped[int] = mapped_column(
        ForeignKey('operations.id'), nullable=False
    )
    item_id: Mapped[UUID] = mapped_column(CHAR(36), nullable=False)
    item_type: Mapped[str] = mapped_column(
        Enum('Part', 'Mold', name='item_type_enum'), nullable=False
    )
    status: Mapped[OpStatusEnum] = mapped_column(Enum(OpStatusEnum), nullable=False)

    operation: Mapped['Operation'] = relationship(
        back_populates='operation_associations'
    )


@dataclass
class Operation(BaseModel):
    __tablename__ = 'operations'

    op_type: Mapped[str] = mapped_column(String(255))
    machine_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('machines.id', ondelete='SET NULL'), nullable=True
    )

    machine: Mapped['Machine'] = relationship(
        'Machine', back_populates='machines', passive_deletes=True
    )
    parts: Mapped[list['Part']] = relationship(
        secondary='operation_association', back_populates='operations'
    )
    molds: Mapped[list['Mold']] = relationship(
        secondary='operation_association', back_populates='operations'
    )
    operation_associations: Mapped[list['OperationAssociation']] = relationship(
        back_populates='operation'
    )
