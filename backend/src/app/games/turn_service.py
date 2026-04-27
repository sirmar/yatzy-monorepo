from dataclasses import dataclass
from app.games.game_repository import GameRepository
from app.games.turn_repository import TurnRepository
from app.scoring.score_calculator import calculate
from app.scoring.scorecard import Scorecard
from app.scoring.scorecard_repository import ScorecardRepository
from yatzy_rules.score_category import ScoreCategory
from yatzy_rules.game_variant import get_variant


@dataclass
class TurnResult:
  scorecard: Scorecard
  game_ended: bool
  next_player_id: int | None
  player_ids: list[int]


class TurnService:
  def __init__(self, conn):
    self._conn = conn

  async def score_and_advance(
    self, game_id: int, player_id: int, category: ScoreCategory
  ) -> TurnResult:
    game_repo = GameRepository(self._conn)
    turn_repo = TurnRepository(self._conn)
    scorecard_repo = ScorecardRepository(self._conn)

    game = await game_repo.get_by_id(game_id)
    assert game is not None
    variant = get_variant(game.mode)

    turn_info = await turn_repo.get_turn_info(game_id)
    assert turn_info is not None
    turn_id, _, rolls_remaining, saved_rolls = turn_info

    dice = await turn_repo.get_dice_values(turn_id)
    score = calculate(category, dice)
    await scorecard_repo.save(game_id, player_id, category, score)

    new_saved = (saved_rolls + rolls_remaining) if variant.saves_rolls else 0
    await game_repo.update_saved_rolls(game_id, player_id, new_saved)

    total_scored = await scorecard_repo.count_all_scored(game_id)
    game_ended = total_scored >= len(game.player_ids) * len(variant.categories)
    next_player_id = None

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

    scorecard = await scorecard_repo.get(game_id, player_id, variant)
    assert scorecard is not None

    return TurnResult(
      scorecard=scorecard,
      game_ended=game_ended,
      next_player_id=next_player_id,
      player_ids=game.player_ids,
    )
