
# --- AUTHENTICATION CLASSES --- #


from typing import Generic, List, TypeVar
from pydantic import BaseModel, EmailStr

from app.types import UserResponse


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


class TimeUnitResponse(BaseModel):
    time_unit: List[str]



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
