from datetime import datetime
from unittest.mock import AsyncMock
from app.game_repository import GameRepository
from tests.unit.repository_test_case import RepositoryTestCase


class TestGameRepository(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.cursor.lastrowid = 1
    self.repo = GameRepository(self.conn)

  # create

  async def test_create_maps_row_to_game_fields(self):
    self.GivenDatabaseReturnsGame(id=1, creator_id=5)
    self.GivenDatabaseReturnsPlayerIds()
    await self.WhenGameIsCreated(5)
    self.ThenGameHasId(1)
    self.ThenGameHasStatus('lobby')
    self.ThenGameHasCreatorId(5)

  async def test_create_uses_creator_id_in_insert(self):
    self.GivenDatabaseReturnsGame()
    self.GivenDatabaseReturnsPlayerIds()
    await self.WhenGameIsCreated(5)
    self.ThenInsertWasCalledWithCreatorId(5)

  async def test_create_adds_creator_to_player_ids(self):
    self.GivenDatabaseReturnsGame()
    self.GivenDatabaseReturnsPlayerIds(player_ids=[5])
    await self.WhenGameIsCreated(5)
    self.ThenGamePlayerIdsInclude(5)

  async def test_create_game_select_filters_deleted(self):
    self.GivenDatabaseReturnsGame()
    self.GivenDatabaseReturnsPlayerIds()
    await self.WhenGameIsCreated(5)
    self.ThenGameSelectFiltersOnDeletedAt()

  async def test_create_game_players_select_filters_deleted(self):
    self.GivenDatabaseReturnsGame()
    self.GivenDatabaseReturnsPlayerIds()
    await self.WhenGameIsCreated(5)
    self.ThenGamePlayersSelectFiltersOnDeletedAt()

  async def test_create_maps_started_at_and_ended_at(self):
    self.GivenDatabaseReturnsGame()
    self.GivenDatabaseReturnsPlayerIds()
    await self.WhenGameIsCreated(5)
    self.ThenGameStartedAtIsNone()
    self.ThenGameEndedAtIsNone()

  # end

  async def test_end_returns_game_with_finished_status(self):
    self.GivenDatabaseReturnsGame(status='finished')
    self.GivenDatabaseReturnsPlayerIds()
    self.GivenDatabaseAffectsRows(1)
    await self.WhenGameIsEnded(1)
    self.ThenGameHasStatus('finished')

  async def test_end_returns_none_when_not_found_or_not_active(self):
    self.GivenDatabaseAffectsRows(0)
    await self.WhenGameIsEnded(99)
    self.ThenGameIsNone()

  async def test_end_only_updates_active_games(self):
    self.GivenDatabaseReturnsGame()
    self.GivenDatabaseReturnsPlayerIds()
    self.GivenDatabaseAffectsRows(1)
    await self.WhenGameIsEnded(1)
    self.ThenEndUpdateFilteredOnActiveStatus()

  # start

  async def test_start_returns_game_with_active_status(self):
    self.GivenDatabaseReturnsGame(status='active')
    self.GivenDatabaseReturnsPlayerIds()
    self.GivenDatabaseAffectsRows(1)
    await self.WhenGameIsStarted(1, 7)
    self.ThenGameHasStatus('active')

  async def test_start_uses_turn_id_and_game_id_in_update(self):
    self.GivenDatabaseReturnsGame()
    self.GivenDatabaseReturnsPlayerIds()
    self.GivenDatabaseAffectsRows(1)
    await self.WhenGameIsStarted(1, 7)
    self.ThenStartUpdateUsedTurnIdAndGameId(7, 1)

  async def test_start_returns_none_when_not_found(self):
    self.GivenDatabaseAffectsRows(0)
    await self.WhenGameIsStarted(99, 7)
    self.ThenGameIsNone()

  # get_by_id

  async def test_get_by_id_returns_game(self):
    self.GivenDatabaseReturnsGame(id=1)
    self.GivenDatabaseReturnsPlayerIds()
    await self.WhenGameIsFetchedById(1)
    self.ThenGameHasId(1)
    self.ThenGameHasStatus('lobby')

  async def test_get_by_id_returns_none_when_not_found(self):
    self.GivenDatabaseReturnsNoRow()
    await self.WhenGameIsFetchedById(99)
    self.ThenGameIsNone()

  async def test_get_by_id_filters_deleted(self):
    self.GivenDatabaseReturnsGame()
    self.GivenDatabaseReturnsPlayerIds()
    await self.WhenGameIsFetchedById(1)
    self.ThenGetByIdQueryFiltersOnDeletedAt()

  # list_all

  async def test_list_all_returns_games(self):
    self.GivenDatabaseHasGamesWithPlayers([(1, 'lobby', 5, [5]), (2, 'lobby', 5, [5])])
    await self.WhenAllGamesAreListed()
    self.ThenGamesAreReturned([1, 2])

  async def test_list_all_filters_deleted(self):
    self.GivenDatabaseHasGamesWithPlayers([(1, 'lobby', 5, [5])])
    await self.WhenAllGamesAreListed()
    self.ThenListQueryFiltersOnDeletedAt()

  async def test_list_all_returns_empty_list(self):
    self.GivenDatabaseHasGamesWithPlayers([])
    await self.WhenAllGamesAreListed()
    self.ThenGamesAreReturned([])

  async def test_soft_delete_returns_true_when_deleted(self):
    self.GivenDatabaseAffectsRows(1)
    await self.WhenGameIsDeleted(1)
    self.ThenDeletedIsTrue()

  async def test_soft_delete_returns_false_when_not_found(self):
    self.GivenDatabaseAffectsRows(0)
    await self.WhenGameIsDeleted(99)
    self.ThenDeletedIsFalse()

  async def test_soft_delete_filters_on_lobby_or_finished(self):
    self.GivenDatabaseAffectsRows(1)
    await self.WhenGameIsDeleted(1)
    self.ThenDeleteQueryFiltersOnLobbeyOrFinished()

  async def test_soft_delete_uses_game_id(self):
    self.GivenDatabaseAffectsRows(1)
    await self.WhenGameIsDeleted(1)
    self.ThenDeleteQueryUsesGameId(1)

  # Given

  def GivenDatabaseReturnsGame(self, id=1, status='lobby', creator_id=5, created_at=datetime(2024, 6, 1), started_at=None, ended_at=None):
    self.cursor.lastrowid = id
    self.cursor.fetchone = AsyncMock(return_value=(id, status, creator_id, created_at, started_at, ended_at))

  def GivenDatabaseReturnsPlayerIds(self, player_ids=None):
    ids = player_ids if player_ids is not None else [5]
    self.cursor.fetchall = AsyncMock(return_value=[(pid,) for pid in ids])

  def GivenDatabaseReturnsNoRow(self):
    self.cursor.fetchone = AsyncMock(return_value=None)

  def GivenDatabaseAffectsRows(self, count):
    self.cursor.rowcount = count

  def GivenDatabaseHasGamesWithPlayers(self, games_with_players):
    game_rows = [
      (id, status, creator_id, datetime(2024, 6, 1), None, None)
      for id, status, creator_id, _ in games_with_players
    ]
    player_rows_list = [[(pid,) for pid in pids] for _, _, _, pids in games_with_players]
    self.cursor.fetchall = AsyncMock(side_effect=[game_rows] + player_rows_list)

  # When

  async def WhenGameIsCreated(self, creator_id):
    self.game = await self.repo.create(creator_id)

  async def WhenGameIsEnded(self, game_id):
    self.game = await self.repo.end(game_id)

  async def WhenGameIsStarted(self, game_id, turn_id):
    self.game = await self.repo.start(game_id, turn_id)

  async def WhenGameIsFetchedById(self, game_id):
    self.game = await self.repo.get_by_id(game_id)

  async def WhenAllGamesAreListed(self):
    self.games = await self.repo.list_all()

  async def WhenGameIsDeleted(self, game_id):
    self.deleted = await self.repo.soft_delete(game_id)

  # Then

  def ThenGameHasId(self, id):
    assert self.game.id == id

  def ThenGameHasStatus(self, status):
    assert self.game.status == status

  def ThenGameHasCreatorId(self, creator_id):
    assert self.game.creator_id == creator_id

  def ThenGamePlayerIdsInclude(self, player_id):
    assert player_id in self.game.player_ids

  def ThenGameIsNone(self):
    assert self.game is None

  def ThenGamesAreReturned(self, ids):
    assert [g.id for g in self.games] == ids

  def ThenInsertWasCalledWithCreatorId(self, creator_id):
    insert_call = self.cursor.execute.call_args_list[0]
    assert creator_id in insert_call[0][1]

  def ThenGameSelectFiltersOnDeletedAt(self):
    select_call = self.cursor.execute.call_args_list[2]
    assert 'deleted_at IS NULL' in select_call[0][0]

  def ThenGamePlayersSelectFiltersOnDeletedAt(self):
    select_call = self.cursor.execute.call_args_list[3]
    assert 'deleted_at IS NULL' in select_call[0][0]

  def ThenGetByIdQueryFiltersOnDeletedAt(self):
    select_call = self.cursor.execute.call_args_list[0]
    assert 'deleted_at IS NULL' in select_call[0][0]

  def ThenListQueryFiltersOnDeletedAt(self):
    list_call = self.cursor.execute.call_args_list[0]
    assert 'deleted_at IS NULL' in list_call[0][0]

  def ThenEndUpdateFilteredOnActiveStatus(self):
    update_call = self.cursor.execute.call_args_list[0]
    assert 'status = \'active\'' in update_call[0][0]

  def ThenStartUpdateUsedTurnIdAndGameId(self, turn_id, game_id):
    update_call = self.cursor.execute.call_args_list[0]
    assert update_call[0][1] == (turn_id, game_id)

  def ThenGameStartedAtIsNone(self):
    assert self.game.started_at is None

  def ThenGameEndedAtIsNone(self):
    assert self.game.ended_at is None

  def ThenDeletedIsTrue(self):
    assert self.deleted is True

  def ThenDeletedIsFalse(self):
    assert self.deleted is False

  def ThenDeleteQueryFiltersOnLobbeyOrFinished(self):
    delete_call = self.cursor.execute.call_args_list[0]
    assert 'status IN' in delete_call[0][0]

  def ThenDeleteQueryUsesGameId(self, game_id):
    delete_call = self.cursor.execute.call_args_list[0]
    assert delete_call[0][1] == (game_id,)
