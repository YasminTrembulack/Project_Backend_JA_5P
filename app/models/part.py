from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CHAR, UUID, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import PartStatusEnum, SimpleStatusEnum

if TYPE_CHECKING:
    from app.models.material import Material, MaterialParts
    from app.models.mold import Mold
    from app.models.operation import Operation, OperationAssociation


@dataclass
class Part(BaseModel):
    __tablename__ = 'parts'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[PartStatusEnum] = mapped_column(
        Enum(PartStatusEnum), nullable=False
    )
    model_3d: Mapped[SimpleStatusEnum] = mapped_column(
        Enum(SimpleStatusEnum), nullable=False
    )
    nc_program: Mapped[SimpleStatusEnum] = mapped_column(
        Enum(SimpleStatusEnum), nullable=False
    )

    # Referência ao molde que possui a peça
    mold_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('molds.id', ondelete='CASCADE'), nullable=False
    )
    mold: Mapped['Mold'] = relationship(
        'Mold', back_populates='mold_parts', passive_deletes=True
    )

    operations: Mapped[list['Operation']] = relationship(
        secondary='operation_association',
        primaryjoin='and_(Part.id == foreign(OperationAssociation.item_id), '
        'OperationAssociation.item_type == "Part")',
        secondaryjoin=(
            'and_(OperationAssociation.operation_id == foreign(Operation.id), '
            'OperationAssociation.item_type == "Part")'
        ),
        viewonly=True,
    )

    operation_associations: Mapped[list['OperationAssociation']] = relationship(
        primaryjoin='and_(Part.id == foreign(OperationAssociation.item_id), '
        'OperationAssociation.item_type == "Part")',
        backref='part',
        cascade='all, delete-orphan',
    )

    material_associations: Mapped[list['MaterialParts']] = relationship(
        back_populates='part', cascade='all, delete-orphan'
    )

    materials: Mapped[list['Material']] = relationship(
        secondary='material_parts', back_populates='parts', viewonly=True
    )
