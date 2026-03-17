from typing import Annotated
from collections.abc import AsyncGenerator
from fastapi import APIRouter, Depends
import aiomysql
from app.database import Database
from app.player import Player, PlayerCreate
from app.player_repository import PlayerRepository


def create_player_router(database: Database) -> APIRouter:
  router = APIRouter()

  async def get_conn() -> AsyncGenerator[aiomysql.Connection, None]:
    async for conn in database.get_db():
      yield conn

  @router.post('/players', status_code=201, response_model=Player)
  async def create_player(
    body: PlayerCreate,
    conn: Annotated[aiomysql.Connection, Depends(get_conn)],
  ) -> Player:
    return await PlayerRepository(conn).create(body.name)

  @router.get('/players', response_model=list[Player])
  async def list_players(
    conn: Annotated[aiomysql.Connection, Depends(get_conn)],
  ) -> list[Player]:
    return await PlayerRepository(conn).list_all()

  return router
