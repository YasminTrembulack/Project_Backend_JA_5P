from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CHAR, VARCHAR, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.types.enums import MachineStatusEnum

if TYPE_CHECKING:
    from app.models.operation import Operation


@dataclass
class Machine(BaseModel):
    __tablename__ = 'machines'

    id: Mapped[UUID] = mapped_column(CHAR(36), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(VARCHAR(30), unique=True, nullable=False)
    m_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[MachineStatusEnum] = mapped_column(
        Enum(MachineStatusEnum), nullable=False
    )

    operations: Mapped[list['Operation']] = relationship(
        'Operation', back_populates='machine', passive_deletes=True
    )
