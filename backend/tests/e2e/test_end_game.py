from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_end_game_returns_200(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.end(game.id)
  game.assert_status(200)


async def test_end_game_status_is_finished(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.end(game.id)
  game.assert_game_status('finished')


async def test_end_game_not_found(client: AsyncClient):
  game = await Game(client).end(999)
  game.assert_status(404).assert_has_detail()


async def test_end_lobby_game(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.end(game.id)
  game.assert_status(409).assert_has_detail()


async def test_end_finished_game(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.end(game.id)
  await game.end(game.id)
  game.assert_status(409).assert_has_detail()
