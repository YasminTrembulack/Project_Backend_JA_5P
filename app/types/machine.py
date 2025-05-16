

# --- MACHINE CLASSES --- #


from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.types.enums import MachineStatusEnum


class MachineBase(BaseModel):
    name: Optional[str] = None
    m_type: Optional[str] = None
    status: Optional[MachineStatusEnum] = MachineStatusEnum.AVAILABLE


class MachinePayload(MachineBase):
    m_type: str


class MachineResponse(MachineBase):
    id: UUID
    name: str
    m_type: str
    status: MachineStatusEnum
    created_at: str
    updated_at: str


class MachineUpdatePayload(MachineBase):
    status: Optional[MachineStatusEnum] = None
