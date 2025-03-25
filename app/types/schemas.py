from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, EmailStr

T = TypeVar('T')


class EntityResponse(BaseModel, Generic[T]):
    message: str
    data: T


class Metadata(BaseModel):
    total: int  # Total de itens disponíveis no banco de dados
    limit: int  # Número de itens por página
    page: int  # Página atual
    total_pages: int  # Total de páginas
    has_next: bool  # Se existe uma próxima página
    has_previous: bool  # Se existe uma página anterior
    order_by: str
    desc_order: bool


class GetAllResponse(BaseModel, Generic[T]):
    message: str
    data: List[T]
    metadata: Metadata


class DeleteResponse(BaseModel):
    message: str


class PingResponse(BaseModel):
    timestamp_br: str
    project_name: str
    version: str


class UserPayload(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    registration_number: str
    role: Optional[str] = 'User'


class UserUpdatePayload(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    registration_number: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    role: str
    created_at: str
    updated_at: str


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    user: UserResponse
    token: str
