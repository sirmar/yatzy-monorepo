from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import aiomysql
from app.database import Database
from app.users.reset_repository import ResetRepository
from app.users.user_repository import UserRepository
from app.users.verification_repository import VerificationRepository


def create_dev_router(database: Database) -> APIRouter:
  router = APIRouter(tags=['Dev'])

  @router.get('/dev/verification-token')
  async def get_verification_token(
    email: str,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> dict:
    user_result = await UserRepository(conn).find_by_email(email)
    if user_result is None:
      raise HTTPException(status_code=404, detail='User not found')
    user, _ = user_result
    token = await VerificationRepository(conn).get_latest_token(user.id)
    if token is None:
      raise HTTPException(status_code=404, detail='No active verification token')
    return {'token': token}

  @router.get('/dev/reset-token')
  async def get_reset_token(
    email: str,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> dict:
    user_result = await UserRepository(conn).find_by_email(email)
    if user_result is None:
      raise HTTPException(status_code=404, detail='User not found')
    user, _ = user_result
    token = await ResetRepository(conn).get_latest_token(user.id)
    if token is None:
      raise HTTPException(status_code=404, detail='No active reset token')
    return {'token': token}

  return router
