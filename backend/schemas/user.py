"""
User schemas - Schema Người dùng
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ---- Role / Vai trò ----

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True


# ---- User / Người dùng ----

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role_id: int


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role_id: int
    role: Optional[RoleResponse] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
