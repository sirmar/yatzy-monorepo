from dataclasses import dataclass, field
from yatzy_rules.score_category import ScoreCategory as Category


@dataclass
class GameState:
  dice: list[int]
  kept: list[bool]
  rolls_remaining: int
  categories: list[Category]
  saved_rolls: int = 0
  scores: dict[Category, int] = field(default_factory=dict)
  has_rolled: bool = False

  @property
  def available_categories(self) -> list[Category]:
    return [c for c in self.categories if c not in self.scores]

  @property
  def can_roll(self) -> bool:
    return (self.rolls_remaining > 0 or self.saved_rolls > 0) and not self.is_done

  @property
  def must_score(self) -> bool:
    return self.has_rolled and self.rolls_remaining == 0 and self.saved_rolls == 0

  @property
  def is_done(self) -> bool:
    return len(self.scores) == len(self.categories)
