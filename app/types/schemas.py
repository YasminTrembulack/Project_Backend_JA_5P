from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel

T = TypeVar('T')


class CreateResponse(BaseModel, Generic[T]):
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
    # TODO: verificar se caso nao tenha nada cadastrado na tabela da entidade retornar []
    data: List[T]
    metadata: Metadata


class PingResponse(BaseModel):
    timestamp_br: str
    project_name: str
    version: str


class UserPayload(BaseModel):
    full_name: str
    email: str
    password: str
    registration_number: str
    role: Optional[str] = 'User'


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    role: str
    created_at: str
    updated_at: str


class LoginPayload(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    user: UserResponse
    token: str
