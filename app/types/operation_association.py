
# --- OPERATION ASSOCIATION CLASSES --- #


from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.types.enums import OpStatusEnum


class OperationAssociationBase(BaseModel):
    status: Optional[OpStatusEnum] = OpStatusEnum.PENDING
    item_type: Optional[str] = None
    item_id: Optional[str] = None
    operation_id: Optional[str] = None


class OperationAssociationPayload(OperationAssociationBase):
    item_id: str
    operation_id: str


class OperationAssociationResponse(OperationAssociationBase):
    id: UUID
    status: OpStatusEnum
    item_type: str
    item_id: str
    operation_id: str
    created_at: str
    updated_at: str


class OperationAssociationUpdatePayload(OperationAssociationBase):
    status: Optional[OpStatusEnum] = None
