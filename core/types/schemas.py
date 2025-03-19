from typing import Generic, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel

T = TypeVar('T')


class ResponseCreate(BaseModel, Generic[T]):
    message: str
    data: T


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    full_name: str
    email: str
    password: str
    role: Literal['user', 'admin'] = 'user'

class UserPublic(BaseModel):
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
    user: UserPublic
    token: str
