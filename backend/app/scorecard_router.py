from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import aiomysql
from app.database import Database
from app.scorecard import Scorecard
from app.scorecard_repository import ScorecardRepository


def create_scorecard_router(database: Database) -> APIRouter:
  router = APIRouter()

  @router.get(
    '/games/{game_id}/players/{player_id}/scorecard', response_model=Scorecard
  )
  async def get_scorecard(
    game_id: int,
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Scorecard:
    scorecard = await ScorecardRepository(conn).get(game_id, player_id)
    if scorecard is None:
      raise HTTPException(status_code=404, detail='Game or player not found')
    return scorecard

  return router
