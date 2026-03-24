from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
import aiomysql
from app.config import Settings
from app.database import Database
from app.users.auth import (
  create_access_token,
  hash_password,
  make_get_current_user,
  verify_password,
)
from app.users.token_repository import TokenRepository
from app.users.user import (
  LogoutRequest,
  RefreshRequest,
  TokenResponse,
  User,
  UserCreate,
)
from app.users.user_repository import UserRepository


def create_user_router(database: Database, settings: Settings) -> APIRouter:
  router = APIRouter(tags=['Auth'])
  get_current_user = make_get_current_user(settings)

  @router.post(
    '/register',
    status_code=201,
    response_model=TokenResponse,
    responses={
      201: {'description': 'User registered'},
      409: {'description': 'Email already registered'},
    },
  )
  async def register(
    body: UserCreate,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> TokenResponse:
    """Register a new user with email and password."""
    user_repo = UserRepository(conn)
    existing = await user_repo.find_by_email(body.email)
    if existing is not None:
      raise HTTPException(status_code=409, detail='Email already registered')
    user = await user_repo.create(body.email, hash_password(body.password))
    token_repo = TokenRepository(conn)
    access_token = create_access_token(user.id, user.email, settings)
    refresh_token = await token_repo.create(user.id, settings.refresh_token_expire_days)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

  @router.post(
    '/login',
    response_model=TokenResponse,
    responses={
      401: {'description': 'Invalid credentials'},
    },
  )
  async def login(
    body: UserCreate,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> TokenResponse:
    """Login with email and password."""
    result = await UserRepository(conn).find_by_email(body.email)
    if result is None or not verify_password(body.password, result[1]):
      raise HTTPException(status_code=401, detail='Invalid credentials')
    user, _ = result
    token_repo = TokenRepository(conn)
    access_token = create_access_token(user.id, user.email, settings)
    refresh_token = await token_repo.create(user.id, settings.refresh_token_expire_days)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

  @router.post(
    '/refresh',
    response_model=TokenResponse,
    responses={
      401: {'description': 'Invalid or expired refresh token'},
    },
  )
  async def refresh(
    body: RefreshRequest,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> TokenResponse:
    """Exchange a refresh token for a new token pair."""
    user_id = await TokenRepository(conn).consume(body.refresh_token)
    if user_id is None:
      raise HTTPException(status_code=401, detail='Invalid or expired refresh token')
    user = await UserRepository(conn).get_by_id(user_id)
    if user is None:
      raise HTTPException(status_code=401, detail='User not found')
    token_repo = TokenRepository(conn)
    access_token = create_access_token(user.id, user.email, settings)
    new_refresh_token = await token_repo.create(
      user.id, settings.refresh_token_expire_days
    )
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)

  @router.post(
    '/logout',
    status_code=204,
  )
  async def logout(
    body: LogoutRequest,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Response:
    """Revoke a refresh token."""
    await TokenRepository(conn).revoke(body.refresh_token)
    return Response(status_code=204)

  @router.get(
    '/me',
    response_model=User,
    responses={
      401: {'description': 'Unauthorized'},
    },
  )
  async def me(
    payload: Annotated[dict, Depends(get_current_user)],
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> User:
    """Get the current authenticated user."""
    user = await UserRepository(conn).get_by_id(payload['sub'])
    if user is None:
      raise HTTPException(status_code=401, detail='User not found')
    return user

  return router
