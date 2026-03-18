from app.game_player_repository import GamePlayerRepository
from tests.unit.repository_test_case import RepositoryTestCase


class TestGamePlayerRepository(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = GamePlayerRepository(self.conn)

  # add

  async def test_add_uses_game_id_player_id_and_join_order(self):
    await self.WhenPlayerIsAdded(1, 5, 2)
    self.ThenInsertWasCalledWith(1, 5, 2)

  # Given

  # When

  async def WhenPlayerIsAdded(self, game_id, player_id, join_order):
    await self.repo.add(game_id, player_id, join_order)

  # Then

  def ThenInsertWasCalledWith(self, game_id, player_id, join_order):
    call = self.cursor.execute.call_args_list[0]
    assert call[0][1] == (game_id, player_id, join_order)
