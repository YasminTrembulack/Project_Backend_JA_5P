
# --- MATERIAL PARTS CLASSES --- #


from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.types import MaterialStatusEnum


class MaterialPartBase(BaseModel):
    part_id: Optional[str] = None
    material_id: Optional[str] = None
    quantity: Optional[float] = 1.0
    expected_delivery_date: Optional[datetime] = None
    status: Optional[MaterialStatusEnum] = MaterialStatusEnum.PENDING


class MaterialPartPayload(MaterialPartBase):
    material_id: str
    part_id: str


class MaterialPartResponse(MaterialPartBase):
    id: UUID
    material_id: str
    part_id: str
    quantity: float
    status: str
    expected_delivery_date: datetime | None
    created_at: str
    updated_at: str


class MaterialPartUpdatePayload(MaterialPartBase):
    quantity: Optional[float] = None
    status: Optional[MaterialStatusEnum] = None
