from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import lobby_game, active_game


async def test_list_games_empty(client: AsyncClient):
  result = await Game(client).list_all()
  result.assert_status(200).assert_is_empty_list()


async def test_list_games_returns_created_games(client: AsyncClient):
  player, game1 = await lobby_game(client)
  game2 = await Game(client).create(player.id, token=player.token)
  result = await Game(client).list_all()
  result.assert_status(200).assert_ids_include(game1.id, game2.id)


async def test_list_games_filtered_by_lobby(client: AsyncClient):
  _, lobby = await lobby_game(client)
  _, active = await active_game(client)
  result = await Game(client).list_all(status='lobby')
  result.assert_status(200).assert_ids_include(lobby.id).assert_ids_exclude(active.id)


async def test_list_games_filtered_by_active(client: AsyncClient):
  _, lobby = await lobby_game(client)
  _, active = await active_game(client)
  result = await Game(client).list_all(status='active')
  result.assert_status(200).assert_ids_include(active.id).assert_ids_exclude(lobby.id)
