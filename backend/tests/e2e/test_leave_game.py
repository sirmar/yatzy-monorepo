from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player
from tests.e2e.helpers import lobby_game, active_game


async def test_leave_game_returns_200(client: AsyncClient):
  p1, game = await lobby_game(client)
  p2 = await Player(client).create('Bob')
  await game.join(game.id, p2.id)
  await game.leave(game.id, p2.id)
  game.assert_status(200)


async def test_leave_game_removes_player(client: AsyncClient):
  p1, game = await lobby_game(client)
  p2 = await Player(client).create('Bob')
  await game.join(game.id, p2.id)
  await game.leave(game.id, p2.id)
  await game.get(game.id)
  assert p2.id not in game.json['player_ids']


async def test_leave_game_not_found(client: AsyncClient):
  p1, _ = await lobby_game(client)
  game = Game(client)
  await game.leave(999, p1.id)
  game.assert_status(404).assert_has_detail()


async def test_leave_game_player_not_in_game(client: AsyncClient):
  _, game = await lobby_game(client)
  p2 = await Player(client).create('Bob')
  await game.leave(game.id, p2.id)
  game.assert_status(404).assert_has_detail()


async def test_leave_active_game(client: AsyncClient):
  p1, game = await active_game(client)
  await game.leave(game.id, p1.id)
  game.assert_status(409).assert_has_detail()


async def test_creator_cannot_leave(client: AsyncClient):
  p1, game = await lobby_game(client)
  await game.leave(game.id, p1.id)
  game.assert_status(403).assert_has_detail()
