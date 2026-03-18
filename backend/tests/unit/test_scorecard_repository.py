from unittest.mock import AsyncMock
from app.scorecard_repository import ScorecardRepository
from app.score_category import ScoreCategory
from tests.unit.repository_test_case import RepositoryTestCase


class TestScorecardRepository(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = ScorecardRepository(self.conn)

  async def test_get_returns_none_when_game_not_found(self):
    self.GivenGameNotFound()
    await self.WhenScorecardIsFetched(99, 1)
    self.ThenScorecardIsNone()

  async def test_get_returns_none_when_player_not_in_game(self):
    self.GivenGameFound()
    self.GivenPlayerNotInGame()
    await self.WhenScorecardIsFetched(1, 99)
    self.ThenScorecardIsNone()

  async def test_get_returns_scorecard_with_twenty_entries(self):
    self.GivenGameFound()
    self.GivenPlayerInGame()
    self.GivenNoScoredEntries()
    await self.WhenScorecardIsFetched(1, 1)
    self.ThenEntryCountIs(20)

  async def test_get_returns_all_null_scores_when_no_entries(self):
    self.GivenGameFound()
    self.GivenPlayerInGame()
    self.GivenNoScoredEntries()
    await self.WhenScorecardIsFetched(1, 1)
    self.ThenAllScoresAreNull()

  async def test_get_returns_scored_entry(self):
    self.GivenGameFound()
    self.GivenPlayerInGame()
    self.GivenScoredEntries([('ones', 3)])
    await self.WhenScorecardIsFetched(1, 1)
    self.ThenCategoryScoreIs(ScoreCategory.ONES, 3)

  async def test_get_total_includes_scored_entries(self):
    self.GivenGameFound()
    self.GivenPlayerInGame()
    self.GivenScoredEntries([('ones', 3), ('twos', 6)])
    await self.WhenScorecardIsFetched(1, 1)
    self.ThenTotalIs(9)

  async def test_get_bonus_null_when_upper_below_threshold(self):
    self.GivenGameFound()
    self.GivenPlayerInGame()
    self.GivenScoredEntries([('ones', 3)])
    await self.WhenScorecardIsFetched(1, 1)
    self.ThenBonusIsNone()

  async def test_get_bonus_awarded_when_upper_reaches_threshold(self):
    self.GivenGameFound()
    self.GivenPlayerInGame()
    self.GivenScoredEntries([
      ('ones', 4), ('twos', 8), ('threes', 12),
      ('fours', 20), ('fives', 20), ('sixes', 20),
    ])
    await self.WhenScorecardIsFetched(1, 1)
    self.ThenBonusIs(100)

  async def test_get_total_includes_bonus(self):
    self.GivenGameFound()
    self.GivenPlayerInGame()
    self.GivenScoredEntries([
      ('ones', 4), ('twos', 8), ('threes', 12),
      ('fours', 20), ('fives', 20), ('sixes', 20),
    ])
    await self.WhenScorecardIsFetched(1, 1)
    self.ThenTotalIs(184)

  def GivenGameNotFound(self):
    self.cursor.fetchone = AsyncMock(return_value=None)

  def GivenGameFound(self):
    self.cursor.fetchone = AsyncMock(return_value=(1,))

  def GivenPlayerNotInGame(self):
    self.cursor.fetchone = AsyncMock(side_effect=[(1,), None])

  def GivenPlayerInGame(self):
    self.cursor.fetchone = AsyncMock(side_effect=[(1,), (1,)])

  def GivenNoScoredEntries(self):
    self.cursor.fetchall = AsyncMock(return_value=[])

  def GivenScoredEntries(self, entries):
    self.cursor.fetchall = AsyncMock(return_value=entries)

  async def WhenScorecardIsFetched(self, game_id, player_id):
    self.scorecard = await self.repo.get(game_id, player_id)

  def ThenScorecardIsNone(self):
    assert self.scorecard is None

  def ThenEntryCountIs(self, count):
    assert len(self.scorecard.entries) == count

  def ThenAllScoresAreNull(self):
    assert all(e.score is None for e in self.scorecard.entries)

  def ThenCategoryScoreIs(self, category, score):
    entry = next(e for e in self.scorecard.entries if e.category == category)
    assert entry.score == score

  def ThenTotalIs(self, total):
    assert self.scorecard.total == total

  def ThenBonusIsNone(self):
    assert self.scorecard.bonus is None

  def ThenBonusIs(self, bonus):
    assert self.scorecard.bonus == bonus
