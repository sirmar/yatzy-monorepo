from collections import Counter
from collections.abc import Callable
from functools import partial
from yatzy_rules.score_category import ScoreCategory as Category
from yatzy_rules.score_calculator import calculate
from app.sim.game_state import GameState, DICE_COUNT
from yatzy_rules.scoring_rules import BONUS_SCORE

_UPPER_TARGET_DICE = 4

_CAT_TO_FACE = {
  Category.ONES: 1,
  Category.TWOS: 2,
  Category.THREES: 3,
  Category.FOURS: 4,
  Category.FIVES: 5,
  Category.SIXES: 6,
}

_FACE_TO_CAT = {face: cat for cat, face in _CAT_TO_FACE.items()}
_UPPER_EXPECTED = {cat: face * _UPPER_TARGET_DICE for cat, face in _CAT_TO_FACE.items()}

# Fallbacks: categories that can catch the same dice if the primary target is missed
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

_FALLBACK_WEIGHT = 0.3

_GRAB_THRESHOLDS: dict[Category, float] = {
  Category.MAXI_YATZY: 100,
  Category.FULL_STRAIGHT: 21,
  Category.LARGE_STRAIGHT: 20,
  Category.SMALL_STRAIGHT: 15,
  Category.TOWER: 34 * 0.7,
  Category.VILLA: 33 * 0.7,
  Category.THREE_PAIRS: 30 * 0.7,
}


def _upper_remaining(state: GameState) -> list[Category]:
  return [c for c in _UPPER_EXPECTED if c not in state.scores]


def _upper_surplus(state: GameState) -> int:
  surplus = 0
  for cat, expected in _UPPER_EXPECTED.items():
    if cat in state.scores:
      surplus += state.scores[cat] - expected
  return surplus


def _upper_bonus_contribution(score: float, expected: int) -> float:
  return min(score / expected, 1.0) * (BONUS_SCORE / len(_UPPER_EXPECTED)) * 2


def _maxi_yatzy_value(counts: Counter, available: set) -> float | None:
  best_face = max(counts, key=lambda f: (counts[f], f))
  count = counts[best_face]
  if count < 4:
    return None
  value = (count / DICE_COUNT) * 100.0
  if _FACE_TO_CAT[best_face] in available:
    value *= 0.25
  return value


def _fallback_value(cat: Category, dice: list[int], available: set) -> float:
  return (
    sum(calculate(fb, dice) for fb in _FALLBACKS.get(cat, []) if fb in available)
    * _FALLBACK_WEIGHT
  )


def _upper_expected_score(
  cat: Category, counts: Counter, rolls_remaining: int
) -> float:
  face = _CAT_TO_FACE[cat]
  current_count = counts[face]
  rolls = max(rolls_remaining, 1)
  p_improve = 1 - (5 / 6) ** rolls
  expected_count = current_count + (DICE_COUNT - current_count) * p_improve
  return min(expected_count, DICE_COUNT) * face


def _effective_value(cat: Category, state: GameState) -> float:
  if cat in _UPPER_EXPECTED:
    expected_score = _upper_expected_score(
      cat, Counter(state.dice), state.rolls_remaining
    )
    return expected_score + _upper_bonus_contribution(
      expected_score, _UPPER_EXPECTED[cat]
    )

  if cat == Category.MAXI_YATZY:
    return (
      _maxi_yatzy_value(Counter(state.dice), set(state.available_categories)) or 0.0
    )

  return float(calculate(cat, state.dice)) + _fallback_value(
    cat, state.dice, set(state.available_categories)
  )


def _choose_target(state: GameState) -> Category:
  return max(state.available_categories, key=lambda cat: _effective_value(cat, state))


def _keep_for_straight(dice: list[int]) -> list[bool]:
  for run in [{1, 2, 3, 4, 5, 6}, {2, 3, 4, 5, 6}, {1, 2, 3, 4, 5}]:
    if len(run & set(dice)) >= 4:
      partials = [_keep_n_of_face(dice, face, 1) for face in run]
      return [any(col) for col in zip(*partials)]
  return [False] * DICE_COUNT


def _keep_n_of_face(dice: list[int], face: int, n: int) -> list[bool]:
  keep_indices = set([i for i, d in enumerate(dice) if d == face][:n])
  return [i in keep_indices for i in range(len(dice))]


def _keep_pairs_from_faces(dice: list[int], faces: list[int]) -> list[bool]:
  partials = [_keep_n_of_face(dice, face, 2) for face in faces]
  return [any(col) for col in zip(*partials)]


def _keep_best_single(dice: list[int]) -> list[bool]:
  kept = [False] * DICE_COUNT
  kept[dice.index(max(dice))] = True
  return kept


def _keep_upper(cat: Category, dice: list[int]) -> list[bool]:
  return [d == _CAT_TO_FACE[cat] for d in dice]


def _keep_n_of_a_kind(dice: list[int], n: int) -> list[bool]:
  counts = Counter(dice)
  best = max(counts, key=lambda f: (counts[f], f))
  return _keep_n_of_face(dice, best, n)


def _keep_top_faces_with_limits(dice: list[int], limits: list[int]) -> list[bool]:
  counts = Counter(dice)
  sorted_faces = sorted(counts.keys(), key=lambda f: (counts[f], f), reverse=True)
  partials = [
    _keep_n_of_face(dice, face, limit) for face, limit in zip(sorted_faces, limits)
  ]
  return [any(col) for col in zip(*partials)]


def _keep_tower(dice: list[int]) -> list[bool]:
  return _keep_top_faces_with_limits(dice, [4, 2])


def _keep_villa(dice: list[int]) -> list[bool]:
  return _keep_top_faces_with_limits(dice, [3, 3])


def _keep_three_pairs(dice: list[int]) -> list[bool]:
  counts = Counter(dice)
  faces = sorted([face for face, count in counts.items() if count >= 2], reverse=True)[
    :3
  ]
  if faces:
    return _keep_pairs_from_faces(dice, faces)
  return _keep_best_single(dice)


def _keep_full_house(dice: list[int]) -> list[bool]:
  return _keep_top_faces_with_limits(dice, [3, 2])


def _keep_two_pairs(dice: list[int]) -> list[bool]:
  counts = Counter(dice)
  faces = sorted([face for face, count in counts.items() if count >= 2], reverse=True)[
    :2
  ]
  if len(faces) >= 2:
    return _keep_pairs_from_faces(dice, faces)
  return _keep_best_single(dice)


def _keep_one_pair(dice: list[int]) -> list[bool]:
  counts = Counter(dice)
  pairs = [face for face, count in counts.items() if count >= 2]
  if pairs:
    return _keep_n_of_face(dice, max(pairs), 2)
  return _keep_best_single(dice)


def _keep_chance(dice: list[int]) -> list[bool]:
  return [d >= 4 for d in dice]


_KEEP_DISPATCH: dict[Category, Callable[[list[int]], list[bool]]] = {
  **{cat: partial(_keep_upper, cat) for cat in _CAT_TO_FACE},
  Category.MAXI_YATZY: partial(_keep_n_of_a_kind, n=DICE_COUNT),
  Category.FULL_STRAIGHT: _keep_for_straight,
  Category.LARGE_STRAIGHT: _keep_for_straight,
  Category.SMALL_STRAIGHT: _keep_for_straight,
  Category.TOWER: _keep_tower,
  Category.VILLA: _keep_villa,
  Category.FIVE_OF_A_KIND: partial(_keep_n_of_a_kind, n=5),
  Category.FOUR_OF_A_KIND: partial(_keep_n_of_a_kind, n=4),
  Category.THREE_OF_A_KIND: partial(_keep_n_of_a_kind, n=3),
  Category.THREE_PAIRS: _keep_three_pairs,
  Category.FULL_HOUSE: _keep_full_house,
  Category.TWO_PAIRS: _keep_two_pairs,
  Category.ONE_PAIR: _keep_one_pair,
  Category.CHANCE: _keep_chance,
}


def _keep_for_target(dice: list[int], cat: Category) -> list[bool]:
  return _KEEP_DISPATCH.get(cat, lambda _: [False] * DICE_COUNT)(dice)


def _score_value(cat: Category, state: GameState) -> float:
  current_score = float(calculate(cat, state.dice))

  if cat in _UPPER_EXPECTED:
    if current_score <= 0:
      return 0.0
    if _upper_surplus(state) + (current_score - _UPPER_EXPECTED[cat]) < 0:
      return current_score * 0.5
    return current_score + _upper_bonus_contribution(
      current_score, _UPPER_EXPECTED[cat]
    )

  if cat == Category.MAXI_YATZY:
    return (
      _maxi_yatzy_value(Counter(state.dice), set(state.available_categories))
      or current_score
    )

  if cat == Category.CHANCE:
    return current_score * 0.7

  return current_score + _fallback_value(
    cat, state.dice, set(state.available_categories)
  )


def _best_scoring_category(state: GameState) -> Category | None:
  scored = [
    (cat, _score_value(cat, state))
    for cat in state.available_categories
    if calculate(cat, state.dice) > 0
  ]
  preferred = [(cat, v) for cat, v in scored if cat != Category.CHANCE]

  if not preferred:
    return Category.CHANCE if scored else None

  surplus_safe = [
    (cat, v)
    for cat, v in preferred
    if cat not in _UPPER_EXPECTED
    or _upper_surplus(state) + (calculate(cat, state.dice) - _UPPER_EXPECTED[cat]) >= 0
  ]
  chance_scored = any(cat == Category.CHANCE for cat, _ in scored)
  if not surplus_safe and chance_scored:
    return Category.CHANCE

  return max(surplus_safe or preferred, key=lambda x: x[1])[0]


def _sacrifice_category(state: GameState) -> Category:
  protect_upper = _upper_remaining(state) and _upper_surplus(state) < 0
  candidates = [
    c
    for c in state.available_categories
    if not protect_upper or c not in _UPPER_EXPECTED
  ]
  return min(
    candidates or state.available_categories,
    key=lambda cat: _effective_value(cat, state),
  )


def _best_score_action(state: GameState) -> Category:
  return _best_scoring_category(state) or _sacrifice_category(state)


def _grab_exceptional(dice: list[int], available: set) -> Category | None:
  return next(
    (
      cat
      for cat, threshold in _GRAB_THRESHOLDS.items()
      if cat in available and calculate(cat, dice) >= threshold
    ),
    None,
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
    return _best_score_action(state)

  if not state.has_rolled:
    return [False] * DICE_COUNT

  dice = state.dice
  available = set(state.available_categories)

  if (grab := _grab_exceptional(dice, available)) is not None:
    return grab

  if (keep := _keep_rolling_for_five_of_a_kind(dice, available)) is not None:
    return keep

  if state.rolls_remaining == 0 and state.saved_rolls > 0:
    for cat in available:
      if cat in _UPPER_EXPECTED and calculate(cat, dice) >= _UPPER_EXPECTED[cat]:
        return cat

  return _keep_for_target(state.dice, _choose_target(state))
