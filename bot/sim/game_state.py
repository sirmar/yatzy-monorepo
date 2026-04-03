from dataclasses import dataclass, field
from yatzy_rules.score_category import ScoreCategory as Category

DICE_COUNT = 6
ROLLS_PER_TURN = 3
INITIAL_SAVED_ROLLS = 0

CATEGORIES = [
  Category.ONES,
  Category.TWOS,
  Category.THREES,
  Category.FOURS,
  Category.FIVES,
  Category.SIXES,
  Category.ONE_PAIR,
  Category.TWO_PAIRS,
  Category.THREE_PAIRS,
  Category.THREE_OF_A_KIND,
  Category.FOUR_OF_A_KIND,
  Category.FIVE_OF_A_KIND,
  Category.SMALL_STRAIGHT,
  Category.LARGE_STRAIGHT,
  Category.FULL_STRAIGHT,
  Category.FULL_HOUSE,
  Category.VILLA,
  Category.TOWER,
  Category.CHANCE,
  Category.MAXI_YATZY,
]


@dataclass
class GameState:
  # Current dice values, length == DICE_COUNT
  dice: list[int]

  # Which dice are held (not rerolled on next roll)
  kept: list[bool]

  # Rolls remaining in the current turn (0 means must score)
  rolls_remaining: int

  # Saved rolls banked from previous turns
  saved_rolls: int

  # Scored categories: category -> points awarded
  scores: dict[Category, int] = field(default_factory=dict)

  # Whether the player has rolled at least once this turn
  # (must roll before scoring)
  has_rolled: bool = False

  @property
  def available_categories(self) -> list[Category]:
    return [c for c in CATEGORIES if c not in self.scores]

  @property
  def can_roll(self) -> bool:
    return (self.rolls_remaining > 0 or self.saved_rolls > 0) and not self.is_done

  @property
  def must_score(self) -> bool:
    return self.has_rolled and self.rolls_remaining == 0 and self.saved_rolls == 0

  @property
  def is_done(self) -> bool:
    return len(self.scores) == len(CATEGORIES)
