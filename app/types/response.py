from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

from app.types.base import (
    CustomerBase,
    MachineBase,
    MaterialBase,
    MaterialPartBase,
    Metadata,
    Model3DBase,
    MoldBase,
    NcProgramBase,
    OperationAssociationBase,
    OperationBase,
    PartBase,
    ResponseBase,
    UserBase,
)
from app.types.enums import (
    ItemStatusEnum,
    MachineStatusEnum,
    OpStatusEnum,
    PriorityEnum,
)
from app.types.relation import (
    CustomerRelation,
    MachineRelation,
    MaterialPartRelation,
    MaterialRelation,
    Model3DRelation,
    MoldRelation,
    NcProgramRelation,
    OperationAssociationRelation,
    OperationRelation,
    PartRelation,
    UserRelation,
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

class FilterFieldsResponse(BaseModel):
    filter_fields: List[str]

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


class MaterialResponse(ResponseBase, MaterialBase, MaterialRelation):
    name: str
    description: str
    stock_quantity: float
    unit_of_measure: str
    lead_time: str


class Model3DResponse(ResponseBase, Model3DBase, Model3DRelation):
    name: str | None


class MoldResponse(ResponseBase, MoldBase, MoldRelation):
    name: str
    delivery_date: datetime
    priority: PriorityEnum
    quantity: int
    progress_percentage: float
    status: ItemStatusEnum
    dimensions: str | None
    created_by_id: str
    customer_id: str | None

class NcProgramResponse(ResponseBase, NcProgramBase, NcProgramRelation):
    name: str | None

class OperationAssociationResponse(
    ResponseBase, OperationAssociationBase, OperationAssociationRelation
):
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
    model_3d_id: str | None
    nc_program_id: str | None
    mold: Optional[MoldResponse] = None
    mold_id: str


class UserResponse(ResponseBase, UserBase, UserRelation):
    full_name: str
    email: str
    registration_number: str
    role: str


class LoginResponse(BaseModel):
    message: str
    user: UserResponse
    access_token: str


class RefreshTokenResponse(BaseModel):
    message: str
    access_token: str
