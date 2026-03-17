from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_join_game_returns_200(client: AsyncClient):
  alice = await Player(client).create('Alice')
  bob = await Player(client).create('Bob')
  game = await Game(client).create(alice.id)
  await game.join(game.id, bob.id)
  game.assert_status(200)


async def test_join_game_adds_player(client: AsyncClient):
  alice = await Player(client).create('Alice')
  bob = await Player(client).create('Bob')
  game = await Game(client).create(alice.id)
  await game.join(game.id, bob.id)
  game.assert_player_ids_include(bob.id)


async def test_join_game_not_found(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).join(999, alice.id)
  game.assert_status(404).assert_has_detail()


async def test_join_game_already_joined(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.join(game.id, alice.id)
  game.assert_status(409).assert_has_detail()


async def test_join_non_lobby_game(client: AsyncClient):
  alice = await Player(client).create('Alice')
  bob = await Player(client).create('Bob')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.join(game.id, bob.id)
  game.assert_status(409).assert_has_detail()


async def test_join_game_full(client: AsyncClient):
  players = [await Player(client).create(f'Player{i}') for i in range(7)]
  game = await Game(client).create(players[0].id)
  for player in players[1:6]:
    await game.join(game.id, player.id)
  await game.join(game.id, players[6].id)
  game.assert_status(409).assert_has_detail()
