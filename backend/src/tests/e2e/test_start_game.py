from httpx import AsyncClient
from tests.e2e.players import Player
from tests.e2e.helpers import lobby_game, active_game


async def test_start_game_returns_200(client: AsyncClient):
  player, game = await lobby_game(client)
  await game.start(game.id, player.id)
  game.assert_status(200)


async def test_start_game_status_is_active(client: AsyncClient):
  player, game = await lobby_game(client)
  await game.start(game.id, player.id)
  game.assert_game_status('active')


async def test_start_game_not_found(client: AsyncClient):
  player, game = await lobby_game(client)
  await game.start(999, player.id)
  game.assert_status(404).assert_has_detail()


async def test_start_game_not_creator(client: AsyncClient, make_token):
  _, game = await lobby_game(client)
  p2 = await Player(client).create('Bob', token=make_token())
  await game.join(game.id, p2.id, token=p2.token)
  await game.start(game.id, p2.id, token=p2.token)
  game.assert_status(403).assert_has_detail()


async def test_start_game_already_active(client: AsyncClient):
  player, game = await active_game(client)
  await game.start(game.id, player.id)
  game.assert_status(409).assert_has_detail()
