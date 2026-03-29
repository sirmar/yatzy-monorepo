import asyncio
import json
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
import aiomysql
from app.auth import make_get_current_user
from app.config import Settings
from app.database import Database
from app.events import EventBus
from app.games.game import Game, GameCreate
from app.games.game_status import GameStatus
from app.games.guards import (
  assert_game_exists,
  assert_game_active,
  assert_game_in_lobby,
  assert_game_deletable,
  assert_player_exists,
  assert_player_in_game,
  assert_player_not_in_game,
  assert_game_not_full,
  assert_is_creator,
  assert_not_creator,
  assert_player_owns,
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
from app.games.game_variant import get_variant
from app.games.roll_repository import RollRepository
from app.games.turn_repository import TurnRepository
from app.players.player_repository import PlayerRepository


def create_game_router(
  database: Database, settings: Settings, event_bus: EventBus
) -> APIRouter:
  router = APIRouter(tags=['Games'])
  get_current_user = make_get_current_user(settings)

  @router.post(
    '/games',
    status_code=201,
    response_model=Game,
    responses={
      201: {'description': 'Game created'},
    },
  )
  async def create_game(
    body: GameCreate,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Game:
    """Create a new game. The requesting player becomes the creator."""
    player = assert_player_exists(
      await PlayerRepository(conn).get_by_id(body.creator_id)
    )
    assert_player_owns(player, current_user['sub'])
    game = await GameRepository(conn).create(body.creator_id, body.mode)
    event_bus.publish_lobby()
    return game

  @router.get('/games', response_model=list[Game])
  async def list_games(
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    status: Annotated[GameStatus | None, Query()] = None,
  ) -> list[Game]:
    """List all games, optionally filtered by status."""
    return await GameRepository(conn).list_all(status)

  @router.get('/games/lobby/events')
  async def lobby_events(
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> StreamingResponse:
    """SSE stream: fires when any lobby-visible game changes."""

    async def generator():
      q = event_bus.subscribe_lobby()
      try:
        while True:
          if await request.is_disconnected():
            break
          try:
            event = await asyncio.wait_for(q.get(), timeout=15.0)
            yield f'data: {json.dumps(event)}\n\n'
          except asyncio.TimeoutError:
            yield ': heartbeat\n\n'
      finally:
        event_bus.unsubscribe_lobby(q)

    return StreamingResponse(generator(), media_type='text/event-stream')

  @router.get('/games/active/events')
  async def active_game_events(
    request: Request,
    player_id: Annotated[int, Query()],
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> StreamingResponse:
    """SSE stream: fires when a game the authenticated player participates in changes status."""
    player = assert_player_exists(await PlayerRepository(conn).get_by_id(player_id))
    assert_player_owns(player, current_user['sub'])

    async def generator():
      q = event_bus.subscribe_player(player_id)
      try:
        while True:
          if await request.is_disconnected():
            break
          try:
            event = await asyncio.wait_for(q.get(), timeout=15.0)
            yield f'data: {json.dumps(event)}\n\n'
          except asyncio.TimeoutError:
            yield ': heartbeat\n\n'
      finally:
        event_bus.unsubscribe_player(player_id, q)

    return StreamingResponse(generator(), media_type='text/event-stream')

  @router.get(
    '/games/{game_id}',
    response_model=Game,
    responses={
      404: {'description': 'Game not found'},
    },
  )
  async def get_game(
    game_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Game:
    """Get a game by ID."""
    return assert_game_exists(await GameRepository(conn).get_by_id(game_id))

  @router.delete(
    '/games/{game_id}',
    status_code=204,
    responses={
      404: {'description': 'Game not found'},
      409: {'description': 'Game cannot be deleted (already started or ended)'},
    },
  )
  async def delete_game(
    game_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> None:
    """Delete a game. Only lobby games can be deleted."""
    repo = GameRepository(conn)
    game = assert_game_exists(await repo.get_by_id(game_id))
    player = assert_player_exists(
      await PlayerRepository(conn).get_by_id(game.creator_id)
    )
    assert_player_owns(player, current_user['sub'])
    assert_game_deletable(game)
    await repo.soft_delete(game_id)
    event_bus.publish_lobby()

  @router.delete(
    '/games/{game_id}/players/{player_id}',
    response_model=Game,
    responses={
      403: {'description': 'Creator cannot leave the game'},
      404: {'description': 'Game not found'},
      409: {'description': 'Player not in game or game is not in lobby'},
    },
  )
  async def leave_game(
    game_id: int,
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Game:
    """Leave a lobby game. The creator cannot leave — delete the game instead."""
    player = assert_player_exists(await PlayerRepository(conn).get_by_id(player_id))
    assert_player_owns(player, current_user['sub'])
    game = assert_game_exists(await GameRepository(conn).get_by_id(game_id))
    assert_game_in_lobby(game)
    assert_player_in_game(game, player_id)
    assert_not_creator(game, player_id)
    await GamePlayerRepository(conn).remove(game_id, player_id)
    updated = await GameRepository(conn).get_by_id(game_id)
    if updated is None:
      raise HTTPException(status_code=409, detail='Game could not be retrieved')
    event_bus.publish_lobby()
    return updated

  @router.post(
    '/games/{game_id}/join',
    response_model=Game,
    responses={
      404: {'description': 'Game not found'},
      409: {
        'description': 'Game is not in lobby, player already joined, or game is full'
      },
    },
  )
  async def join_game(
    game_id: int,
    body: GameJoin,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Game:
    """Join a game that is in the lobby. Up to 6 players can join."""
    player = assert_player_exists(
      await PlayerRepository(conn).get_by_id(body.player_id)
    )
    assert_player_owns(player, current_user['sub'])
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
    event_bus.publish_lobby()
    return updated

  @router.post(
    '/games/{game_id}/start',
    response_model=Game,
    responses={
      404: {'description': 'Game not found'},
      409: {'description': 'Game is not in lobby or player is not the creator'},
    },
  )
  async def start_game(
    game_id: int,
    body: GameStart,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Game:
    """Start a game. Only the creator can start it."""
    player = assert_player_exists(
      await PlayerRepository(conn).get_by_id(body.player_id)
    )
    assert_player_owns(player, current_user['sub'])
    game = assert_game_exists(await GameRepository(conn).get_by_id(game_id))
    assert_game_in_lobby(game)
    assert_is_creator(game, body.player_id)
    variant = get_variant(game.mode)
    turn_id = await TurnRepository(conn).create(
      game_id, body.player_id, 1, variant.dice_count
    )
    started = await GameRepository(conn).start(game_id, turn_id)
    if started is None:
      raise HTTPException(status_code=409, detail='Game could not be started')
    event_bus.publish_game(game_id)
    event_bus.publish_lobby()
    event_bus.publish_player(started.player_ids)
    return started

  @router.post(
    '/games/{game_id}/abort',
    response_model=Game,
    responses={
      404: {'description': 'Game not found'},
      409: {'description': 'Game is not active'},
    },
  )
  async def abort_game(
    game_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Game:
    """Abort an active game. The game is marked as abandoned. Only the creator can abort."""
    repo = GameRepository(conn)
    game = assert_game_exists(await repo.get_by_id(game_id))
    assert_game_active(game)
    player = assert_player_exists(
      await PlayerRepository(conn).get_by_id(game.creator_id)
    )
    assert_player_owns(player, current_user['sub'])
    aborted = await repo.abort(game_id)
    if aborted is None:
      raise HTTPException(status_code=409, detail='Game could not be aborted')
    event_bus.publish_game(game_id)
    event_bus.publish_lobby()
    event_bus.publish_player(aborted.player_ids)
    return aborted

  @router.post(
    '/games/{game_id}/roll',
    response_model=DiceResponse,
    responses={
      404: {'description': 'Game not found'},
      409: {
        'description': "Game is not active, not the player's turn, or no rolls remaining"
      },
    },
  )
  async def roll_dice(
    game_id: int,
    body: RollRequest,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> DiceResponse:
    """Roll dice for the current player's turn. Pass kept_dice to hold specific dice between rolls."""
    player = assert_player_exists(
      await PlayerRepository(conn).get_by_id(body.player_id)
    )
    assert_player_owns(player, current_user['sub'])
    game = assert_game_exists(await GameRepository(conn).get_by_id(game_id))
    assert_game_active(game)
    roll_repo = RollRepository(conn)
    turn_id, current_player_id, rolls_remaining, saved_rolls = assert_turn_active(
      await roll_repo.get_turn_info(game_id)
    )
    assert_current_player(body.player_id, current_player_id)
    assert_rolls_remaining(rolls_remaining, saved_rolls)
    dice = await roll_repo.execute(
      turn_id, game_id, body.player_id, rolls_remaining, body.kept_dice
    )
    event_bus.publish_game(game_id)
    return DiceResponse(dice=dice)

  @router.get(
    '/games/{game_id}/state',
    response_model=GameState,
    responses={
      404: {'description': 'Game not found'},
    },
  )
  async def get_game_state(
    game_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> GameState:
    """Get the current game state. Returns dice, current player and scores when the game has ended."""
    state = await GameStateRepository(conn).get(game_id)
    if state is None:
      raise HTTPException(status_code=404, detail='Game not found')
    return state

  @router.get('/games/{game_id}/events')
  async def game_events(
    game_id: int,
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> StreamingResponse:
    """SSE stream: fires when in-game state changes (roll, score, abort)."""

    async def generator():
      q = event_bus.subscribe_game(game_id)
      try:
        while True:
          if await request.is_disconnected():
            break
          try:
            event = await asyncio.wait_for(q.get(), timeout=15.0)
            yield f'data: {json.dumps(event)}\n\n'
          except asyncio.TimeoutError:
            yield ': heartbeat\n\n'
      finally:
        event_bus.unsubscribe_game(game_id, q)

    return StreamingResponse(generator(), media_type='text/event-stream')

  return router
