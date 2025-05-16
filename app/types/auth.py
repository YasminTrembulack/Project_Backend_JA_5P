
from pydantic import BaseModel, EmailStr

from app.types.user import UserResponse
# --- AUTHENTICATION CLASSES --- #


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    user: UserResponse
    access_token: str


class RefreshTokenResponse(BaseModel):
    message: str
    access_token: str
