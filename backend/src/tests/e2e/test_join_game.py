from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player
from tests.e2e.helpers import lobby_game, active_game


async def test_join_game_returns_200(client: AsyncClient, make_token):
  _, game = await lobby_game(client)
  p2 = await Player(client).create('Bob', token=make_token())
  await game.join(game.id, p2.id, token=p2.token)
  game.assert_status(200)


async def test_join_game_adds_player(client: AsyncClient, make_token):
  _, game = await lobby_game(client)
  p2 = await Player(client).create('Bob', token=make_token())
  await game.join(game.id, p2.id, token=p2.token)
  game.assert_player_ids_include(p2.id)


async def test_join_game_not_found(client: AsyncClient):
  p1, game = await lobby_game(client)
  await game.join(999, p1.id)
  game.assert_status(404).assert_has_detail()


async def test_join_game_already_joined(client: AsyncClient):
  p1, game = await lobby_game(client)
  await game.join(game.id, p1.id)
  game.assert_status(409).assert_has_detail()


async def test_join_non_lobby_game(client: AsyncClient, make_token):
  _, game = await active_game(client)
  p2 = await Player(client).create('Bob', token=make_token())
  await game.join(game.id, p2.id, token=p2.token)
  game.assert_status(409).assert_has_detail()


async def test_join_game_full(client: AsyncClient, make_token):
  players = [
    await Player(client).create(f'Player{i}', token=make_token()) for i in range(7)
  ]
  game = await Game(client).create(players[0].id, token=players[0].token)
  for player in players[1:6]:
    await game.join(game.id, player.id, token=player.token)
  await game.join(game.id, players[6].id, token=players[6].token)
  game.assert_status(409).assert_has_detail()
