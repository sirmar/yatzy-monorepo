from typing import Annotated
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import Settings

_bearer = HTTPBearer()


def make_get_current_user(settings: Settings):
  async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
  ) -> dict:
    try:
      return jwt.decode(
        credentials.credentials,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
      )
    except jwt.ExpiredSignatureError:
      raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
      raise HTTPException(status_code=401, detail='Invalid token')

  return get_current_user
