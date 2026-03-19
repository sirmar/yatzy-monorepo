from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import aiomysql
from app.database import Database
from app.games.game import Game, GameCreate
from app.games.guards import (
  assert_game_exists,
  assert_game_active,
  assert_game_in_lobby,
  assert_game_deletable,
  assert_player_not_in_game,
  assert_game_not_full,
  assert_is_creator,
  assert_turn_active,
  assert_current_player,
  assert_rolls_remaining,
)
from app.games.requests import GameJoin, GameStart, RollRequest
from app.games.dice import DiceResponse
from app.games.game_repository import GameRepository
from app.games.game_player_repository import GamePlayerRepository
from app.games.game_state import GameState
from app.games.game_state_repository import GameStateRepository
from app.games.roll_repository import RollRepository
from app.games.turn_repository import TurnRepository


def create_game_router(database: Database) -> APIRouter:
  router = APIRouter()

  @router.post('/games', status_code=201, response_model=Game)
  async def create_game(
    body: GameCreate,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Game:
    return await GameRepository(conn).create(body.creator_id)

  @router.get('/games/{game_id}', response_model=Game)
  async def get_game(
    game_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Game:
    return assert_game_exists(await GameRepository(conn).get_by_id(game_id))

  @router.post('/games/{game_id}/end', response_model=Game)
  async def end_game(
    game_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Game:
    repo = GameRepository(conn)
    game = assert_game_exists(await repo.get_by_id(game_id))
    assert_game_active(game)
    ended = await repo.end(game_id)
    if ended is None:
      raise HTTPException(status_code=409, detail='Game could not be ended')
    return ended

  @router.post('/games/{game_id}/start', response_model=Game)
  async def start_game(
    game_id: int,
    body: GameStart,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Game:
    game = assert_game_exists(await GameRepository(conn).get_by_id(game_id))
    assert_game_in_lobby(game)
    assert_is_creator(game, body.player_id)
    turn_id = await TurnRepository(conn).create(game_id, body.player_id, 1)
    started = await GameRepository(conn).start(game_id, turn_id)
    if started is None:
      raise HTTPException(status_code=409, detail='Game could not be started')
    return started

  @router.post('/games/{game_id}/join', response_model=Game)
  async def join_game(
    game_id: int,
    body: GameJoin,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Game:
    game = assert_game_exists(await GameRepository(conn).get_by_id(game_id))
    assert_game_in_lobby(game)
    assert_player_not_in_game(game, body.player_id)
    assert_game_not_full(game)
    await GamePlayerRepository(conn).add(
      game_id, body.player_id, len(game.player_ids) + 1
    )
    updated = await GameRepository(conn).get_by_id(game_id)
    if updated is None:
      raise HTTPException(status_code=409, detail='Game could not be retrieved')
    return updated

  @router.post('/games/{game_id}/roll', response_model=DiceResponse)
  async def roll_dice(
    game_id: int,
    body: RollRequest,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> DiceResponse:
    game = assert_game_exists(await GameRepository(conn).get_by_id(game_id))
    assert_game_active(game)
    roll_repo = RollRepository(conn)
    turn_id, current_player_id, rolls_used, rolls_remaining = assert_turn_active(
      await roll_repo.get_turn_info(game_id)
    )
    assert_current_player(body.player_id, current_player_id)
    assert_rolls_remaining(rolls_used, rolls_remaining)
    dice = await roll_repo.execute(turn_id, body.kept_dice)
    return DiceResponse(dice=dice)

  @router.get('/games/{game_id}/state', response_model=GameState)
  async def get_game_state(
    game_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> GameState:
    state = await GameStateRepository(conn).get(game_id)
    if state is None:
      raise HTTPException(status_code=404, detail='Game not found')
    return state

  @router.delete('/games/{game_id}', status_code=204)
  async def delete_game(
    game_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> None:
    repo = GameRepository(conn)
    game = assert_game_exists(await repo.get_by_id(game_id))
    assert_game_deletable(game)
    await repo.soft_delete(game_id)

  @router.get('/games', response_model=list[Game])
  async def list_games(
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> list[Game]:
    return await GameRepository(conn).list_all()

  return router
