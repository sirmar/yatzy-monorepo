from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_start_game_returns_200(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  game.assert_status(200)


async def test_start_game_status_is_active(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  game.assert_game_status('active')


async def test_start_game_not_found(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).start(999, alice.id)
  game.assert_status(404).assert_has_detail()


async def test_start_game_not_creator(client: AsyncClient):
  alice = await Player(client).create('Alice')
  bob = await Player(client).create('Bob')
  game = await Game(client).create(alice.id)
  await game.join(game.id, bob.id)
  await game.start(game.id, bob.id)
  game.assert_status(403).assert_has_detail()


async def test_start_game_already_active(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.start(game.id, alice.id)
  game.assert_status(409).assert_has_detail()
