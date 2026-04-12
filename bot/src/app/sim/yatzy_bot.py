from collections.abc import Callable
from functools import partial
from yatzy_rules.score_category import ScoreCategory as Category
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
  keep_upper,
  keep_n_of_a_kind,
  keep_full_house,
  keep_two_pairs,
  keep_one_pair,
  keep_chance,
  keep_for_straight,
)

_VARIANT = get_variant(GameMode.YATZY)
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
  Category.FOUR_OF_A_KIND: [
    Category.THREE_OF_A_KIND,
    Category.TWO_PAIRS,
    Category.ONE_PAIR,
  ],
  Category.FULL_HOUSE: [
    Category.THREE_OF_A_KIND,
    Category.TWO_PAIRS,
    Category.ONE_PAIR,
  ],
  Category.THREE_OF_A_KIND: [Category.TWO_PAIRS, Category.ONE_PAIR],
  Category.TWO_PAIRS: [Category.ONE_PAIR],
}

_GRAB_THRESHOLDS: dict[Category, float] = {
  Category.YATZY: 50,
  Category.LARGE_STRAIGHT: 20,
  Category.SMALL_STRAIGHT: 15,
}

_YATZY_STRAIGHTS = [{2, 3, 4, 5, 6}, {1, 2, 3, 4, 5}]

_KEEP_DISPATCH: dict[Category, Callable[[list[int]], list[bool]]] = {
  **{cat: partial(keep_upper, face=_CAT_TO_FACE[cat]) for cat in _CAT_TO_FACE},
  Category.YATZY: partial(keep_n_of_a_kind, n=DICE_COUNT),
  Category.LARGE_STRAIGHT: partial(keep_for_straight, straights=_YATZY_STRAIGHTS),
  Category.SMALL_STRAIGHT: partial(keep_for_straight, straights=_YATZY_STRAIGHTS),
  Category.FOUR_OF_A_KIND: partial(keep_n_of_a_kind, n=4),
  Category.THREE_OF_A_KIND: partial(keep_n_of_a_kind, n=3),
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


def action(state: GameState) -> list[bool] | Category:
  if state.must_score:
    return best_score_action(state, _CONFIG)

  if not state.has_rolled:
    return [False] * DICE_COUNT

  dice = state.dice
  available = set(state.available_categories)

  if (grab := grab_exceptional(dice, available, _CONFIG)) is not None:
    return grab

  return keep_for_target(state.dice, choose_target(state, _CONFIG), _CONFIG)
