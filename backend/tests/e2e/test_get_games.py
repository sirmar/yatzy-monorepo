from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import lobby_game


async def test_list_games_empty(client: AsyncClient):
  result = await Game(client).list_all()
  result.assert_status(200).assert_is_empty_list()


async def test_list_games_returns_created_games(client: AsyncClient):
  player, game1 = await lobby_game(client)
  game2 = await Game(client).create(player.id)
  result = await Game(client).list_all()
  result.assert_status(200).assert_ids_include(game1.id, game2.id)
