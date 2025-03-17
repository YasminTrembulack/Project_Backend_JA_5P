from uuid import UUID

from pydantic import BaseModel


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
