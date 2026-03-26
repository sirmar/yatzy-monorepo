from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import lobby_game


async def test_create_game_returns_201(client: AsyncClient):
  _, game = await lobby_game(client)
  game.assert_status(201)


async def test_create_game_returns_id(client: AsyncClient):
  _, game = await lobby_game(client)
  game.assert_id_positive()


async def test_create_game_status_is_lobby(client: AsyncClient):
  _, game = await lobby_game(client)
  game.assert_game_status('lobby')


async def test_create_game_sets_creator(client: AsyncClient):
  player, game = await lobby_game(client)
  game.assert_creator_id(player.id)


async def test_create_game_adds_creator_to_players(client: AsyncClient):
  player, game = await lobby_game(client)
  game.assert_player_ids_include(player.id)


async def test_create_game_has_created_at(client: AsyncClient):
  _, game = await lobby_game(client)
  game.assert_has_created_at()


async def test_create_game_missing_creator_returns_422(client: AsyncClient, make_token):
  game = await Game(client).create(token=make_token())
  game.assert_status(422).assert_has_detail()
