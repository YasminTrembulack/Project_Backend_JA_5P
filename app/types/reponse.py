from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

from app.types.base import (
    CustomerBase,
    MachineBase,
    MaterialBase,
    MaterialPartBase,
    Metadata,
    MoldBase,
    OperationAssociationBase,
    OperationBase,
    PartBase,
    ResponseBase,
)
from app.types.enums import (
    ItemStatusEnum,
    MachineStatusEnum,
    OpStatusEnum,
    PriorityEnum,
    SimpleStatusEnum,
)
from app.types.relation import (
    CustomerRelation,
    MachineRelation,
    MaterialPartRelation,
    MoldRelation,
    OperationRelation,
    PartRelation,
)

T = TypeVar('T')


class EntityResponse(BaseModel, Generic[T]):
    message: str
    data: T


class GetAllResponse(BaseModel, Generic[T]):
    message: str
    data: List[T]
    metadata: Metadata


class DeleteResponse(BaseModel):
    message: str


class PingResponse(BaseModel):
    timestamp: str
    project_name: str
    version: str


class CountyResponse(BaseModel):
    countries: List[str]


class TimeUnitResponse(BaseModel):
    time_unit: List[str]


class CustomerResponse(ResponseBase, CustomerBase, CustomerRelation):
    full_name: str
    country_name: str


class MachineResponse(ResponseBase, MachineBase, MachineRelation):
    name: str
    m_type: str
    status: MachineStatusEnum


class MaterialPartResponse(ResponseBase, MaterialPartBase, MaterialPartRelation):
    material_id: str
    part_id: str
    quantity: float
    status: str
    expected_delivery_date: datetime | None


class MaterialResponse(ResponseBase, MaterialBase):  # MaterialRelation
    name: str
    description: str
    stock_quantity: float
    unit_of_measure: str
    lead_time: str


class MoldResponse(ResponseBase, MoldBase, MoldRelation):
    name: str
    delivery_date: datetime
    priority: PriorityEnum
    quantity: int
    progress_percentage: float
    status: ItemStatusEnum
    dimensions: str | None
    created_by_id: str
    customer_id: str


class OperationAssociationResponse(ResponseBase, OperationAssociationBase):
    # OperationAssociationRelation
    status: OpStatusEnum
    item_type: str
    item_id: str
    operation_id: str


class OperationResponse(ResponseBase, OperationBase, OperationRelation):
    name: str
    op_type: str
    machine_id: str | None


class PartResponse(ResponseBase, PartBase, PartRelation):
    name: str
    description: str | None
    quantity: int
    progress_percentage: float
    status: ItemStatusEnum
    model_3d: SimpleStatusEnum
    nc_program: SimpleStatusEnum
    mold: Optional[MoldResponse] = None
    mold_id: str


class UserResponse(ResponseBase, BaseModel):
    # UserRelation
    full_name: str
    email: str
    registration_number: str
    role: str
