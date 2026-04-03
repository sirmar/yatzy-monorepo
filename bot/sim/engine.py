import random
from yatzy_rules.score_category import ScoreCategory as Category
from yatzy_rules.score_calculator import calculate
from yatzy_rules.scoring_rules import calculate_bonus
from yatzy_rules.game_variant import get_variant
from yatzy_rules.game_mode import GameMode
from sim.game_state import GameState, DICE_COUNT, ROLLS_PER_TURN, INITIAL_SAVED_ROLLS

_VARIANT = get_variant(GameMode.MAXI)


def new_game() -> GameState:
  return GameState(
    dice=[1] * DICE_COUNT,
    kept=[False] * DICE_COUNT,
    rolls_remaining=ROLLS_PER_TURN,
    saved_rolls=INITIAL_SAVED_ROLLS,
  )


def roll(state: GameState, keep: list[bool]) -> GameState:
  if not state.can_roll:
    raise ValueError('No rolls remaining')

  if len(keep) != DICE_COUNT:
    raise ValueError(f'keep must have {DICE_COUNT} elements')

  new_dice = [
    state.dice[i] if keep[i] else random.randint(1, 6) for i in range(DICE_COUNT)
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
    saved_rolls=saved_rolls,
    scores=dict(state.scores),
    has_rolled=True,
  )


def score(state: GameState, category: Category) -> tuple[GameState, int]:
  if not state.has_rolled:
    raise ValueError('Must roll before scoring')

  if category not in state.available_categories:
    raise ValueError(f'{category} is already scored or invalid')

  points = calculate(category, state.dice)
  new_scores = {**state.scores, category: points}

  saved_rolls = state.saved_rolls + state.rolls_remaining

  new_state = GameState(
    dice=[1] * DICE_COUNT,
    kept=[False] * DICE_COUNT,
    rolls_remaining=ROLLS_PER_TURN,
    saved_rolls=saved_rolls,
    scores=new_scores,
    has_rolled=False,
  )

  return new_state, points


def final_score(state: GameState) -> int:
  if not state.is_done:
    raise ValueError('Game is not finished')

  # calculate_bonus (from backend) expects string keys like "ones", "twos", etc.
  scores_by_str = {str(k): v for k, v in state.scores.items()}
  bonus = calculate_bonus(scores_by_str, _VARIANT.bonus_threshold, _VARIANT.bonus_score)
  return sum(state.scores.values()) + bonus
