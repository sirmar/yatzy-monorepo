import pytest
from fastapi import HTTPException
from app.games.guards import assert_sequential_category
from app.scoring.score_category import ScoreCategory

MAXI_CATEGORIES = [
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


class TestAssertSequentialCategory:
  def test_standard_mode_allows_any_category(self):
    self.GivenCategories(MAXI_CATEGORIES)
    self.GivenIsSequential(False)
    self.GivenScored(set())
    self.WhenAsserted(ScoreCategory.CHANCE)

  def test_standard_mode_allows_out_of_order(self):
    self.GivenCategories(MAXI_CATEGORIES)
    self.GivenIsSequential(False)
    self.GivenScored(set())
    self.WhenAsserted(ScoreCategory.MAXI_YATZY)

  def test_sequential_allows_ones_when_none_scored(self):
    self.GivenCategories(MAXI_CATEGORIES)
    self.GivenIsSequential(True)
    self.GivenScored(set())
    self.WhenAsserted(ScoreCategory.ONES)

  def test_sequential_rejects_twos_when_none_scored(self):
    self.GivenCategories(MAXI_CATEGORIES)
    self.GivenIsSequential(True)
    self.GivenScored(set())
    self.ThenRaises409(ScoreCategory.TWOS)

  def test_sequential_rejects_last_category_when_none_scored(self):
    self.GivenCategories(MAXI_CATEGORIES)
    self.GivenIsSequential(True)
    self.GivenScored(set())
    self.ThenRaises409(ScoreCategory.MAXI_YATZY)

  def test_sequential_allows_next_after_first_scored(self):
    self.GivenCategories(MAXI_CATEGORIES)
    self.GivenIsSequential(True)
    self.GivenScored({ScoreCategory.ONES})
    self.WhenAsserted(ScoreCategory.TWOS)

  def test_sequential_rejects_skipping_after_first_scored(self):
    self.GivenCategories(MAXI_CATEGORIES)
    self.GivenIsSequential(True)
    self.GivenScored({ScoreCategory.ONES})
    self.ThenRaises409(ScoreCategory.THREES)

  def test_sequential_allows_last_category_when_all_others_scored(self):
    self.GivenCategories(MAXI_CATEGORIES)
    self.GivenIsSequential(True)
    all_except_last = set(MAXI_CATEGORIES) - {ScoreCategory.MAXI_YATZY}
    self.GivenScored(all_except_last)
    self.WhenAsserted(ScoreCategory.MAXI_YATZY)

  def GivenCategories(self, categories: list[ScoreCategory]) -> None:
    self.categories = categories

  def GivenIsSequential(self, is_sequential: bool) -> None:
    self.is_sequential = is_sequential

  def GivenScored(self, scored: set[ScoreCategory]) -> None:
    self.scored = scored

  def WhenAsserted(self, category: ScoreCategory) -> None:
    assert_sequential_category(self.categories, self.is_sequential, self.scored, category)

  def ThenRaises409(self, category: ScoreCategory) -> None:
    with pytest.raises(HTTPException) as exc:
      assert_sequential_category(self.categories, self.is_sequential, self.scored, category)
    assert exc.value.status_code == 409
