from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import lobby_game, active_game


async def test_abort_game_returns_200(client: AsyncClient):
  _, game = await active_game(client)
  await game.abort(game.id)
  game.assert_status(200)


async def test_abort_game_status_is_abandoned(client: AsyncClient):
  _, game = await active_game(client)
  await game.abort(game.id)
  game.assert_game_status('abandoned')


async def test_abort_game_not_found(client: AsyncClient, make_token):
  game = await Game(client).abort(999, token=make_token())
  game.assert_status(404).assert_has_detail()


async def test_abort_lobby_game(client: AsyncClient):
  _, game = await lobby_game(client)
  await game.abort(game.id)
  game.assert_status(409).assert_has_detail()


async def test_abort_already_abandoned_game(client: AsyncClient):
  _, game = await active_game(client)
  await game.abort(game.id)
  await game.abort(game.id)
  game.assert_status(409).assert_has_detail()
