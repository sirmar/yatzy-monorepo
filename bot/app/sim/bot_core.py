from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from yatzy_rules.score_category import ScoreCategory as Category
from yatzy_rules.score_calculator import calculate

_FALLBACK_WEIGHT = 0.3


@dataclass(frozen=True)
class BotConfig:
  dice_count: int
  bonus_score: int
  upper_expected: dict[Category, int]
  cat_to_face: dict[Category, int]
  face_to_cat: dict[int, Category]
  fallbacks: dict[Category, list[Category]]
  grab_thresholds: dict[Category, float]
  keep_dispatch: dict[Category, Callable[[list[int]], list[bool]]]
  yatzy_category: Category
  yatzy_min_count: int


def _upper_remaining(state, cfg: BotConfig) -> list[Category]:
  return [c for c in cfg.upper_expected if c not in state.scores]


def _upper_surplus(state, cfg: BotConfig) -> int:
  surplus = 0
  for cat, expected in cfg.upper_expected.items():
    if cat in state.scores:
      surplus += state.scores[cat] - expected
  return surplus


def _upper_bonus_contribution(score: float, expected: int, cfg: BotConfig) -> float:
  return min(score / expected, 1.0) * (cfg.bonus_score / len(cfg.upper_expected)) * 2


def _yatzy_value(counts: Counter, available: set, cfg: BotConfig) -> float | None:
  best_face = max(counts, key=lambda f: (counts[f], f))
  count = counts[best_face]
  if count < cfg.yatzy_min_count:
    return None
  value = (count / cfg.dice_count) * cfg.bonus_score
  if cfg.face_to_cat[best_face] in available:
    value *= 0.25
  return value


def _fallback_value(
  cat: Category, dice: list[int], available: set, cfg: BotConfig
) -> float:
  return (
    sum(calculate(fb, dice) for fb in cfg.fallbacks.get(cat, []) if fb in available)
    * _FALLBACK_WEIGHT
  )


def _upper_expected_score(
  cat: Category, counts: Counter, rolls_remaining: int, cfg: BotConfig
) -> float:
  face = cfg.cat_to_face[cat]
  current_count = counts[face]
  rolls = max(rolls_remaining, 1)
  p_improve = 1 - (5 / 6) ** rolls
  expected_count = current_count + (cfg.dice_count - current_count) * p_improve
  return min(expected_count, cfg.dice_count) * face


def effective_value(cat: Category, state, cfg: BotConfig) -> float:
  if cat in cfg.upper_expected:
    expected_score = _upper_expected_score(
      cat, Counter(state.dice), state.rolls_remaining, cfg
    )
    return expected_score + _upper_bonus_contribution(
      expected_score, cfg.upper_expected[cat], cfg
    )

  if cat == cfg.yatzy_category:
    return (
      _yatzy_value(Counter(state.dice), set(state.available_categories), cfg) or 0.0
    )

  return float(calculate(cat, state.dice)) + _fallback_value(
    cat, state.dice, set(state.available_categories), cfg
  )


def choose_target(state, cfg: BotConfig) -> Category:
  return max(
    state.available_categories, key=lambda cat: effective_value(cat, state, cfg)
  )


def keep_for_target(dice: list[int], cat: Category, cfg: BotConfig) -> list[bool]:
  return cfg.keep_dispatch.get(cat, lambda _: [False] * cfg.dice_count)(dice)


def score_value(cat: Category, state, cfg: BotConfig) -> float:
  current_score = float(calculate(cat, state.dice))

  if cat in cfg.upper_expected:
    if current_score <= 0:
      return 0.0
    surplus = _upper_surplus(state, cfg)
    if surplus + (current_score - cfg.upper_expected[cat]) < 0:
      return current_score * 0.5
    return current_score + _upper_bonus_contribution(
      current_score, cfg.upper_expected[cat], cfg
    )

  if cat == cfg.yatzy_category:
    return (
      _yatzy_value(Counter(state.dice), set(state.available_categories), cfg)
      or current_score
    )

  if cat == Category.CHANCE:
    return current_score * 0.7

  return current_score + _fallback_value(
    cat, state.dice, set(state.available_categories), cfg
  )


def best_scoring_category(state, cfg: BotConfig) -> Category | None:
  scored = [
    (cat, score_value(cat, state, cfg))
    for cat in state.available_categories
    if calculate(cat, state.dice) > 0
  ]
  preferred = [(cat, v) for cat, v in scored if cat != Category.CHANCE]

  if not preferred:
    return Category.CHANCE if scored else None

  surplus = _upper_surplus(state, cfg)
  surplus_safe = [
    (cat, v)
    for cat, v in preferred
    if cat not in cfg.upper_expected
    or surplus + (calculate(cat, state.dice) - cfg.upper_expected[cat]) >= 0
  ]
  chance_scored = any(cat == Category.CHANCE for cat, _ in scored)
  if not surplus_safe and chance_scored:
    return Category.CHANCE

  return max(surplus_safe or preferred, key=lambda x: x[1])[0]


def sacrifice_category(state, cfg: BotConfig) -> Category:
  protect_upper = _upper_remaining(state, cfg) and _upper_surplus(state, cfg) < 0
  candidates = [
    c
    for c in state.available_categories
    if not protect_upper or c not in cfg.upper_expected
  ]
  return min(
    candidates or state.available_categories,
    key=lambda cat: effective_value(cat, state, cfg),
  )


def best_score_action(state, cfg: BotConfig) -> Category:
  return best_scoring_category(state, cfg) or sacrifice_category(state, cfg)


def grab_exceptional(
  dice: list[int], available: set, cfg: BotConfig
) -> Category | None:
  return next(
    (
      cat
      for cat, threshold in cfg.grab_thresholds.items()
      if cat in available and calculate(cat, dice) >= threshold
    ),
    None,
  )
