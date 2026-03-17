from typing import Annotated
from collections.abc import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
import aiomysql
from app.database import Database
from app.game import Game, GameCreate
from app.game_join import GameJoin
from app.game_start import GameStart
from app.game_repository import GameRepository
from app.game_player_repository import GamePlayerRepository
from app.turn_repository import TurnRepository


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

  @router.post('/games/{game_id}/start', response_model=Game)
  async def start_game(
    game_id: int,
    body: GameStart,
    conn: Annotated[aiomysql.Connection, Depends(get_conn)],
  ) -> Game:
    game = await GameRepository(conn).get_by_id(game_id)
    if game is None:
      raise HTTPException(status_code=404, detail='Game not found')
    if game.status != 'lobby':
      raise HTTPException(status_code=409, detail='Game is not in lobby')
    if body.player_id != game.creator_id:
      raise HTTPException(status_code=403, detail='Only the creator can start the game')
    turn_id = await TurnRepository(conn).create(game_id, body.player_id, 1)
    started = await GameRepository(conn).start(game_id, turn_id)
    assert started is not None
    return started

  @router.post('/games/{game_id}/join', response_model=Game)
  async def join_game(
    game_id: int,
    body: GameJoin,
    conn: Annotated[aiomysql.Connection, Depends(get_conn)],
  ) -> Game:
    game = await GameRepository(conn).get_by_id(game_id)
    if game is None:
      raise HTTPException(status_code=404, detail='Game not found')
    if game.status != 'lobby':
      raise HTTPException(status_code=409, detail='Game is not in lobby')
    if body.player_id in game.player_ids:
      raise HTTPException(status_code=409, detail='Player already in game')
    if len(game.player_ids) >= 6:
      raise HTTPException(status_code=409, detail='Game is full')
    await GamePlayerRepository(conn).add(game_id, body.player_id, len(game.player_ids) + 1)
    updated = await GameRepository(conn).get_by_id(game_id)
    assert updated is not None
    return updated

  @router.get('/games', response_model=list[Game])
  async def list_games(
    conn: Annotated[aiomysql.Connection, Depends(get_conn)],
  ) -> list[Game]:
    return await GameRepository(conn).list_all()

  return router
