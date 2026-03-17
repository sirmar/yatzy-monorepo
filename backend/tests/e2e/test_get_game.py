from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_get_game_returns_game(client: AsyncClient):
  player = await Player(client).create('Alice')
  created = await Game(client).create(player.id)
  game = await Game(client).get(created.id)
  game.assert_status(200)
  game.assert_id_positive()
  game.assert_game_status('lobby')
  game.assert_creator_id(player.id)
  game.assert_player_ids_include(player.id)
  game.assert_has_created_at()


async def test_get_game_not_found(client: AsyncClient):
  game = await Game(client).get(999)
  game.assert_status(404)
  game.assert_has_detail()
