from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import lobby_game, active_game


async def test_end_game_returns_200(client: AsyncClient):
  _, game = await active_game(client)
  await game.end(game.id)
  game.assert_status(200)


async def test_end_game_status_is_finished(client: AsyncClient):
  _, game = await active_game(client)
  await game.end(game.id)
  game.assert_game_status('finished')


async def test_end_game_not_found(client: AsyncClient):
  game = await Game(client).end(999)
  game.assert_status(404).assert_has_detail()


async def test_end_lobby_game(client: AsyncClient):
  _, game = await lobby_game(client)
  await game.end(game.id)
  game.assert_status(409).assert_has_detail()


async def test_end_finished_game(client: AsyncClient):
  _, game = await active_game(client)
  await game.end(game.id)
  await game.end(game.id)
  game.assert_status(409).assert_has_detail()
