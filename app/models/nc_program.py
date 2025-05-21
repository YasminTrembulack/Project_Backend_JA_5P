from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from app.models.file_entity_base import FileEntityBase
from sqlalchemy.orm import Mapped, relationship


if TYPE_CHECKING:
    from app.models.part import Part
    
@dataclass
class NcProgram(FileEntityBase):
    __tablename__ = 'nc_programs'

    part: Mapped['Part'] = relationship(
        'Part', back_populates='nc_program', passive_deletes=True
    )