from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
import aiomysql
from app.auth import make_get_current_user
from app.config import Settings
from app.database import Database
from app.events import EventBus
from app.games.game_player_repository import GamePlayerRepository
from app.games.game_repository import GameRepository
from yatzy_rules.game_variant import get_variant
from app.games.guards import (
  assert_game_exists,
  assert_game_active,
  assert_player_exists_and_owns,
  assert_player_in_game,
  assert_turn_active,
  assert_current_player,
  assert_has_rolled,
  assert_sequential_category,
)
from app.games.roll_repository import RollRepository
from app.games.turn_repository import TurnRepository
from app.players.player_repository import PlayerRepository
from app.scoring.score_calculator import calculate
from app.scoring.scorecard import (
  PlayerScorecard,
  Scorecard,
  ScoreRequest,
  ScoringOption,
)
from app.scoring.games_played import GamesPlayed, GamesPlayedSortBy
from app.scoring.games_played_repository import GamesPlayedRepository
from app.scoring.high_score import HighScore
from app.scoring.high_scores_repository import HighScoresRepository
from app.scoring.scorecard_repository import ScorecardRepository
from app.bot_service import play_bot_turn


def create_scorecard_router(
  database: Database, settings: Settings, event_bus: EventBus
) -> APIRouter:
  router = APIRouter(tags=['Scoring'])
  get_current_user = make_get_current_user(settings)

  @router.get(
    '/games/{game_id}/players/{player_id}/scorecard',
    response_model=Scorecard,
    responses={
      404: {'description': 'Game or player not found'},
    },
  )
  async def get_scorecard(
    game_id: int,
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> Scorecard:
    """Get the scorecard for a player in a game."""
    game = assert_game_exists(await GameRepository(conn).get_by_id(game_id))
    variant = get_variant(game.mode)
    scorecard = await ScorecardRepository(conn).get(game_id, player_id, variant)
    if scorecard is None:
      raise HTTPException(status_code=404, detail='Game or player not found')
    return scorecard

  @router.put(
    '/games/{game_id}/players/{player_id}/scorecard',
    response_model=Scorecard,
    responses={
      404: {'description': 'Game or player not found'},
      409: {
        'description': "Not the player's turn, no roll taken yet, or category already scored"
      },
    },
  )
  async def score_category(
    game_id: int,
    player_id: int,
    body: ScoreRequest,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    background_tasks: BackgroundTasks,
  ) -> Scorecard:
    """Score a category with the current dice. Ends the player's turn and advances to the next player. Ends the game when all categories are filled."""
    assert_player_exists_and_owns(
      await PlayerRepository(conn).get_by_id(player_id), current_user['sub']
    )
    game_repo = GameRepository(conn)
    game = assert_game_exists(await game_repo.get_by_id(game_id))
    assert_player_in_game(game, player_id)
    assert_game_active(game)

    roll_repo = RollRepository(conn)
    turn_id, current_player_id, rolls_remaining, saved_rolls = assert_turn_active(
      await roll_repo.get_turn_info(game_id)
    )
    assert_current_player(player_id, current_player_id)
    assert_has_rolled(rolls_remaining)

    scorecard_repo = ScorecardRepository(conn)
    if await scorecard_repo.is_category_scored(game_id, player_id, body.category):
      raise HTTPException(status_code=409, detail='Category already scored')

    variant = get_variant(game.mode)
    scored = await scorecard_repo.get_scored_categories(game_id, player_id)
    assert_sequential_category(
      variant.categories, variant.is_sequential, scored, body.category
    )

    dice = await roll_repo.get_dice_values(turn_id)
    score = calculate(body.category, dice)
    await scorecard_repo.save(game_id, player_id, body.category, score)

    new_saved = (saved_rolls + rolls_remaining) if variant.saves_rolls else 0
    await GamePlayerRepository(conn).update_saved_rolls(game_id, player_id, new_saved)

    turn_repo = TurnRepository(conn)
    total_scored = await scorecard_repo.count_all_scored(game_id)
    game_ended = total_scored >= len(game.player_ids) * len(variant.categories)
    if game_ended:
      await game_repo.end(game_id)
    else:
      current_index = game.player_ids.index(player_id)
      next_player_id = game.player_ids[(current_index + 1) % len(game.player_ids)]
      turn_number = await turn_repo.get_turn_number(turn_id)
      new_turn_id = await turn_repo.create(
        game_id, next_player_id, turn_number + 1, variant.dice_count
      )
      await game_repo.set_current_turn(game_id, new_turn_id)
      next_player = await PlayerRepository(conn).get_by_id(next_player_id)
      if next_player and next_player.is_bot:
        background_tasks.add_task(
          play_bot_turn, game_id, next_player_id, database, settings, event_bus
        )

    event_bus.publish_game(game_id)
    event_bus.publish_player(game.player_ids)

    scorecard = await scorecard_repo.get(game_id, player_id, variant)
    assert scorecard is not None
    return scorecard

  @router.get(
    '/games/{game_id}/scoreboard',
    response_model=list[PlayerScorecard],
    responses={
      404: {'description': 'Game not found'},
    },
  )
  async def get_scoreboard(
    game_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> list[PlayerScorecard]:
    """Get the full scoreboard for all players in a game."""
    game = assert_game_exists(await GameRepository(conn).get_by_id(game_id))
    variant = get_variant(game.mode)
    return await ScorecardRepository(conn).get_all(game_id, variant)

  @router.get(
    '/games/{game_id}/players/{player_id}/scoring-options',
    response_model=list[ScoringOption],
    responses={
      404: {'description': 'Game not found'},
      409: {'description': "Game is not active or not the player's turn"},
    },
  )
  async def get_scoring_options(
    game_id: int,
    player_id: int,
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> list[ScoringOption]:
    """List scoring categories available for the current dice. In sequential mode, always includes the next required category even if it scores zero. Returns an empty list if no roll has been taken yet this turn."""
    game = assert_game_exists(await GameRepository(conn).get_by_id(game_id))
    assert_player_in_game(game, player_id)
    assert_game_active(game)

    roll_repo = RollRepository(conn)
    turn_id, current_player_id, _, _ = assert_turn_active(
      await roll_repo.get_turn_info(game_id)
    )
    assert_current_player(player_id, current_player_id)

    variant = get_variant(game.mode)
    dice = await roll_repo.get_dice_values(turn_id)
    scored = await ScorecardRepository(conn).get_scored_categories(game_id, player_id)
    if variant.is_sequential:
      next_cat = next((c for c in variant.categories if c not in scored), None)
      allowed = {next_cat} if next_cat else set()
    else:
      allowed = set(variant.categories) - scored
    return [
      ScoringOption(category=cat, score=score)
      for cat in variant.categories
      if cat in allowed
      if (score := calculate(cat, dice)) > 0 or variant.is_sequential
    ]

  @router.get('/high-scores', response_model=list[HighScore])
  async def list_high_scores(
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
  ) -> list[HighScore]:
    """List all finished games sorted by total score descending."""
    return await HighScoresRepository(conn).list_all()

  @router.get('/games-played-leaderboard', response_model=list[GamesPlayed])
  async def list_games_played(
    conn: Annotated[aiomysql.Connection, Depends(database.get_db)],
    sort_by: GamesPlayedSortBy = GamesPlayedSortBy.TOTAL,
  ) -> list[GamesPlayed]:
    """List top 10 players by number of finished games played, ordered by sort_by."""
    return await GamesPlayedRepository(conn).list_top(sort_by)

  return router
