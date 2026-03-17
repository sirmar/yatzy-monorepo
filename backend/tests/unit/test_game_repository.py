from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from app.game_repository import GameRepository


class TestGameRepository:
  def setup_method(self):
    self.cursor = AsyncMock()
    self.cursor.lastrowid = 1
    self.conn = MagicMock()
    self.conn.cursor = AsyncMock(return_value=self.cursor)
    self.repo = GameRepository(self.conn)

  # create

  async def test_create_maps_row_to_game_fields(self):
    self.GivenDatabaseReturnsGame(1, 'lobby', 5, datetime(2024, 6, 1))
    self.GivenDatabaseReturnsPlayerIds([5])
    await self.WhenGameIsCreated(5)
    self.ThenGameHasId(1)
    self.ThenGameHasStatus('lobby')
    self.ThenGameHasCreatorId(5)

  async def test_create_uses_creator_id_in_insert(self):
    self.GivenDatabaseReturnsGame(1, 'lobby', 5, datetime(2024, 6, 1))
    self.GivenDatabaseReturnsPlayerIds([5])
    await self.WhenGameIsCreated(5)
    self.ThenInsertWasCalledWithCreatorId(5)

  async def test_create_adds_creator_to_player_ids(self):
    self.GivenDatabaseReturnsGame(1, 'lobby', 5, datetime(2024, 6, 1))
    self.GivenDatabaseReturnsPlayerIds([5])
    await self.WhenGameIsCreated(5)
    self.ThenGamePlayerIdsInclude(5)

  async def test_create_game_select_filters_deleted(self):
    self.GivenDatabaseReturnsGame(1, 'lobby', 5, datetime(2024, 6, 1))
    self.GivenDatabaseReturnsPlayerIds([5])
    await self.WhenGameIsCreated(5)
    self.ThenGameSelectFiltersOnDeletedAt()

  async def test_create_game_players_select_filters_deleted(self):
    self.GivenDatabaseReturnsGame(1, 'lobby', 5, datetime(2024, 6, 1))
    self.GivenDatabaseReturnsPlayerIds([5])
    await self.WhenGameIsCreated(5)
    self.ThenGamePlayersSelectFiltersOnDeletedAt()

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

  async def test_create_maps_started_at_and_ended_at(self):
    self.GivenDatabaseReturnsGame(1, 'lobby', 5, datetime(2024, 6, 1), None, None)
    self.GivenDatabaseReturnsPlayerIds([5])
    await self.WhenGameIsCreated(5)
    self.ThenGameStartedAtIsNone()
    self.ThenGameEndedAtIsNone()

  # Given

  def GivenDatabaseReturnsGame(self, id, status, creator_id, created_at, started_at=None, ended_at=None):
    self.cursor.lastrowid = id
    self.cursor.fetchone = AsyncMock(return_value=(id, status, creator_id, created_at, started_at, ended_at))

  def GivenDatabaseReturnsPlayerIds(self, player_ids):
    self.cursor.fetchall = AsyncMock(return_value=[(pid,) for pid in player_ids])

  # When

  async def WhenGameIsCreated(self, creator_id):
    self.game = await self.repo.create(creator_id)

  # Then

  def ThenGameHasId(self, id):
    assert self.game.id == id

  def ThenGameHasStatus(self, status):
    assert self.game.status == status

  def ThenGameHasCreatorId(self, creator_id):
    assert self.game.creator_id == creator_id

  def ThenGamePlayerIdsInclude(self, player_id):
    assert player_id in self.game.player_ids

  async def WhenAllGamesAreListed(self):
    self.games = await self.repo.list_all()

  def ThenGamesAreReturned(self, ids):
    assert [g.id for g in self.games] == ids

  def ThenListQueryFiltersOnDeletedAt(self):
    list_call = self.cursor.execute.call_args_list[0]
    assert 'deleted_at IS NULL' in list_call[0][0]

  def GivenDatabaseHasGamesWithPlayers(self, games_with_players):
    game_rows = [
      (id, status, creator_id, datetime(2024, 6, 1), None, None)
      for id, status, creator_id, _ in games_with_players
    ]
    player_rows_list = [[(pid,) for pid in pids] for _, _, _, pids in games_with_players]
    self.cursor.fetchall = AsyncMock(side_effect=[game_rows] + player_rows_list)

  def ThenInsertWasCalledWithCreatorId(self, creator_id):
    insert_call = self.cursor.execute.call_args_list[0]
    assert creator_id in insert_call[0][1]

  def ThenGameSelectFiltersOnDeletedAt(self):
    select_call = self.cursor.execute.call_args_list[2]
    assert 'deleted_at IS NULL' in select_call[0][0]

  def ThenGamePlayersSelectFiltersOnDeletedAt(self):
    select_call = self.cursor.execute.call_args_list[3]
    assert 'deleted_at IS NULL' in select_call[0][0]

  def ThenGameStartedAtIsNone(self):
    assert self.game.started_at is None

  def ThenGameEndedAtIsNone(self):
    assert self.game.ended_at is None
