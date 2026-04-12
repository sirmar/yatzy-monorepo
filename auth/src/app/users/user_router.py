from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
import aiomysql
from app.config import Settings
from app.database import Database
from app.email import EmailSender
from app.users.auth import (
  create_access_token,
  hash_password,
  make_get_current_user,
  verify_password,
)
from app.users.reset_repository import ResetRepository
from app.users.token_repository import TokenRepository
from app.users.user import (
  ChangePasswordRequest,
  ForgotPasswordRequest,
  LogoutRequest,
  RefreshRequest,
  ResetPasswordRequest,
  TokenResponse,
  User,
  UserCreate,
  VerifyEmailRequest,
)
from app.users.user_repository import UserRepository
from app.users.verification_repository import VerificationRepository


def create_user_router(
  database: Database, settings: Settings, email_sender: EmailSender
) -> APIRouter:
  router = APIRouter(tags=['Auth'])
  get_current_user = make_get_current_user(settings)

  @router.post(
    '/register',
    status_code=201,
    responses={
      201: {'description': 'User registered, verification email sent'},
      409: {'description': 'Email already registered'},
    },
  )
  async def register(
    body: UserCreate,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> dict:
    """Register a new user. A verification email will be sent before login is allowed."""
    user_repo = UserRepository(conn)
    existing = await user_repo.find_by_email(body.email)
    if existing is not None:
      raise HTTPException(status_code=409, detail='Email already registered')
    user = await user_repo.create(body.email, hash_password(body.password))
    token = await VerificationRepository(conn).create(
      user.id, settings.email_verification_expire_minutes
    )
    await email_sender.send_verification(body.email, token)
    return {'message': 'Verification email sent'}

  @router.post(
    '/login',
    response_model=TokenResponse,
    responses={
      401: {'description': 'Invalid credentials'},
      403: {'description': 'Email not verified'},
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
    if not user.email_verified:
      raise HTTPException(status_code=403, detail='Email not verified')
    token_repo = TokenRepository(conn)
    access_token = create_access_token(user.id, user.email, settings)
    refresh_token = await token_repo.create(user.id, settings.refresh_token_expire_days)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

  @router.post(
    '/verify-email',
    response_model=TokenResponse,
    responses={
      400: {'description': 'Invalid or expired token'},
    },
  )
  async def verify_email(
    body: VerifyEmailRequest,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> TokenResponse:
    """Verify email address and receive a token pair."""
    user_id = await VerificationRepository(conn).consume(body.token)
    if user_id is None:
      raise HTTPException(
        status_code=400, detail='Invalid or expired verification token'
      )
    user_repo = UserRepository(conn)
    await user_repo.set_email_verified(user_id)
    user = await user_repo.get_by_id(user_id)
    if user is None:
      raise HTTPException(
        status_code=400, detail='Invalid or expired verification token'
      )
    access_token = create_access_token(user.id, user.email, settings)
    refresh_token = await TokenRepository(conn).create(
      user.id, settings.refresh_token_expire_days
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

  @router.post(
    '/forgot-password',
    responses={
      200: {'description': 'Reset email sent if account exists'},
    },
  )
  async def forgot_password(
    body: ForgotPasswordRequest,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> dict:
    """Request a password reset email."""
    result = await UserRepository(conn).find_by_email(body.email)
    if result is not None:
      user, _ = result
      token = await ResetRepository(conn).create(
        user.id, settings.password_reset_expire_minutes
      )
      await email_sender.send_password_reset(body.email, token)
    return {'message': 'If that email is registered, a reset link has been sent'}

  @router.post(
    '/reset-password',
    status_code=204,
    responses={
      400: {'description': 'Invalid or expired token'},
    },
  )
  async def reset_password(
    body: ResetPasswordRequest,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Response:
    """Reset password using a token from email."""
    user_id = await ResetRepository(conn).consume(body.token)
    if user_id is None:
      raise HTTPException(status_code=400, detail='Invalid or expired reset token')
    await TokenRepository(conn).revoke_all_for_user(user_id)
    await UserRepository(conn).update_password(
      user_id, hash_password(body.new_password)
    )
    return Response(status_code=204)

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

  @router.put(
    '/password',
    status_code=204,
    responses={
      401: {'description': 'Unauthorized or wrong current password'},
    },
  )
  async def change_password(
    body: ChangePasswordRequest,
    payload: Annotated[dict, Depends(get_current_user)],
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Response:
    """Change the current user's password."""
    user_repo = UserRepository(conn)
    result = await user_repo.get_by_id_with_hash(payload['sub'])
    if result is None or not verify_password(body.current_password, result[1]):
      raise HTTPException(status_code=401, detail='Invalid credentials')
    await user_repo.update_password(payload['sub'], hash_password(body.new_password))
    return Response(status_code=204)

  @router.delete(
    '/me',
    status_code=204,
    responses={
      401: {'description': 'Unauthorized'},
    },
  )
  async def delete_account(
    payload: Annotated[dict, Depends(get_current_user)],
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Response:
    """Delete the current user's account."""
    user_id = payload['sub']
    await TokenRepository(conn).revoke_all_for_user(user_id)
    await UserRepository(conn).delete(user_id)
    return Response(status_code=204)

  return router
