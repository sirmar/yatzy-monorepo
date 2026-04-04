from collections import Counter
from functools import partial
from yatzy_rules.score_calculator import calculate
from yatzy_rules.score_category import ScoreCategory as Category
from yatzy_rules.game_variant import get_variant
from yatzy_rules.game_mode import GameMode
from app.sim.game_state import GameState
from app.sim.dice_keep import (
  keep_pairs_from_faces,
  keep_best_single,
  keep_upper,
  keep_n_of_a_kind_weighted,
  keep_top_faces_with_limits,
  keep_full_house,
  keep_two_pairs,
  keep_one_pair,
  keep_chance,
  keep_for_straight,
)

_VARIANT = get_variant(GameMode.MAXI_SEQUENTIAL)
DICE_COUNT = _VARIANT.dice_count

_CAT_TO_FACE = {
  Category.ONES: 1,
  Category.TWOS: 2,
  Category.THREES: 3,
  Category.FOURS: 4,
  Category.FIVES: 5,
  Category.SIXES: 6,
}

_FULL_STRAIGHT = [{1, 2, 3, 4, 5, 6}]
_LARGE_STRAIGHT = [{2, 3, 4, 5, 6}]
_SMALL_STRAIGHT = [{1, 2, 3, 4, 5}]


def _keep_tower(dice: list[int]) -> list[bool]:
  return keep_top_faces_with_limits(dice, [4, 2])


def _keep_villa(dice: list[int]) -> list[bool]:
  return keep_top_faces_with_limits(dice, [3, 3])


def _keep_three_pairs(dice: list[int]) -> list[bool]:
  counts = Counter(dice)
  pairs = sorted([face for face, count in counts.items() if count >= 2], reverse=True)
  if not pairs:
    return keep_best_single(dice)
  return keep_pairs_from_faces(dice, pairs[:3])


_SAVED_ROLL_VALUE = 4.0

_SPEND_SAVED_ROLL: set[Category] = {
  Category.MAXI_YATZY,
  Category.FOUR_OF_A_KIND,
  Category.FULL_HOUSE,
  Category.THREE_OF_A_KIND,
  Category.TWO_PAIRS,
}


def _is_satisfied(target: Category, dice: list[int]) -> bool:
  score = calculate(target, dice)
  if score == 0:
    return False
  if target == Category.CHANCE:
    expected_gain = sum(3.5 - v for v in dice if v < 4)
    return expected_gain < _SAVED_ROLL_VALUE
  if target in _CAT_TO_FACE:
    face = _CAT_TO_FACE[target]
    count = score // face
    expected_gain = (DICE_COUNT - count) * face / 6
    return expected_gain < _SAVED_ROLL_VALUE
  return True


_KEEP_DISPATCH = {
  **{cat: partial(keep_upper, face=_CAT_TO_FACE[cat]) for cat in _CAT_TO_FACE},
  Category.MAXI_YATZY: partial(keep_n_of_a_kind_weighted, n=DICE_COUNT),
  Category.FULL_STRAIGHT: partial(keep_for_straight, straights=_FULL_STRAIGHT),
  Category.LARGE_STRAIGHT: partial(keep_for_straight, straights=_LARGE_STRAIGHT),
  Category.SMALL_STRAIGHT: partial(keep_for_straight, straights=_SMALL_STRAIGHT),
  Category.TOWER: _keep_tower,
  Category.VILLA: _keep_villa,
  Category.FIVE_OF_A_KIND: partial(keep_n_of_a_kind_weighted, n=5),
  Category.FOUR_OF_A_KIND: partial(keep_n_of_a_kind_weighted, n=4),
  Category.THREE_OF_A_KIND: partial(keep_n_of_a_kind_weighted, n=3),
  Category.THREE_PAIRS: _keep_three_pairs,
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

  if state.rolls_remaining > 0 and _is_satisfied(target, state.dice):
    return target

  if state.rolls_remaining == 0 and state.saved_rolls > 0:
    if calculate(target, state.dice) > 0:
      return target
    if target not in _SPEND_SAVED_ROLL:
      return target

  keep_fn = _KEEP_DISPATCH.get(target, lambda _: [False] * DICE_COUNT)
  return keep_fn(state.dice)
