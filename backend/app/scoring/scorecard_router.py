from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import aiomysql
from app.database import Database
from app.games.game_player_repository import GamePlayerRepository
from app.games.game_repository import GameRepository
from app.games.game_status import GameStatus
from app.games.roll_repository import RollRepository
from app.games.turn_repository import TurnRepository
from app.scoring.score_calculator import calculate
from app.scoring.score_category import ScoreCategory
from app.scoring.scorecard import Scorecard, ScoreRequest, ScoringOption
from app.scoring.scorecard_repository import ScorecardRepository


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

  @router.put(
    '/games/{game_id}/players/{player_id}/scorecard', response_model=Scorecard
  )
  async def score_category(
    game_id: int,
    player_id: int,
    body: ScoreRequest,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Scorecard:
    game_repo = GameRepository(conn)
    game = await game_repo.get_by_id(game_id)
    if game is None:
      raise HTTPException(status_code=404, detail='Game not found')
    if player_id not in game.player_ids:
      raise HTTPException(status_code=404, detail='Player not in game')
    if game.status != GameStatus.ACTIVE:
      raise HTTPException(status_code=409, detail='Game is not active')

    roll_repo = RollRepository(conn)
    turn_info = await roll_repo.get_turn_info(game_id)
    if turn_info is None:
      raise HTTPException(status_code=409, detail='No active turn found')

    turn_id, current_player_id, rolls_used, rolls_remaining = turn_info
    if player_id != current_player_id:
      raise HTTPException(status_code=403, detail='Not your turn')
    if rolls_used == 0:
      raise HTTPException(status_code=409, detail='Must roll before scoring')

    scorecard_repo = ScorecardRepository(conn)
    if await scorecard_repo.is_category_scored(game_id, player_id, body.category):
      raise HTTPException(status_code=409, detail='Category already scored')

    dice = await roll_repo.get_dice_values(turn_id)
    score = calculate(body.category, dice)
    await scorecard_repo.save(game_id, player_id, body.category, score)

    new_remaining = max(0, 3 + rolls_remaining - rolls_used)
    await GamePlayerRepository(conn).update_rolls_remaining(
      game_id, player_id, new_remaining
    )

    turn_repo = TurnRepository(conn)
    total_scored = await scorecard_repo.count_all_scored(game_id)
    if total_scored >= len(game.player_ids) * 20:
      await game_repo.end(game_id)
    else:
      current_index = game.player_ids.index(player_id)
      next_player_id = game.player_ids[(current_index + 1) % len(game.player_ids)]
      turn_number = await turn_repo.get_turn_number(turn_id)
      new_turn_id = await turn_repo.create(game_id, next_player_id, turn_number + 1)
      await game_repo.set_current_turn(game_id, new_turn_id)

    scorecard = await scorecard_repo.get(game_id, player_id)
    if scorecard is None:
      raise HTTPException(status_code=404, detail='Scorecard not found')
    return scorecard

  @router.get(
    '/games/{game_id}/players/{player_id}/scoring-options',
    response_model=list[ScoringOption],
  )
  async def get_scoring_options(
    game_id: int,
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> list[ScoringOption]:
    game = await GameRepository(conn).get_by_id(game_id)
    if game is None:
      raise HTTPException(status_code=404, detail='Game not found')
    if player_id not in game.player_ids:
      raise HTTPException(status_code=404, detail='Player not in game')
    if game.status != GameStatus.ACTIVE:
      raise HTTPException(status_code=409, detail='Game is not active')

    roll_repo = RollRepository(conn)
    turn_info = await roll_repo.get_turn_info(game_id)
    if turn_info is None:
      raise HTTPException(status_code=409, detail='No active turn found')

    turn_id, current_player_id, _, _ = turn_info
    if player_id != current_player_id:
      raise HTTPException(status_code=403, detail='Not your turn')

    dice = await roll_repo.get_dice_values(turn_id)
    scored = await ScorecardRepository(conn).get_scored_categories(game_id, player_id)
    return [
      ScoringOption(category=cat, score=score)
      for cat in ScoreCategory
      if cat not in scored
      if (score := calculate(cat, dice)) > 0
    ]

  return router
