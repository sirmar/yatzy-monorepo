from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from app.player_repository import PlayerRepository


class TestPlayerRepository:
  def setup_method(self):
    self.cursor = AsyncMock()
    self.conn = MagicMock()
    self.conn.cursor = AsyncMock(return_value=self.cursor)
    self.repo = PlayerRepository(self.conn)

  async def test_create_maps_row_to_player_fields(self):
    self.GivenDatabaseReturnsPlayer(7, 'Alice', datetime(2024, 6, 1, 10, 0, 0))
    await self.WhenPlayerIsCreatedWithName('Alice')
    self.ThenPlayerHasId(7)
    self.ThenPlayerHasName('Alice')
    self.ThenPlayerHasCreatedAt(datetime(2024, 6, 1, 10, 0, 0))

  async def test_create_selects_inserted_row_by_id(self):
    self.GivenDatabaseReturnsPlayer(7, 'Alice', datetime(2024, 6, 1, 10, 0, 0))
    await self.WhenPlayerIsCreatedWithName('Alice')
    self.ThenSelectUsesId(7)

  async def test_create_insert_uses_provided_name(self):
    self.GivenDatabaseReturnsPlayer(7, 'Alice', datetime(2024, 6, 1, 10, 0, 0))
    await self.WhenPlayerIsCreatedWithName('Bob')
    self.ThenInsertWasCalledWithName('Bob')

  async def test_list_all_returns_players(self):
    self.GivenDatabaseHasPlayers(['Alice', 'Bob'])
    await self.WhenAllPlayersAreListed()
    self.ThenPlayersAreReturned(['Alice', 'Bob'])

  async def test_list_all_filters_deleted(self):
    self.GivenDatabaseHasPlayers(['Alice'])
    await self.WhenAllPlayersAreListed()
    self.ThenQueryFiltersDeletedAt()

  def GivenDatabaseReturnsPlayer(self, id, name, created_at):
    self.cursor.lastrowid = id
    self.cursor.fetchone = AsyncMock(return_value=(id, name, created_at))

  def GivenDatabaseHasPlayers(self, names):
    rows = [(i + 1, name, datetime(2024, 6, i + 1, 10, 0, 0)) for i, name in enumerate(names)]
    self.cursor.fetchall = AsyncMock(return_value=rows)

  async def WhenPlayerIsCreatedWithName(self, name):
    self.player = await self.repo.create(name)

  async def WhenAllPlayersAreListed(self):
    self.players = await self.repo.list_all()

  def ThenPlayerHasId(self, id):
    assert self.player.id == id

  def ThenPlayerHasName(self, name):
    assert self.player.name == name

  def ThenPlayerHasCreatedAt(self, created_at):
    assert self.player.created_at == created_at

  def ThenSelectUsesId(self, id):
    select_call = self.cursor.execute.call_args_list[1]
    assert select_call[0][1] == (id,)

  def ThenInsertWasCalledWithName(self, name):
    insert_call = self.cursor.execute.call_args_list[0]
    assert insert_call[0][1] == (name,)

  def ThenPlayersAreReturned(self, names):
    assert [p.name for p in self.players] == names

  def ThenQueryFiltersDeletedAt(self):
    query = self.cursor.execute.call_args_list[0][0][0]
    assert 'deleted_at IS NULL' in query
