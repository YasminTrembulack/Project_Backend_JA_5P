


# --- PART CLASSES --- #


from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from app.types import(
    MaterialPartResponse,
    OperationAssociationResponse,
    MoldResponse,
    ItemStatusEnum,
    SimpleStatusEnum
)


class PartBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = 1
    progress_percentage: Optional[float] = 0.0
    material_associations: Optional[List[MaterialPartResponse]] = []
    operation_associations: Optional[List[OperationAssociationResponse]] = []
    mold: Optional[MoldResponse] = None
    status: Optional[ItemStatusEnum] = ItemStatusEnum.PENDING
    model_3d: Optional[SimpleStatusEnum] = SimpleStatusEnum.PENDING
    nc_program: Optional[SimpleStatusEnum] = SimpleStatusEnum.PENDING
    mold_id: Optional[str] = None


class PartPayload(PartBase):
    mold_id: str


class PartResponse(PartBase):
    id: UUID
    name: str
    description: str | None
    quantity: int
    progress_percentage: float
    status: ItemStatusEnum
    model_3d: SimpleStatusEnum
    nc_program: SimpleStatusEnum
    mold: Optional[MoldResponse] = None
    mold_id: str
    created_at: str
    updated_at: str


class PartUpdatePayload(PartBase):
    quantity: Optional[int] = None
    progress_percentage: Optional[float] = None
    status: Optional[ItemStatusEnum] = None
    model_3d: Optional[SimpleStatusEnum] = None
    nc_program: Optional[SimpleStatusEnum] = None



