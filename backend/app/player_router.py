from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
import aiomysql
from app.database import Database
from app.player import Player, PlayerCreate, PlayerUpdate
from app.player_repository import PlayerRepository


def create_player_router(database: Database) -> APIRouter:
  router = APIRouter()

  @router.post('/players', status_code=201, response_model=Player)
  async def create_player(
    body: PlayerCreate,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Player:
    return await PlayerRepository(conn).create(body.name)

  @router.get('/players', response_model=list[Player])
  async def list_players(
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> list[Player]:
    return await PlayerRepository(conn).list_all()

  @router.get('/players/{player_id}', response_model=Player)
  async def get_player(
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Player:
    player = await PlayerRepository(conn).get_by_id(player_id)
    if player is None:
      raise HTTPException(status_code=404, detail='Player not found')
    return player

  @router.put('/players/{player_id}', response_model=Player)
  async def update_player(
    player_id: int,
    body: PlayerUpdate,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Player:
    player = await PlayerRepository(conn).update(player_id, body.name)
    if player is None:
      raise HTTPException(status_code=404, detail='Player not found')
    return player

  @router.delete('/players/{player_id}', status_code=204)
  async def delete_player(
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Response:
    deleted = await PlayerRepository(conn).delete(player_id)
    if not deleted:
      raise HTTPException(status_code=404, detail='Player not found')
    return Response(status_code=204)

  return router
