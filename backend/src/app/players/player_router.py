import io
import os
from typing import Annotated
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
import aiomysql
from PIL import Image
from app.auth import make_get_current_user
from app.config import Settings
from app.database import Database
from app.games.guards import assert_player_exists_and_owns
from app.players.player import Player, PlayerCreate, PlayerUpdate
from app.players.player_repository import PlayerRepository
from app.players.player_stats import PlayerStats
from app.players.player_stats_repository import PlayerStatsRepository
from app.players.game_history import GameHistory
from app.players.game_history_repository import GameHistoryRepository


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
    '/players/{player_id}/stats',
    response_model=PlayerStats,
    responses={
      404: {'description': 'Player not found'},
    },
  )
  async def get_player_stats(
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> PlayerStats:
    """Get stats for a player."""
    stats = await PlayerStatsRepository(conn).get(player_id)
    if stats is None:
      raise HTTPException(status_code=404, detail='Player not found')
    return stats

  @router.get('/players/{player_id}/game-history', response_model=list[GameHistory])
  async def get_game_history(
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> list[GameHistory]:
    """Get finished game history for a player, sorted by most recent first."""
    return await GameHistoryRepository(conn).list_for_player(player_id)

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
    assert_player_exists_and_owns(await repo.get_by_id(player_id), current_user['sub'])
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
    assert_player_exists_and_owns(await repo.get_by_id(player_id), current_user['sub'])
    await repo.delete(player_id)
    return Response(status_code=204)

  @router.post(
    '/players/{player_id}/picture',
    response_model=Player,
    responses={
      401: {'description': 'Unauthorized'},
      403: {'description': 'Forbidden'},
      404: {'description': 'Player not found'},
      413: {'description': 'File too large'},
      415: {'description': 'Unsupported media type'},
    },
  )
  async def upload_picture(
    player_id: int,
    picture: Annotated[UploadFile, File()],
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Player:
    """Upload a profile picture for a player."""
    repo = PlayerRepository(conn)
    assert_player_exists_and_owns(await repo.get_by_id(player_id), current_user['sub'])
    if picture.content_type not in ('image/jpeg', 'image/png'):
      raise HTTPException(
        status_code=415, detail='Only JPEG and PNG images are supported'
      )
    data = await picture.read()
    if len(data) > 5 * 1024 * 1024:
      raise HTTPException(status_code=413, detail='Picture must be smaller than 5MB')
    img = Image.open(io.BytesIO(data)).convert('RGB')
    size = min(img.width, img.height)
    left = (img.width - size) // 2
    top = (img.height - size) // 2
    img = img.crop((left, top, left + size, top + size)).resize(
      (256, 256), Image.Resampling.LANCZOS
    )
    dest = f'/media/players/{player_id}.jpg'
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    img.save(dest, 'JPEG', quality=85)
    await repo.set_has_picture(player_id, True)
    updated = await repo.get_by_id(player_id)
    assert updated is not None
    return updated

  @router.delete(
    '/players/{player_id}/picture',
    status_code=204,
    responses={
      401: {'description': 'Unauthorized'},
      403: {'description': 'Forbidden'},
      404: {'description': 'Player not found'},
    },
  )
  async def delete_picture(
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
  ) -> Response:
    """Delete a player's profile picture."""
    repo = PlayerRepository(conn)
    assert_player_exists_and_owns(await repo.get_by_id(player_id), current_user['sub'])
    path = f'/media/players/{player_id}.jpg'
    if not os.path.exists(path):
      raise HTTPException(status_code=404, detail='Picture not found')
    os.remove(path)
    await repo.set_has_picture(player_id, False)
    return Response(status_code=204)

  return router
