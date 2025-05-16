

# --- OPERATION CLASSES --- #


from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.types.machine import MachineResponse
from app.types.request_params import create_query_params_class


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

OPERATIONS_ASSOCIATIONS = ['machine']


OperationQueryParams = create_query_params_class(
    'OperationQueryParams',
    OPERATIONS_ASSOCIATIONS,
    ['created_at']
)