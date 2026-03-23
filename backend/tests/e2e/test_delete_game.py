from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import lobby_game, active_game, abandoned_game


async def test_delete_lobby_game_returns_204(client: AsyncClient):
  _, game = await lobby_game(client)
  await game.delete(game.id)
  game.assert_status(204)


async def test_delete_abandoned_game_returns_204(client: AsyncClient):
  _, game = await abandoned_game(client)
  await game.delete(game.id)
  game.assert_status(204)


async def test_delete_game_not_found(client: AsyncClient):
  game = await Game(client).delete(999)
  game.assert_status(404).assert_has_detail()


async def test_delete_active_game(client: AsyncClient):
  _, game = await active_game(client)
  await game.delete(game.id)
  game.assert_status(409).assert_has_detail()


async def test_deleted_game_not_returned_by_get(client: AsyncClient):
  _, game = await lobby_game(client)
  game_id = game.id
  await game.delete(game_id)
  await game.get(game_id)
  game.assert_status(404)
