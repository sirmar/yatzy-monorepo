from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
  email: EmailStr
  password: str

  @field_validator('password')
  @classmethod
  def password_min_length(cls, v: str) -> str:
    if len(v) < 8:
      raise ValueError('password must be at least 8 characters')
    return v


class User(BaseModel):
  id: str
  email: str
  created_at: datetime


class TokenResponse(BaseModel):
  access_token: str
  refresh_token: str
  token_type: str = 'bearer'


class RefreshRequest(BaseModel):
  refresh_token: str


class LogoutRequest(BaseModel):
  refresh_token: str
