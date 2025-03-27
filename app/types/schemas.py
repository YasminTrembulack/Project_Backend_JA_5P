from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, EmailStr, computed_field, field_validator

from app.models.customer import CountryEnum
from app.types.exceptions import InvalidCountryError

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
    timestamp_br: str
    project_name: str
    version: str


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
    role: str
    created_at: str
    updated_at: str


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
