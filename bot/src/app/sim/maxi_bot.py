from collections import Counter
from collections.abc import Callable
from functools import partial
from yatzy_rules.score_category import ScoreCategory as Category
from yatzy_rules.score_calculator import calculate
from yatzy_rules.game_variant import get_variant
from yatzy_rules.game_mode import GameMode
from app.sim.game_state import GameState
from app.sim.bot_core import (
  BotConfig,
  best_score_action,
  choose_target,
  grab_exceptional,
  keep_for_target,
)
from app.sim.dice_keep import (
  keep_pairs_from_faces,
  keep_best_single,
  keep_upper,
  keep_n_of_a_kind,
  keep_top_faces_with_limits,
  keep_full_house,
  keep_two_pairs,
  keep_one_pair,
  keep_chance,
  keep_for_straight,
)

_VARIANT = get_variant(GameMode.MAXI)
DICE_COUNT = _VARIANT.dice_count

_CAT_TO_FACE = {
  Category.ONES: 1,
  Category.TWOS: 2,
  Category.THREES: 3,
  Category.FOURS: 4,
  Category.FIVES: 5,
  Category.SIXES: 6,
}

_UPPER_EXPECTED = {
  cat: face * _VARIANT.upper_target_dice for cat, face in _CAT_TO_FACE.items()
}

_FALLBACKS: dict[Category, list[Category]] = {
  Category.FIVE_OF_A_KIND: [Category.FOUR_OF_A_KIND, Category.THREE_OF_A_KIND],
  Category.VILLA: [
    Category.FOUR_OF_A_KIND,
    Category.THREE_OF_A_KIND,
    Category.FULL_HOUSE,
    Category.TWO_PAIRS,
    Category.ONE_PAIR,
  ],
  Category.TOWER: [
    Category.FOUR_OF_A_KIND,
    Category.THREE_OF_A_KIND,
    Category.FULL_HOUSE,
    Category.TWO_PAIRS,
    Category.ONE_PAIR,
  ],
  Category.FOUR_OF_A_KIND: [
    Category.THREE_OF_A_KIND,
    Category.TWO_PAIRS,
    Category.ONE_PAIR,
  ],
  Category.THREE_PAIRS: [Category.TWO_PAIRS, Category.ONE_PAIR],
  Category.FULL_HOUSE: [
    Category.THREE_OF_A_KIND,
    Category.TWO_PAIRS,
    Category.ONE_PAIR,
  ],
  Category.THREE_OF_A_KIND: [Category.TWO_PAIRS, Category.ONE_PAIR],
  Category.FULL_STRAIGHT: [Category.LARGE_STRAIGHT, Category.SMALL_STRAIGHT],
  Category.TWO_PAIRS: [Category.ONE_PAIR],
}

_GRAB_THRESHOLDS: dict[Category, float] = {
  Category.MAXI_YATZY: 100,
  Category.FULL_STRAIGHT: 21,
  Category.LARGE_STRAIGHT: 20,
  Category.SMALL_STRAIGHT: 15,
  Category.TOWER: 34 * 0.7,
  Category.VILLA: 33 * 0.7,
  Category.THREE_PAIRS: 30 * 0.7,
}

_MAXI_STRAIGHTS = [{1, 2, 3, 4, 5, 6}, {2, 3, 4, 5, 6}, {1, 2, 3, 4, 5}]


def _keep_tower(dice: list[int]) -> list[bool]:
  return keep_top_faces_with_limits(dice, [4, 2])


def _keep_villa(dice: list[int]) -> list[bool]:
  return keep_top_faces_with_limits(dice, [3, 3])


def _keep_three_pairs(dice: list[int]) -> list[bool]:
  counts = Counter(dice)
  faces = sorted([face for face, count in counts.items() if count >= 2], reverse=True)[
    :3
  ]
  if faces:
    return keep_pairs_from_faces(dice, faces)
  return keep_best_single(dice)


_KEEP_DISPATCH: dict[Category, Callable[[list[int]], list[bool]]] = {
  **{cat: partial(keep_upper, face=_CAT_TO_FACE[cat]) for cat in _CAT_TO_FACE},
  Category.MAXI_YATZY: partial(keep_n_of_a_kind, n=DICE_COUNT),
  Category.FULL_STRAIGHT: partial(keep_for_straight, straights=_MAXI_STRAIGHTS),
  Category.LARGE_STRAIGHT: partial(keep_for_straight, straights=_MAXI_STRAIGHTS),
  Category.SMALL_STRAIGHT: partial(keep_for_straight, straights=_MAXI_STRAIGHTS),
  Category.TOWER: _keep_tower,
  Category.VILLA: _keep_villa,
  Category.FIVE_OF_A_KIND: partial(keep_n_of_a_kind, n=5),
  Category.FOUR_OF_A_KIND: partial(keep_n_of_a_kind, n=4),
  Category.THREE_OF_A_KIND: partial(keep_n_of_a_kind, n=3),
  Category.THREE_PAIRS: _keep_three_pairs,
  Category.FULL_HOUSE: keep_full_house,
  Category.TWO_PAIRS: keep_two_pairs,
  Category.ONE_PAIR: keep_one_pair,
  Category.CHANCE: keep_chance,
}

_CONFIG = BotConfig(
  dice_count=DICE_COUNT,
  bonus_score=_VARIANT.bonus_score,
  upper_expected=_UPPER_EXPECTED,
  cat_to_face=_CAT_TO_FACE,
  face_to_cat={face: cat for cat, face in _CAT_TO_FACE.items()},
  fallbacks=_FALLBACKS,
  grab_thresholds=_GRAB_THRESHOLDS,
  keep_dispatch=_KEEP_DISPATCH,
  yatzy_category=_VARIANT.yatzy_category,
  yatzy_min_count=_VARIANT.dice_count - 2,
)


def _keep_rolling_for_five_of_a_kind(
  dice: list[int], available: set
) -> list[bool] | None:
  for cat in [Category.FOURS, Category.FIVES, Category.SIXES]:
    face = _CAT_TO_FACE[cat]
    if cat in available and calculate(cat, dice) == face * (DICE_COUNT - 2):
      return [d == face for d in dice]
  return None


def action(state: GameState) -> list[bool] | Category:
  if state.must_score:
    return best_score_action(state, _CONFIG)

  if not state.has_rolled:
    return [False] * DICE_COUNT

  dice = state.dice
  available = set(state.available_categories)

  if (grab := grab_exceptional(dice, available, _CONFIG)) is not None:
    return grab

  if (keep := _keep_rolling_for_five_of_a_kind(dice, available)) is not None:
    return keep

  if state.rolls_remaining == 0 and state.saved_rolls > 0:
    for cat in available:
      if cat in _UPPER_EXPECTED and calculate(cat, dice) >= _UPPER_EXPECTED[cat]:
        return cat

  return keep_for_target(state.dice, choose_target(state, _CONFIG), _CONFIG)
