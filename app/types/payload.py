from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.types.base import (
    BaseQueryParams,
    CustomerBase,
    MachineBase,
    MaterialBase,
    MaterialPartBase,
    MoldBase,
    OperationAssociationBase,
    OperationBase,
    PartBase,
    UserBase,
)
from app.types.enums import (
    ItemStatusEnum,
    MachineStatusEnum,
    MaterialStatusEnum,
    OpStatusEnum,
    PriorityEnum,
    SimpleStatusEnum,
)


# --- AUTHENTICATION CLASSES --- #

class LoginPayload(BaseModel):
    email: EmailStr
    password: str


# --- CUSTOMER CLASSES --- #

class CustomerPayload(CustomerBase):
    full_name: str
    country_name: str


class CustomerUpdatePayload(CustomerBase):
    pass


class CustomerQueryParams(BaseQueryParams):
    order_by: str = 'created_at'


# --- MACHINE CLASSES --- #


class MachinePayload(MachineBase):
    m_type: str


class MachineUpdatePayload(MachineBase):
    status: Optional[MachineStatusEnum] = None


class MachineQueryParams(BaseQueryParams):
    order_by: str = 'created_at'


# --- MATERIAL PARTS CLASSES --- #


class MaterialPartPayload(MaterialPartBase):
    material_id: str
    part_id: str


class MaterialPartUpdatePayload(MaterialPartBase):
    quantity: Optional[float] = None
    status: Optional[MaterialStatusEnum] = None


class MaterialPartQueryParams(BaseQueryParams):
    order_by: str = 'created_at'


# --- MATERIAL CLASSES --- #


class MaterialPayload(MaterialBase):
    stock_quantity: float
    lead_time: str


class MaterialUpdatePayload(MaterialBase):
    stock_quantity: Optional[float] = None
    

class MaterialQueryParams(BaseQueryParams):
    order_by: str = 'created_at'

# --- MOLD CLASSES --- #


class MoldPayload(MoldBase):
    delivery_date: datetime
    customer_id: str


class MoldUpdatePayload(MoldBase):
    priority: Optional[PriorityEnum] = None
    quantity: Optional[int] = None
    status: Optional[ItemStatusEnum] = None
    progress_percentage: Optional[float] = None


class MoldQueryParams(BaseQueryParams):
    order_by: str = 'created_at'


# --- OPERATION ASSOCIATION CLASSES --- #


class OperationAssociationPayload(OperationAssociationBase):
    item_id: str
    operation_id: str


class OperationAssociationUpdatePayload(OperationAssociationBase):
    status: Optional[OpStatusEnum] = None


# --- OPERATION CLASSES --- #


class OperationPayload(OperationBase):
    op_type: str


class OperationUpdatePayload(OperationBase):
    pass


class OperationQueryParams(BaseQueryParams):
    order_by: str = 'created_at'


# --- PART CLASSES --- #


class PartPayload(PartBase):
    mold_id: str


class PartUpdatePayload(PartBase):
    quantity: Optional[int] = None
    progress_percentage: Optional[float] = None
    status: Optional[ItemStatusEnum] = None
    model_3d: Optional[SimpleStatusEnum] = None
    nc_program: Optional[SimpleStatusEnum] = None


class PartQueryParams(BaseQueryParams):
    order_by: str = 'created_at'


# --- USER CLASSES --- #


class UserPayload(UserBase):
    full_name: str
    email: EmailStr
    password: str
    registration_number: str
    role: Optional[str] = 'User'


class UserUpdatePayload(UserBase):
    pass
