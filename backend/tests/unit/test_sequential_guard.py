import pytest
from fastapi import HTTPException
from app.games.game_mode import GameMode
from app.games.guards import assert_sequential_category
from app.scoring.score_category import ScoreCategory


class TestAssertSequentialCategory:
  def test_standard_mode_allows_any_category(self):
    self.GivenMode(GameMode.STANDARD)
    self.GivenScored(set())
    self.WhenAsserted(ScoreCategory.CHANCE)

  def test_standard_mode_allows_out_of_order(self):
    self.GivenMode(GameMode.STANDARD)
    self.GivenScored(set())
    self.WhenAsserted(ScoreCategory.MAXI_YATZY)

  def test_sequential_allows_ones_when_none_scored(self):
    self.GivenMode(GameMode.SEQUENTIAL)
    self.GivenScored(set())
    self.WhenAsserted(ScoreCategory.ONES)

  def test_sequential_rejects_twos_when_none_scored(self):
    self.GivenMode(GameMode.SEQUENTIAL)
    self.GivenScored(set())
    self.ThenRaises409(ScoreCategory.TWOS)

  def test_sequential_rejects_last_category_when_none_scored(self):
    self.GivenMode(GameMode.SEQUENTIAL)
    self.GivenScored(set())
    self.ThenRaises409(ScoreCategory.MAXI_YATZY)

  def test_sequential_allows_next_after_first_scored(self):
    self.GivenMode(GameMode.SEQUENTIAL)
    self.GivenScored({ScoreCategory.ONES})
    self.WhenAsserted(ScoreCategory.TWOS)

  def test_sequential_rejects_skipping_after_first_scored(self):
    self.GivenMode(GameMode.SEQUENTIAL)
    self.GivenScored({ScoreCategory.ONES})
    self.ThenRaises409(ScoreCategory.THREES)

  def test_sequential_allows_last_category_when_all_others_scored(self):
    self.GivenMode(GameMode.SEQUENTIAL)
    all_except_last = set(ScoreCategory) - {ScoreCategory.MAXI_YATZY}
    self.GivenScored(all_except_last)
    self.WhenAsserted(ScoreCategory.MAXI_YATZY)

  def GivenMode(self, mode: GameMode) -> None:
    self.mode = mode

  def GivenScored(self, scored: set[ScoreCategory]) -> None:
    self.scored = scored

  def WhenAsserted(self, category: ScoreCategory) -> None:
    assert_sequential_category(self.mode, self.scored, category)

  def ThenRaises409(self, category: ScoreCategory) -> None:
    with pytest.raises(HTTPException) as exc:
      assert_sequential_category(self.mode, self.scored, category)
    assert exc.value.status_code == 409
