from datetime import date, datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

import pytz
from pydantic import BaseModel, EmailStr, computed_field, field_validator

from app.core.settings import Settings
from app.types.enums import (
    CountryEnum,
    MoldStatusEnum,
    PartStatusEnum,
    PriorityEnum,
    SimpleStatusEnum,
)
from app.types.exceptions import InvalidCountryError, InvalidFieldError

T = TypeVar('T')


# --- RESPONSE CLASSES --- #


class EntityResponse(BaseModel, Generic[T]):
    message: str
    data: T


class GetAllResponse(BaseModel, Generic[T]):
    message: str
    data: List[T]
    metadata: 'Metadata'


class DeleteResponse(BaseModel):
    message: str


class PingResponse(BaseModel):
    timestamp: str
    project_name: str
    version: str


class CountyResponse(BaseModel):
    countries: List[str]


# --- USER CLASSES --- #


class UserBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    registration_number: Optional[str] = None
    role: Optional[str] = None


class UserPayload(UserBase):
    full_name: str
    email: EmailStr
    password: str
    registration_number: str
    role: Optional[str] = 'User'


class UserUpdatePayload(UserBase):
    pass


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    registration_number: str
    role: str
    created_at: str
    updated_at: str


# --- AUTHENTICATION CLASSES --- #


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    user: UserResponse
    token: str


# --- METADATA CLASS --- #


class Metadata(BaseModel):
    total: int  # Total de itens disponíveis no banco de dados
    limit: int  # Número de itens por página
    page: int  # Página atual
    total_pages: int  # Total de páginas
    has_next: bool  # Se existe uma próxima página
    has_previous: bool  # Se existe uma página anterior
    order_by: str
    desc_order: bool


# --- CUSTOMER CLASSES --- #


class CustomerBase(BaseModel):
    full_name: Optional[str] = None
    country_name: Optional[str] = None

    @field_validator('country_name')
    def validate_country(cls, v):
        if v not in [country.value for country in CountryEnum]:
            raise InvalidCountryError(f"Country '{v}' is not supported")
        return v

    @computed_field
    @property
    def country_code(self) -> str | None:
        return (
            CountryEnum.get_country_code(self.country_name)
            if self.country_name
            else None
        )


class CustomerPayload(CustomerBase):
    full_name: str
    country_name: str


class CustomerUpdatePayload(CustomerBase):
    pass


class CustomerResponse(BaseModel):
    id: UUID
    full_name: str
    country_name: str
    country_code: str
    created_at: str
    updated_at: str


# --- PART CLASSES --- #


class PartBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = 1
    status: Optional[PartStatusEnum] = PartStatusEnum.PENDING
    model_3d: Optional[SimpleStatusEnum] = SimpleStatusEnum.PENDING
    nc_program: Optional[SimpleStatusEnum] = SimpleStatusEnum.PENDING
    mold_id: Optional[str] = None


class PartPayload(PartBase):
    description: str
    mold_id: str


class PartResponse(PartBase):
    id: UUID
    name: str
    description: str
    quantity: int
    status: PartStatusEnum
    model_3d: SimpleStatusEnum
    nc_program: SimpleStatusEnum
    mold_id: str
    created_at: str
    updated_at: str


class PartUpdatePayload(PartBase):
    pass


# --- MOLD CLASSES --- #


class MoldBase(BaseModel):
    name: Optional[str] = None
    delivery_date: Optional[date] = None
    priority: Optional[PriorityEnum] = PriorityEnum.LOW
    quantity: Optional[int] = 1
    status: Optional[MoldStatusEnum] = MoldStatusEnum.PENDING
    dimensions: Optional[str] = None
    created_by_id: Optional[str] = None
    customer_id: Optional[str] = None

    @field_validator('delivery_date', mode='before')
    @classmethod
    def validate_delivery_date(cls, value):
        if value is None:
            return value
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError:
                raise InvalidFieldError('Invalid date format. Use YYYY-MM-DD.')
        time = datetime.now(pytz.timezone(Settings().TZ))
        if value < time:
            raise InvalidFieldError('Delivery date must be in the future.')

        return value


class MoldPayload(MoldBase):
    delivery_date: str
    created_by_id: str
    customer_id: str


class MoldResponde(MoldBase):
    id: UUID
    name: str
    delivery_date: str
    priority: PriorityEnum
    quantity: int
    status: MoldStatusEnum
    dimensions: str
    created_by: UserBase
    customer: CustomerBase
    created_at: str
    updated_at: str


class MoldUpdatePayload(MoldBase):
    pass


# --- MATERIAL CLASSES --- #


class MaterialBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stock_quantity: Optional[float] = 1.0
    unit_of_measure: Optional[str] = None


class MaterialPayload(MaterialBase):
    stock_quantity: float


class MaterialResponse(MaterialBase):
    id: UUID
    name: str
    description: str
    stock_quantity: float
    unit_of_measure: str
    created_at: str
    updated_at: str


class MaterialUpdatePayload(MaterialBase):
    pass

# --- OPERATION CLASSES --- #


class OperationlBase(BaseModel):
    name: Optional[str] = None
    op_type: Optional[str] = None
    machine_id: Optional[str] = None


class OperationPayload(OperationlBase):
    op_type: str


class OperationResponse(OperationlBase):
    id: UUID
    op_type: str
    machine_id: str
    created_at: str
    updated_at: str


class OperationUpdatePayload(OperationlBase):
    pass
