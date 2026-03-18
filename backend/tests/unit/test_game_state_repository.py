from unittest.mock import AsyncMock
from app.games.game_state_repository import GameStateRepository
from tests.unit.repository_test_case import RepositoryTestCase


class TestGameStateRepository(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = GameStateRepository(self.conn)

  async def test_get_returns_none_when_not_found(self):
    self.GivenDatabaseReturnsNoRow()
    await self.WhenStateIsFetched(99)
    self.ThenStateIsNone()

  async def test_get_returns_status_for_lobby_game(self):
    self.GivenDatabaseReturnsGame(status='lobby', current_turn=None)
    await self.WhenStateIsFetched(1)
    self.ThenStateStatusIs('lobby')

  async def test_get_returns_no_dice_for_lobby_game(self):
    self.GivenDatabaseReturnsGame(status='lobby', current_turn=None)
    await self.WhenStateIsFetched(1)
    self.ThenDiceIsNone()

  async def test_get_returns_current_player_for_active_game(self):
    self.GivenDatabaseReturnsGame(status='active', current_turn=7)
    self.GivenTurnBelongsToPlayer(5)
    self.GivenDatabaseReturnsDice([])
    await self.WhenStateIsFetched(1)
    self.ThenCurrentPlayerIdIs(5)

  async def test_get_returns_six_dice_for_active_game(self):
    self.GivenDatabaseReturnsGame(status='active', current_turn=7)
    self.GivenTurnBelongsToPlayer(5)
    self.GivenDatabaseReturnsDice([(i, None, False) for i in range(6)])
    await self.WhenStateIsFetched(1)
    self.ThenDiceCountIs(6)

  async def test_get_maps_die_fields(self):
    self.GivenDatabaseReturnsGame(status='active', current_turn=7)
    self.GivenTurnBelongsToPlayer(5)
    self.GivenDatabaseReturnsDice([(0, 4, True)])
    await self.WhenStateIsFetched(1)
    self.ThenFirstDieIs(index=0, value=4, kept=True)

  async def test_get_filters_deleted(self):
    self.GivenDatabaseReturnsNoRow()
    await self.WhenStateIsFetched(1)
    self.ThenGameQueryFiltersOnDeletedAt()

  async def test_get_filters_deleted_on_turns(self):
    self.GivenDatabaseReturnsGame(status='active', current_turn=7)
    self.GivenTurnBelongsToPlayer(5)
    self.GivenDatabaseReturnsDice([])
    await self.WhenStateIsFetched(1)
    self.ThenTurnsQueryFiltersOnDeletedAt()

  def GivenDatabaseReturnsNoRow(self):
    self.cursor.fetchone = AsyncMock(return_value=None)

  def GivenDatabaseReturnsGame(self, status='lobby', current_turn=None):
    self.cursor.fetchone = AsyncMock(return_value=(status, current_turn))

  def GivenTurnBelongsToPlayer(self, player_id):
    self.cursor.fetchone = AsyncMock(side_effect=[
      self.cursor.fetchone.return_value,
      (player_id,),
    ])

  def GivenDatabaseReturnsDice(self, dice):
    self.cursor.fetchall = AsyncMock(return_value=dice)

  async def WhenStateIsFetched(self, game_id):
    self.state = await self.repo.get(game_id)

  def ThenStateIsNone(self):
    assert self.state is None

  def ThenStateStatusIs(self, status):
    assert self.state.status == status

  def ThenDiceIsNone(self):
    assert self.state.dice is None

  def ThenCurrentPlayerIdIs(self, player_id):
    assert self.state.current_player_id == player_id

  def ThenDiceCountIs(self, count):
    assert len(self.state.dice) == count

  def ThenFirstDieIs(self, index, value, kept):
    die = self.state.dice[0]
    assert die.index == index
    assert die.value == value
    assert die.kept == kept

  def ThenGameQueryFiltersOnDeletedAt(self):
    query = self.cursor.execute.call_args_list[0][0][0]
    assert 'deleted_at IS NULL' in query

  def ThenTurnsQueryFiltersOnDeletedAt(self):
    query = self.cursor.execute.call_args_list[1][0][0]
    assert 'deleted_at IS NULL' in query
