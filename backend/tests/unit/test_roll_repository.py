from unittest.mock import AsyncMock, call, patch
from app.games.roll_repository import RollRepository
from tests.unit.repository_test_case import RepositoryTestCase


class TestRollRepository(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = RollRepository(self.conn)

  async def test_get_turn_info_returns_none_when_not_found(self):
    self.GivenNoTurnInfo()
    await self.WhenTurnInfoIsFetched(1)
    self.ThenTurnInfoIsNone()

  async def test_get_turn_info_returns_turn_data(self):
    self.GivenTurnInfo(turn_id=7, player_id=5, rolls_used=1, rolls_remaining=0)
    await self.WhenTurnInfoIsFetched(1)
    self.ThenTurnInfoIs(7, 5, 1, 0)

  async def test_get_turn_info_uses_game_id(self):
    self.GivenNoTurnInfo()
    await self.WhenTurnInfoIsFetched(3)
    self.ThenTurnInfoQueryUsesGameId(3)

  async def test_execute_rolls_non_kept_dice(self):
    self.GivenDiceRows([(i, None, False) for i in range(6)])
    await self.WhenRollIsExecuted(7, kept_dice=[])
    self.ThenAllDiceWereUpdatedWithValues(7)

  async def test_execute_marks_kept_dice(self):
    self.GivenDiceRows([(i, 3, False) for i in range(6)])
    await self.WhenRollIsExecuted(7, kept_dice=[0, 2])
    self.ThenKeptDiceWereMarkedKept(7, [0, 2])

  async def test_execute_increments_rolls_used(self):
    self.GivenDiceRows([])
    await self.WhenRollIsExecuted(7, kept_dice=[])
    self.ThenRollsUsedWasIncremented(7)

  async def test_execute_returns_dice(self):
    self.GivenDiceRows([(0, 4, True), (1, 2, False)])
    await self.WhenRollIsExecuted(7, kept_dice=[0])
    self.ThenDiceCountIs(2)
    self.ThenFirstDieIs(index=0, value=4, kept=True)

  def GivenNoTurnInfo(self):
    self.cursor.fetchone = AsyncMock(return_value=None)

  def GivenTurnInfo(self, turn_id, player_id, rolls_used, rolls_remaining):
    self.cursor.fetchone = AsyncMock(return_value=(turn_id, player_id, rolls_used, rolls_remaining))

  def GivenDiceRows(self, rows):
    self.cursor.fetchall = AsyncMock(return_value=rows)

  async def WhenTurnInfoIsFetched(self, game_id):
    self.turn_info = await self.repo.get_turn_info(game_id)

  async def WhenRollIsExecuted(self, turn_id, kept_dice):
    with patch('app.games.roll_repository.random.randint', return_value=4):
      self.dice = await self.repo.execute(turn_id, kept_dice)

  def ThenTurnInfoIsNone(self):
    assert self.turn_info is None

  def ThenTurnInfoIs(self, turn_id, player_id, rolls_used, rolls_remaining):
    assert self.turn_info == (turn_id, player_id, rolls_used, rolls_remaining)

  def ThenTurnInfoQueryUsesGameId(self, game_id):
    query_call = self.cursor.execute.call_args_list[0]
    assert query_call[0][1] == (game_id,)

  def ThenAllDiceWereUpdatedWithValues(self, turn_id):
    update_calls = [c for c in self.cursor.execute.call_args_list if 'SET value' in c[0][0]]
    assert len(update_calls) == 6

  def ThenKeptDiceWereMarkedKept(self, turn_id, die_indices):
    kept_calls = [c for c in self.cursor.execute.call_args_list if 'SET kept = TRUE' in c[0][0]]
    assert len(kept_calls) == 1
    params = kept_calls[0][0][1]
    assert params[0] == turn_id
    assert set(params[1:]) == set(die_indices)

  def ThenRollsUsedWasIncremented(self, turn_id):
    update_call = next(c for c in self.cursor.execute.call_args_list if 'rolls_used = rolls_used + 1' in c[0][0])
    assert update_call[0][1] == (turn_id,)

  def ThenDiceCountIs(self, count):
    assert len(self.dice) == count

  def ThenFirstDieIs(self, index, value, kept):
    die = self.dice[0]
    assert die.index == index
    assert die.value == value
    assert die.kept == kept


class TestRollRepositoryGetDiceValues(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = RollRepository(self.conn)

  async def test_get_dice_values_returns_values(self):
    self.GivenDiceRows([(3,), (5,), (1,), (4,), (2,), (6,)])
    await self.WhenDiceValuesFetched(7)
    self.ThenValuesAre([3, 5, 1, 4, 2, 6])

  async def test_get_dice_values_uses_turn_id(self):
    self.GivenDiceRows([])
    await self.WhenDiceValuesFetched(42)
    self.ThenQueryUsesTurnId(42)

  def GivenDiceRows(self, rows):
    self.cursor.fetchall = AsyncMock(return_value=rows)

  async def WhenDiceValuesFetched(self, turn_id):
    self.values = await self.repo.get_dice_values(turn_id)

  def ThenValuesAre(self, values):
    assert self.values == values

  def ThenQueryUsesTurnId(self, turn_id):
    call = self.cursor.execute.call_args_list[0]
    assert call[0][1] == (turn_id,)
