from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
import aiomysql
from app.auth import make_get_current_user
from app.config import Settings
from app.database import Database
from app.players.player import Player, PlayerCreate, PlayerUpdate
from app.players.player_repository import PlayerRepository


def create_player_router(database: Database, settings: Settings) -> APIRouter:
  router = APIRouter(tags=['Players'])
  get_current_user = make_get_current_user(settings)

  @router.post(
    '/players',
    status_code=201,
    response_model=Player,
    responses={
      201: {'description': 'Player created'},
      401: {'description': 'Unauthorized'},
      409: {'description': 'Player already exists for this account'},
    },
  )
  async def create_player(
    body: PlayerCreate,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Player:
    """Create a new player for the authenticated account."""
    try:
      return await PlayerRepository(conn).create(current_user['sub'], body.name)
    except aiomysql.IntegrityError:
      raise HTTPException(
        status_code=409, detail='Player already exists for this account'
      )

  @router.get(
    '/players/me',
    response_model=Player,
    responses={
      401: {'description': 'Unauthorized'},
      404: {'description': 'No player for this account'},
    },
  )
  async def get_my_player(
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Player:
    """Get the authenticated account's player."""
    player = await PlayerRepository(conn).get_by_account_id(current_user['sub'])
    if player is None:
      raise HTTPException(status_code=404, detail='No player for this account')
    return player

  @router.get('/players', response_model=list[Player])
  async def list_players(
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> list[Player]:
    """List all players."""
    return await PlayerRepository(conn).list_all()

  @router.get(
    '/players/{player_id}',
    response_model=Player,
    responses={
      404: {'description': 'Player not found'},
    },
  )
  async def get_player(
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Player:
    """Get a player by ID."""
    player = await PlayerRepository(conn).get_by_id(player_id)
    if player is None:
      raise HTTPException(status_code=404, detail='Player not found')
    return player

  @router.put(
    '/players/{player_id}',
    response_model=Player,
    responses={
      401: {'description': 'Unauthorized'},
      403: {'description': 'Forbidden'},
      404: {'description': 'Player not found'},
    },
  )
  async def update_player(
    player_id: int,
    body: PlayerUpdate,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Player:
    """Update a player's name."""
    repo = PlayerRepository(conn)
    player = await repo.get_by_id(player_id)
    if player is None:
      raise HTTPException(status_code=404, detail='Player not found')
    if player.account_id != current_user['sub']:
      raise HTTPException(status_code=403, detail='Forbidden')
    updated = await repo.update(player_id, body.name)
    assert updated is not None
    return updated

  @router.delete(
    '/players/{player_id}',
    status_code=204,
    responses={
      401: {'description': 'Unauthorized'},
      403: {'description': 'Forbidden'},
      404: {'description': 'Player not found'},
    },
  )
  async def delete_player(
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Response:
    """Delete a player."""
    repo = PlayerRepository(conn)
    player = await repo.get_by_id(player_id)
    if player is None:
      raise HTTPException(status_code=404, detail='Player not found')
    if player.account_id != current_user['sub']:
      raise HTTPException(status_code=403, detail='Forbidden')
    await repo.delete(player_id)
    return Response(status_code=204)

  return router
