from datetime import datetime, timedelta, timezone
from typing import Annotated
import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import Settings

_bearer = HTTPBearer()


def hash_password(plain: str) -> str:
  return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
  return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str, email: str, settings: Settings) -> str:
  payload = {
    'sub': user_id,
    'email': email,
    'exp': datetime.now(timezone.utc)
    + timedelta(minutes=settings.access_token_expire_minutes),
  }
  return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict:
  try:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
  except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail='Token expired')
  except jwt.InvalidTokenError:
    raise HTTPException(status_code=401, detail='Invalid token')


def make_get_current_user(settings: Settings):
  async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
  ) -> dict:
    return decode_access_token(credentials.credentials, settings)

  return get_current_user
