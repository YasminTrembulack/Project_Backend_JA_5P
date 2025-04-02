from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import MachineStatusEnum

if TYPE_CHECKING:
    from app.models.operation import Operation


@dataclass
class Machine(BaseModel):
    __tablename__ = 'machines'

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    m_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[MachineStatusEnum] = mapped_column(
        Enum(MachineStatusEnum), nullable=False
    )

    operations: Mapped[list['Operation']] = relationship(
        'Operation', back_populates='machine', passive_deletes=True
    )
