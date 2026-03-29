from datetime import datetime
from typing import Annotated
from pydantic import AfterValidator, BaseModel, EmailStr


def _check_password_length(v: str) -> str:
  if len(v) < 8:
    raise ValueError('password must be at least 8 characters')
  return v


Password = Annotated[str, AfterValidator(_check_password_length)]


class UserCreate(BaseModel):
  email: EmailStr
  password: Password


class User(BaseModel):
  id: str
  email: str
  email_verified: bool
  created_at: datetime


class TokenResponse(BaseModel):
  access_token: str
  refresh_token: str
  token_type: str = 'bearer'


class RefreshRequest(BaseModel):
  refresh_token: str


class LogoutRequest(BaseModel):
  refresh_token: str


class VerifyEmailRequest(BaseModel):
  token: str


class ForgotPasswordRequest(BaseModel):
  email: EmailStr


class ResetPasswordRequest(BaseModel):
  token: str
  new_password: Password


class ChangePasswordRequest(BaseModel):
  current_password: str
  new_password: Password
