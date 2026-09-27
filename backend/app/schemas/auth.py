import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: Optional[str] = Field(default="VizMind User")


class UserLoginRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    refresh_token: str = Field(..., description="JWT Refresh Token")


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
