from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import lobby_game


async def test_get_game_returns_game(client: AsyncClient):
  player, game = await lobby_game(client)
  await game.get(game.id)
  (
    game.assert_status(200)
    .assert_id_positive()
    .assert_game_status('lobby')
    .assert_creator_id(player.id)
    .assert_player_ids_include(player.id)
    .assert_has_created_at()
  )


async def test_get_game_not_found(client: AsyncClient):
  game = await Game(client).get(999)
  game.assert_status(404).assert_has_detail()
