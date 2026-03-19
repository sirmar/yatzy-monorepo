from app.games.game_player_repository import GamePlayerRepository
from tests.unit.repository_test_case import RepositoryTestCase


class TestGamePlayerRepositoryUpdateRollsRemaining(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = GamePlayerRepository(self.conn)

  async def test_update_rolls_remaining_uses_correct_params(self):
    await self.WhenRollsRemainingUpdated(1, 5, 2)
    self.ThenUpdateWasCalledWith(1, 5, 2)

  async def WhenRollsRemainingUpdated(self, game_id, player_id, value):
    await self.repo.update_rolls_remaining(game_id, player_id, value)

  def ThenUpdateWasCalledWith(self, game_id, player_id, value):
    call = self.cursor.execute.call_args_list[0]
    assert 'UPDATE game_players' in call[0][0]
    assert call[0][1] == (value, game_id, player_id)





class TestGamePlayerRepository(RepositoryTestCase):
  def setup_method(self):
    super().setup_method()
    self.repo = GamePlayerRepository(self.conn)

  async def test_add_uses_game_id_player_id_and_join_order(self):
    await self.WhenPlayerIsAdded(1, 5, 2)
    self.ThenInsertWasCalledWith(1, 5, 2)

  async def WhenPlayerIsAdded(self, game_id, player_id, join_order):
    await self.repo.add(game_id, player_id, join_order)

  def ThenInsertWasCalledWith(self, game_id, player_id, join_order):
    call = self.cursor.execute.call_args_list[0]
    assert call[0][1] == (game_id, player_id, join_order)
