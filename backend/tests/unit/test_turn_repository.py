from unittest.mock import AsyncMock
from app.games.turn_repository import TurnRepository
from tests.unit.repository_test_case import RepositoryTestCase


class TestTurnRepository(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.cursor.lastrowid = 7
    self.repo = TurnRepository(self.conn)

  async def test_create_inserts_turn_with_correct_fields(self):
    await self.WhenTurnIsCreated(1, 5, 1)
    self.ThenTurnInsertWasCalledWith(1, 5, 1)

  async def test_create_inserts_six_dice(self):
    await self.WhenTurnIsCreated(1, 5, 1)
    self.ThenSixDiceWereInserted(7)

  async def test_create_returns_turn_id(self):
    await self.WhenTurnIsCreated(1, 5, 1)
    self.ThenTurnIdIs(7)

  async def WhenTurnIsCreated(self, game_id, player_id, turn_number):
    self.turn_id = await self.repo.create(game_id, player_id, turn_number)

  def ThenTurnInsertWasCalledWith(self, game_id, player_id, turn_number):
    insert_call = self.cursor.execute.call_args_list[0]
    assert insert_call[0][1] == (game_id, player_id, turn_number)

  def ThenSixDiceWereInserted(self, turn_id):
    dice_call = self.cursor.execute.call_args_list[1]
    assert 'INSERT INTO turn_dice' in dice_call[0][0]
    assert dice_call[0][0].count('(%s, %s)') == 6
    expected_values = [v for i in range(6) for v in (turn_id, i)]
    assert list(dice_call[0][1]) == expected_values

  def ThenTurnIdIs(self, turn_id):
    assert self.turn_id == turn_id


class TestTurnRepositoryGetTurnNumber(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = TurnRepository(self.conn)

  async def test_get_turn_number_returns_number(self):
    self.GivenTurnNumber(3)
    await self.WhenTurnNumberFetched(7)
    self.ThenTurnNumberIs(3)

  async def test_get_turn_number_uses_turn_id(self):
    self.GivenTurnNumber(1)
    await self.WhenTurnNumberFetched(42)
    self.ThenQueryUsesTurnId(42)

  def GivenTurnNumber(self, number):
    self.cursor.fetchone = AsyncMock(return_value=(number,))

  async def WhenTurnNumberFetched(self, turn_id):
    self.turn_number = await self.repo.get_turn_number(turn_id)

  def ThenTurnNumberIs(self, number):
    assert self.turn_number == number

  def ThenQueryUsesTurnId(self, turn_id):
    call = self.cursor.execute.call_args_list[0]
    assert call[0][1] == (turn_id,)
