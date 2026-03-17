from unittest.mock import AsyncMock, MagicMock, call
from app.turn_repository import TurnRepository


class TestTurnRepository:
  def setup_method(self):
    self.cursor = AsyncMock()
    self.cursor.lastrowid = 7
    self.conn = MagicMock()
    self.conn.cursor = AsyncMock(return_value=self.cursor)
    self.repo = TurnRepository(self.conn)

  # create

  async def test_create_inserts_turn_with_correct_fields(self):
    await self.WhenTurnIsCreated(1, 5, 1)
    self.ThenTurnInsertWasCalledWith(1, 5, 1)

  async def test_create_inserts_six_dice(self):
    await self.WhenTurnIsCreated(1, 5, 1)
    self.ThenSixDiceWereInserted(7)

  async def test_create_returns_turn_id(self):
    await self.WhenTurnIsCreated(1, 5, 1)
    self.ThenTurnIdIs(7)

  # Given

  # When

  async def WhenTurnIsCreated(self, game_id, player_id, turn_number):
    self.turn_id = await self.repo.create(game_id, player_id, turn_number)

  # Then

  def ThenTurnInsertWasCalledWith(self, game_id, player_id, turn_number):
    insert_call = self.cursor.execute.call_args_list[0]
    assert insert_call[0][1] == (game_id, player_id, turn_number)

  def ThenSixDiceWereInserted(self, turn_id):
    dice_calls = self.cursor.execute.call_args_list[1:]
    assert len(dice_calls) == 6
    for i, c in enumerate(dice_calls):
      assert c == call('INSERT INTO turn_dice (turn_id, die_index) VALUES (%s, %s)', (turn_id, i))

  def ThenTurnIdIs(self, turn_id):
    assert self.turn_id == turn_id
