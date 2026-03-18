from datetime import datetime
from unittest.mock import AsyncMock
from app.players.player_repository import PlayerRepository
from tests.unit.repository_test_case import RepositoryTestCase


class TestPlayerRepository(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = PlayerRepository(self.conn)

  async def test_create_maps_row_to_player_fields(self):
    self.GivenDatabaseReturnsPlayer(id=7, name='Alice', created_at=datetime(2024, 6, 1, 10, 0, 0))
    await self.WhenPlayerIsCreatedWithName('Alice')
    self.ThenPlayerHasId(7)
    self.ThenPlayerHasName('Alice')
    self.ThenPlayerHasCreatedAt(datetime(2024, 6, 1, 10, 0, 0))

  async def test_create_selects_inserted_row_by_id(self):
    self.GivenDatabaseReturnsPlayer(id=7)
    await self.WhenPlayerIsCreatedWithName('Alice')
    self.ThenSelectQueriesById(7)

  async def test_create_insert_uses_provided_name(self):
    self.GivenDatabaseReturnsPlayer()
    await self.WhenPlayerIsCreatedWithName('Bob')
    self.ThenInsertWasCalledWith('Bob')

  async def test_list_all_returns_players(self):
    self.GivenDatabaseHasPlayers(['Alice', 'Bob'])
    await self.WhenAllPlayersAreListed()
    self.ThenPlayersAreReturned(['Alice', 'Bob'])

  async def test_list_all_filters_deleted(self):
    self.GivenDatabaseHasPlayers(['Alice'])
    await self.WhenAllPlayersAreListed()
    self.ThenQueryFiltersOnDeletedAtColumn()

  async def test_get_by_id_returns_player(self):
    self.GivenDatabaseReturnsPlayer(id=3, name='Alice')
    await self.WhenPlayerIsFetchedById(3)
    self.ThenPlayerHasId(3)
    self.ThenPlayerHasName('Alice')

  async def test_get_by_id_returns_none_when_not_found(self):
    self.GivenDatabaseReturnsNoRow()
    await self.WhenPlayerIsFetchedById(99)
    self.ThenPlayerIsNone()

  async def test_get_by_id_filters_deleted(self):
    self.GivenDatabaseReturnsPlayer()
    await self.WhenPlayerIsFetchedById(3)
    self.ThenQueryFiltersOnDeletedAtColumn()

  async def test_update_returns_updated_player(self):
    self.GivenDatabaseReturnsPlayer(name='Bob')
    await self.WhenPlayerIsUpdated(3, 'Bob')
    self.ThenPlayerHasName('Bob')

  async def test_update_uses_provided_name(self):
    self.GivenDatabaseReturnsPlayer()
    await self.WhenPlayerIsUpdated(3, 'Bob')
    self.ThenUpdateQueryUsesNameAndId('Bob', 3)

  async def test_update_returns_none_when_not_found(self):
    self.GivenDatabaseAffectsRows(0)
    await self.WhenPlayerIsUpdated(99, 'Bob')
    self.ThenPlayerIsNone()

  async def test_update_filters_deleted(self):
    self.GivenDatabaseReturnsPlayer()
    await self.WhenPlayerIsUpdated(3, 'Bob')
    self.ThenQueryFiltersOnDeletedAtColumn()

  async def test_delete_query_uses_player_id(self):
    self.GivenDatabaseAffectsRows(1)
    await self.WhenPlayerIsDeleted(3)
    self.ThenDeleteQueryUsesId(3)

  async def test_delete_returns_true_when_found(self):
    self.GivenDatabaseAffectsRows(1)
    await self.WhenPlayerIsDeleted(3)
    self.ThenPlayerIsTrue()

  async def test_delete_returns_false_when_not_found(self):
    self.GivenDatabaseAffectsRows(0)
    await self.WhenPlayerIsDeleted(99)
    self.ThenDeletedIsFalse()

  async def test_delete_filters_deleted(self):
    self.GivenDatabaseAffectsRows(1)
    await self.WhenPlayerIsDeleted(3)
    self.ThenQueryFiltersOnDeletedAtColumn()

  # Given

  def GivenDatabaseReturnsPlayer(self, id=1, name='Alice', created_at=datetime(2024, 6, 1, 10, 0, 0)):
    self.cursor.lastrowid = id
    self.cursor.fetchone = AsyncMock(return_value=(id, name, created_at))

  def GivenDatabaseHasPlayers(self, names):
    rows = [(i + 1, name, datetime(2024, 6, i + 1, 10, 0, 0)) for i, name in enumerate(names)]
    self.cursor.fetchall = AsyncMock(return_value=rows)

  def GivenDatabaseReturnsNoRow(self):
    self.cursor.fetchone = AsyncMock(return_value=None)

  def GivenDatabaseAffectsRows(self, count):
    self.cursor.rowcount = count

  # When

  async def WhenPlayerIsCreatedWithName(self, name):
    self.player = await self.repo.create(name)

  async def WhenAllPlayersAreListed(self):
    self.players = await self.repo.list_all()

  async def WhenPlayerIsFetchedById(self, id):
    self.player = await self.repo.get_by_id(id)

  async def WhenPlayerIsUpdated(self, id, name):
    self.player = await self.repo.update(id, name)

  async def WhenPlayerIsDeleted(self, id):
    self.player = await self.repo.delete(id)

  # Then

  def ThenPlayerHasId(self, id):
    assert self.player.id == id

  def ThenPlayerHasName(self, name):
    assert self.player.name == name

  def ThenPlayerHasCreatedAt(self, created_at):
    assert self.player.created_at == created_at

  def ThenSelectQueriesById(self, id):
    select_call = self.cursor.execute.call_args_list[1]
    assert select_call[0][1] == (id,)

  def ThenInsertWasCalledWith(self, name):
    insert_call = self.cursor.execute.call_args_list[0]
    assert insert_call[0][1] == (name,)

  def ThenPlayersAreReturned(self, names):
    assert [p.name for p in self.players] == names

  def ThenQueryFiltersOnDeletedAtColumn(self):
    query = self.cursor.execute.call_args_list[0][0][0]
    assert 'deleted_at IS NULL' in query

  def ThenPlayerIsNone(self):
    assert self.player is None

  def ThenPlayerIsTrue(self):
    assert self.player is True

  def ThenUpdateQueryUsesNameAndId(self, name, id):
    update_call = self.cursor.execute.call_args_list[0]
    assert update_call[0][1] == (name, id)

  def ThenDeleteQueryUsesId(self, id):
    delete_call = self.cursor.execute.call_args_list[0]
    assert delete_call[0][1] == (id,)

  def ThenDeletedIsFalse(self):
    assert self.player is False
