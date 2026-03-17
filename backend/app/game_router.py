from typing import Annotated
from collections.abc import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
import aiomysql
from app.database import Database
from app.game import Game, GameCreate
from app.game_repository import GameRepository


def create_game_router(database: Database) -> APIRouter:
  router = APIRouter()

  async def get_conn() -> AsyncGenerator[aiomysql.Connection, None]:
    async for conn in database.get_db():
      yield conn

  @router.post('/games', status_code=201, response_model=Game)
  async def create_game(
    body: GameCreate,
    conn: Annotated[aiomysql.Connection, Depends(get_conn)],
  ) -> Game:
    return await GameRepository(conn).create(body.creator_id)

  @router.get('/games/{game_id}', response_model=Game)
  async def get_game(
    game_id: int,
    conn: Annotated[aiomysql.Connection, Depends(get_conn)],
  ) -> Game:
    game = await GameRepository(conn).get_by_id(game_id)
    if game is None:
      raise HTTPException(status_code=404, detail='Game not found')
    return game

  @router.get('/games', response_model=list[Game])
  async def list_games(
    conn: Annotated[aiomysql.Connection, Depends(get_conn)],
  ) -> list[Game]:
    return await GameRepository(conn).list_all()

  return router
