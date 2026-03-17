from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, call
from app.player_repository import PlayerRepository


class TestPlayerRepository:
  def setup_method(self):
    self.cursor = AsyncMock()
    self.cursor.lastrowid = 7
    self.cursor.fetchone = AsyncMock(return_value=(7, 'Alice', datetime(2024, 6, 1, 10, 0, 0)))
    self.conn = MagicMock()
    self.conn.cursor = AsyncMock(return_value=self.cursor)

  async def test_maps_row_to_player_fields(self):
    self.GivenARepository()
    await self.WhenPlayerIsCreatedWithName('Alice')
    self.ThenTheReturnedPlayerMapsAllRowFields()

  async def test_selects_inserted_row_by_id(self):
    self.GivenARepository()
    await self.WhenPlayerIsCreatedWithName('Alice')
    self.ThenTheSelectUsesLastRowId()

  async def test_insert_uses_provided_name(self):
    self.GivenARepository()
    await self.WhenPlayerIsCreatedWithName('Bob')
    self.ThenInsertWasCalledWithName('Bob')

  def GivenARepository(self):
    self.repo = PlayerRepository(self.conn)

  async def WhenPlayerIsCreatedWithName(self, name):
    self.player = await self.repo.create(name)

  def ThenTheReturnedPlayerMapsAllRowFields(self):
    assert self.player.id == 7
    assert self.player.name == 'Alice'
    assert self.player.created_at == datetime(2024, 6, 1, 10, 0, 0)

  def ThenTheSelectUsesLastRowId(self):
    select_call = self.cursor.execute.call_args_list[1]
    assert select_call[0][1] == (7,)

  def ThenInsertWasCalledWithName(self, name):
    insert_call = self.cursor.execute.call_args_list[0]
    assert insert_call[0][1] == (name,)
