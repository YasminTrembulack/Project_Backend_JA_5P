from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from app.models.file_entity_base import FileEntityBase
from sqlalchemy.orm import Mapped, relationship


if TYPE_CHECKING:
    from app.models.part import Part
    
@dataclass
class Model3D(FileEntityBase):
    __tablename__ = 'models_3d'

    part: Mapped['Part'] = relationship(
        'Part', back_populates='model_3d', passive_deletes=True
    )