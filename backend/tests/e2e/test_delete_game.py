from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_delete_lobby_game_returns_204(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.delete(game.id)
  game.assert_status(204)


async def test_delete_finished_game_returns_204(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.end(game.id)
  await game.delete(game.id)
  game.assert_status(204)


async def test_delete_game_not_found(client: AsyncClient):
  game = await Game(client).delete(999)
  game.assert_status(404).assert_has_detail()


async def test_delete_active_game(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.delete(game.id)
  game.assert_status(409).assert_has_detail()


async def test_deleted_game_not_returned_by_get(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  game_id = game.id
  await game.delete(game_id)
  await game.get(game_id)
  game.assert_status(404)
