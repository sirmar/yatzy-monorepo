from unittest.mock import AsyncMock
from app.scoring.scorecard_repository import ScorecardRepository
from app.scoring.score_category import ScoreCategory
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


class TestScorecardRepositoryGetAll(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = ScorecardRepository(self.conn)

  async def test_get_all_returns_scorecard_per_player(self):
    self.GivenPlayersInGame([(1,), (2,)])
    self.GivenEntriesPerPlayer([[], []])
    await self.WhenGetAllIsCalled(1)
    self.ThenResultHasPlayerCount(2)

  async def test_get_all_returns_empty_for_game_with_no_players(self):
    self.GivenPlayersInGame([])
    await self.WhenGetAllIsCalled(1)
    self.ThenResultIsEmpty()

  def GivenPlayersInGame(self, player_rows):
    self._player_rows = player_rows
    self.cursor.fetchall = AsyncMock(return_value=player_rows)

  def GivenEntriesPerPlayer(self, entries_per_player):
    self.cursor.fetchall = AsyncMock(side_effect=[self._player_rows] + entries_per_player)

  async def WhenGetAllIsCalled(self, game_id):
    self.result = await self.repo.get_all(game_id)

  def ThenResultHasPlayerCount(self, count):
    assert len(self.result) == count

  def ThenResultIsEmpty(self):
    assert self.result == []


class TestScorecardRepositoryIsScored(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = ScorecardRepository(self.conn)

  async def test_is_category_scored_returns_true_when_entry_exists(self):
    self.GivenEntryFound()
    await self.WhenIsCategoryScored(1, 1, ScoreCategory.ONES)
    self.ThenResultIsTrue()

  async def test_is_category_scored_returns_false_when_no_entry(self):
    self.GivenEntryNotFound()
    await self.WhenIsCategoryScored(1, 1, ScoreCategory.ONES)
    self.ThenResultIsFalse()

  def GivenEntryFound(self):
    self.cursor.fetchone = AsyncMock(return_value=(1,))

  def GivenEntryNotFound(self):
    self.cursor.fetchone = AsyncMock(return_value=None)

  async def WhenIsCategoryScored(self, game_id, player_id, category):
    self.result = await self.repo.is_category_scored(game_id, player_id, category)

  def ThenResultIsTrue(self):
    assert self.result is True

  def ThenResultIsFalse(self):
    assert self.result is False


class TestScorecardRepositorySave(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = ScorecardRepository(self.conn)

  async def test_save_inserts_entry(self):
    await self.WhenSaved(1, 2, ScoreCategory.CHANCE, 21)
    self.ThenInsertWasCalled(1, 2, ScoreCategory.CHANCE, 21)

  async def WhenSaved(self, game_id, player_id, category, score):
    await self.repo.save(game_id, player_id, category, score)

  def ThenInsertWasCalled(self, game_id, player_id, category, score):
    call_args = self.cursor.execute.call_args[0]
    assert 'INSERT INTO scorecard_entries' in call_args[0]
    assert (game_id, player_id, category, score) == call_args[1]


class TestScorecardRepositoryCountAllScored(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = ScorecardRepository(self.conn)

  async def test_count_all_scored_returns_count(self):
    self.GivenCountIs(5)
    await self.WhenCountAllScored(1)
    self.ThenCountIs(5)

  def GivenCountIs(self, count):
    self.cursor.fetchone = AsyncMock(return_value=(count,))

  async def WhenCountAllScored(self, game_id):
    self.result = await self.repo.count_all_scored(game_id)

  def ThenCountIs(self, count):
    assert self.result == count
