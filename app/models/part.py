from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CHAR, UUID, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import ItemStatusEnum

if TYPE_CHECKING:
    from app.models.material import Material
    from app.models.material_part import MaterialPart
    from app.models.mold import Mold
    from app.models.model_3d import Model3D
    from app.models.nc_program import NcProgram
    from app.models.operation_association import OperationAssociation


@dataclass
class Part(BaseModel):
    __tablename__ = 'parts'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    progress_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[ItemStatusEnum] = mapped_column(
        Enum(ItemStatusEnum), nullable=False
    )
    
    model_3d_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('models_3d.id', ondelete='SET NULL'), nullable=True
    )
    model_3d: Mapped['Model3D'] = relationship(
        'Model3D', back_populates='part'
    )
    nc_program_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('nc_programs.id', ondelete='SET NULL'), nullable=True
    )
    nc_program: Mapped['NcProgram'] = relationship(
        'NcProgram', back_populates='part'
    )
    # Referência ao molde que possui a peça
    mold_id: Mapped[UUID] = mapped_column(
        CHAR(36), ForeignKey('molds.id', ondelete='CASCADE'), nullable=False
    )
    mold: Mapped['Mold'] = relationship(
        'Mold', back_populates='mold_parts', passive_deletes=True
    )

    operation_associations: Mapped[list['OperationAssociation']] = relationship(
        primaryjoin=(
            'and_(foreign(OperationAssociation.item_id) == Part.id, '
            "OperationAssociation.item_type == 'Part')"
        ),
        back_populates='part',
        cascade='all, delete-orphan',
        overlaps='operation_associations',
    )

    material_associations: Mapped[list['MaterialPart']] = relationship(
        back_populates='part', cascade='all, delete-orphan'
    )

    materials: Mapped[list['Material']] = relationship(
        secondary='material_part', back_populates='parts', viewonly=True
    )
