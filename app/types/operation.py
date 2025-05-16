# --- OPERATION CLASSES --- #


from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel

from app.types.base import BaseQueryParams
from app.types.machine import MachineResponse

OPERATIONS_ASSOCIATIONS = ['machine']


class OperationBase(BaseModel):
    name: Optional[str] = None
    op_type: Optional[str] = None
    machine_id: Optional[str] = None
    machine: Optional[MachineResponse] = None


class OperationPayload(OperationBase):
    op_type: str


class OperationResponse(OperationBase):
    id: UUID
    name: str
    op_type: str
    machine_id: str | None
    created_at: str
    updated_at: str


class OperationUpdatePayload(OperationBase):
    pass


class OperationQueryParams(BaseQueryParams):
    order_by: str = 'created_at'  

