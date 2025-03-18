from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class ResponseCreate(GenericModel, Generic[T]):
    message: str
    data: T


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    full_name: str
    email: str
    password: str


class UserPublic(BaseModel):
    id: UUID
    full_name: str
    email: str
    created_at: str
    updated_at: str
