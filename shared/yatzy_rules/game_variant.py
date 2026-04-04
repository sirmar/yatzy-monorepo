from dataclasses import dataclass
from yatzy_rules.game_mode import GameMode
from yatzy_rules.score_category import ScoreCategory


@dataclass(frozen=True)
class GameVariant:
  dice_count: int
  rolls_per_turn: int
  categories: list[ScoreCategory]
  yatzy_category: ScoreCategory
  upper_target_dice: int
  bonus_threshold: int
  bonus_score: int
  saves_rolls: bool
  is_sequential: bool


_MAXI_CATEGORIES = [
  ScoreCategory.ONES,
  ScoreCategory.TWOS,
  ScoreCategory.THREES,
  ScoreCategory.FOURS,
  ScoreCategory.FIVES,
  ScoreCategory.SIXES,
  ScoreCategory.ONE_PAIR,
  ScoreCategory.TWO_PAIRS,
  ScoreCategory.THREE_PAIRS,
  ScoreCategory.THREE_OF_A_KIND,
  ScoreCategory.FOUR_OF_A_KIND,
  ScoreCategory.FIVE_OF_A_KIND,
  ScoreCategory.SMALL_STRAIGHT,
  ScoreCategory.LARGE_STRAIGHT,
  ScoreCategory.FULL_STRAIGHT,
  ScoreCategory.FULL_HOUSE,
  ScoreCategory.VILLA,
  ScoreCategory.TOWER,
  ScoreCategory.CHANCE,
  ScoreCategory.MAXI_YATZY,
]

_YATZY_CATEGORIES = [
  ScoreCategory.ONES,
  ScoreCategory.TWOS,
  ScoreCategory.THREES,
  ScoreCategory.FOURS,
  ScoreCategory.FIVES,
  ScoreCategory.SIXES,
  ScoreCategory.ONE_PAIR,
  ScoreCategory.TWO_PAIRS,
  ScoreCategory.THREE_OF_A_KIND,
  ScoreCategory.FOUR_OF_A_KIND,
  ScoreCategory.SMALL_STRAIGHT,
  ScoreCategory.LARGE_STRAIGHT,
  ScoreCategory.FULL_HOUSE,
  ScoreCategory.CHANCE,
  ScoreCategory.YATZY,
]

_VARIANTS: dict[GameMode, GameVariant] = {
  GameMode.MAXI: GameVariant(
    dice_count=6,
    rolls_per_turn=3,
    categories=_MAXI_CATEGORIES,
    yatzy_category=ScoreCategory.MAXI_YATZY,
    upper_target_dice=4,
    bonus_threshold=84,
    bonus_score=100,
    saves_rolls=True,
    is_sequential=False,
  ),
  GameMode.MAXI_SEQUENTIAL: GameVariant(
    dice_count=6,
    rolls_per_turn=3,
    categories=_MAXI_CATEGORIES,
    yatzy_category=ScoreCategory.MAXI_YATZY,
    upper_target_dice=4,
    bonus_threshold=84,
    bonus_score=100,
    saves_rolls=True,
    is_sequential=True,
  ),
  GameMode.YATZY: GameVariant(
    dice_count=5,
    rolls_per_turn=3,
    categories=_YATZY_CATEGORIES,
    yatzy_category=ScoreCategory.YATZY,
    upper_target_dice=3,
    bonus_threshold=63,
    bonus_score=50,
    saves_rolls=False,
    is_sequential=False,
  ),
  GameMode.YATZY_SEQUENTIAL: GameVariant(
    dice_count=5,
    rolls_per_turn=3,
    categories=_YATZY_CATEGORIES,
    yatzy_category=ScoreCategory.YATZY,
    upper_target_dice=3,
    bonus_threshold=63,
    bonus_score=50,
    saves_rolls=False,
    is_sequential=True,
  ),
}


def get_variant(mode: GameMode) -> GameVariant:
  return _VARIANTS[mode]
