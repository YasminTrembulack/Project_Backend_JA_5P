# --- USER CLASSES --- #


from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


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
