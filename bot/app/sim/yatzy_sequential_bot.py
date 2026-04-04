from functools import partial
from yatzy_rules.score_calculator import calculate
from yatzy_rules.score_category import ScoreCategory as Category
from yatzy_rules.game_variant import get_variant
from yatzy_rules.game_mode import GameMode
from app.sim.game_state import GameState
from app.sim.dice_keep import (
  keep_upper,
  keep_n_of_a_kind_weighted,
  keep_full_house,
  keep_two_pairs,
  keep_one_pair,
  keep_chance,
  keep_for_straight,
)

_VARIANT = get_variant(GameMode.YATZY_SEQUENTIAL)
DICE_COUNT = _VARIANT.dice_count

_CAT_TO_FACE = {
  Category.ONES: 1,
  Category.TWOS: 2,
  Category.THREES: 3,
  Category.FOURS: 4,
  Category.FIVES: 5,
  Category.SIXES: 6,
}

_LARGE_STRAIGHT = [{2, 3, 4, 5, 6}]
_SMALL_STRAIGHT = [{1, 2, 3, 4, 5}]

_SCORE_FIXED: set[Category] = {
  Category.TWO_PAIRS,
  Category.FULL_HOUSE,
}

_KEEP_DISPATCH = {
  **{cat: partial(keep_upper, face=_CAT_TO_FACE[cat]) for cat in _CAT_TO_FACE},
  Category.YATZY: partial(keep_n_of_a_kind_weighted, n=DICE_COUNT),
  Category.LARGE_STRAIGHT: partial(keep_for_straight, straights=_LARGE_STRAIGHT),
  Category.SMALL_STRAIGHT: partial(keep_for_straight, straights=_SMALL_STRAIGHT),
  Category.FOUR_OF_A_KIND: partial(keep_n_of_a_kind_weighted, n=4),
  Category.THREE_OF_A_KIND: partial(keep_n_of_a_kind_weighted, n=3),
  Category.FULL_HOUSE: keep_full_house,
  Category.TWO_PAIRS: keep_two_pairs,
  Category.ONE_PAIR: keep_one_pair,
  Category.CHANCE: keep_chance,
}


def action(state: GameState) -> list[bool] | Category:
  target = state.available_categories[0]

  if state.must_score:
    return target

  if not state.has_rolled:
    return [False] * DICE_COUNT

  keep_fn = _KEEP_DISPATCH.get(target, lambda _: [False] * DICE_COUNT)
  keep = keep_fn(state.dice)
  if state.rolls_remaining > 0:
    if all(keep):
      return target
    if target in _SCORE_FIXED and calculate(target, state.dice) > 0:
      return target
  return keep
