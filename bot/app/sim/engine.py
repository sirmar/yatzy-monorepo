import random
from yatzy_rules.score_category import ScoreCategory as Category
from yatzy_rules.score_calculator import calculate, calculate_bonus
from yatzy_rules.game_variant import GameVariant
from app.sim.game_state import GameState


class Engine:
  def __init__(self, variant: GameVariant) -> None:
    self._variant = variant

  def new_game(self) -> GameState:
    v = self._variant
    return GameState(
      dice=[1] * v.dice_count,
      kept=[False] * v.dice_count,
      rolls_remaining=v.rolls_per_turn,
      categories=v.categories,
    )

  def roll(self, state: GameState, keep: list[bool]) -> GameState:
    v = self._variant
    if not state.can_roll:
      raise ValueError('No rolls remaining')
    if len(keep) != v.dice_count:
      raise ValueError(f'keep must have {v.dice_count} elements')

    new_dice = [
      state.dice[i] if keep[i] else random.randint(1, 6) for i in range(v.dice_count)
    ]

    if state.rolls_remaining > 0:
      rolls_remaining = state.rolls_remaining - 1
      saved_rolls = state.saved_rolls
    else:
      rolls_remaining = 0
      saved_rolls = state.saved_rolls - 1

    return GameState(
      dice=new_dice,
      kept=keep,
      rolls_remaining=rolls_remaining,
      categories=state.categories,
      saved_rolls=saved_rolls,
      scores=dict(state.scores),
      has_rolled=True,
    )

  def score(self, state: GameState, category: Category) -> tuple[GameState, int]:
    v = self._variant
    if not state.has_rolled:
      raise ValueError('Must roll before scoring')
    if category not in state.available_categories:
      raise ValueError(f'{category} is already scored or invalid')

    points = calculate(category, state.dice)
    saved_rolls = state.saved_rolls + state.rolls_remaining if v.saves_rolls else 0

    return GameState(
      dice=[1] * v.dice_count,
      kept=[False] * v.dice_count,
      rolls_remaining=v.rolls_per_turn,
      categories=state.categories,
      saved_rolls=saved_rolls,
      scores={**state.scores, category: points},
      has_rolled=False,
    ), points

  def final_score(self, state: GameState) -> int:
    if not state.is_done:
      raise ValueError('Game is not finished')
    scores_by_str = {str(k): v for k, v in state.scores.items()}
    v = self._variant
    bonus = calculate_bonus(scores_by_str, v.bonus_threshold, v.bonus_score)
    return sum(state.scores.values()) + bonus
