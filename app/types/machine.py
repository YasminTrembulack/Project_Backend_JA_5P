# --- MACHINE CLASSES --- #


from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.types.base import BaseQueryParams
from app.types.enums import MachineStatusEnum

if TYPE_CHECKING:
    from app.types.operation import OperationResponse


class MachineBase(BaseModel):
    name: Optional[str] = None
    m_type: Optional[str] = None
    status: Optional[MachineStatusEnum] = MachineStatusEnum.AVAILABLE
    operations: Optional[List['OperationResponse']] = []


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


class MachineQueryParams(BaseQueryParams):
    order_by: str = 'created_at'
