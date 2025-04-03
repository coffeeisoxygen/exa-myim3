from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.user.models import UserRole


class Token(BaseModel):
    """Schema untuk response token."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema untuk data dalam token."""

    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class UserLogin(BaseModel):
    """Schema untuk login request."""

    username: str
    password: str


class UserCreate(BaseModel):
    """Schema untuk membuat user baru."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    password_confirm: str = Field(..., min_length=6, max_length=100)
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.VIEWER

    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("username")
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v


class UserUpdate(BaseModel):
    """Schema untuk mengupdate user."""

    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema untuk response user."""

    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True
