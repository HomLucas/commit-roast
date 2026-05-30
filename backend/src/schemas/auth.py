from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)
    preferred_currency: Optional[str] = Field(default="USD", pattern=r"^[A-Z]{3}$")


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    role: str
    preferred_currency: str
    created_at: Optional[str] = None
    last_login: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshToken(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str = Field(..., min_length=8, max_length=128)
    reset_token: str
