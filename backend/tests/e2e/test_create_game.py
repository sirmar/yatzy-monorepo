from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_create_game_returns_201(client: AsyncClient):
  player = await Player(client).create('Alice')
  game = await Game(client).create(player.id)
  game.assert_status(201)


async def test_create_game_returns_id(client: AsyncClient):
  player = await Player(client).create('Alice')
  game = await Game(client).create(player.id)
  game.assert_id_positive()


async def test_create_game_status_is_lobby(client: AsyncClient):
  player = await Player(client).create('Alice')
  game = await Game(client).create(player.id)
  game.assert_game_status('lobby')


async def test_create_game_sets_creator(client: AsyncClient):
  player = await Player(client).create('Alice')
  game = await Game(client).create(player.id)
  game.assert_creator_id(player.id)


async def test_create_game_adds_creator_to_players(client: AsyncClient):
  player = await Player(client).create('Alice')
  game = await Game(client).create(player.id)
  game.assert_player_ids_include(player.id)


async def test_create_game_has_created_at(client: AsyncClient):
  player = await Player(client).create('Alice')
  game = await Game(client).create(player.id)
  game.assert_has_created_at()


async def test_create_game_missing_creator_returns_422(client: AsyncClient):
  game = await Game(client).create()
  game.assert_status(422)
  game.assert_has_detail()
