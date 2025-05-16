

# --- MATERIAL CLASSES --- #


from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class MaterialBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stock_quantity: Optional[float] = 1.0
    lead_time: Optional[str] = None
    unit_of_measure: Optional[str] = None


class MaterialPayload(MaterialBase):
    stock_quantity: float
    lead_time: str


class MaterialResponse(MaterialBase):
    id: UUID
    name: str
    description: str
    stock_quantity: float
    unit_of_measure: str
    lead_time: str
    created_at: str
    updated_at: str


class MaterialUpdatePayload(MaterialBase):
    stock_quantity: Optional[float] = None
