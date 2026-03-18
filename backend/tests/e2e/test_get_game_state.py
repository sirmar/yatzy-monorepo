from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_get_state_returns_200(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.state(game.id)
  game.assert_status(200)


async def test_get_state_lobby_game(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.state(game.id)
  game.assert_state_status('lobby')


async def test_get_state_active_game_has_current_player(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.state(game.id)
  game.assert_state_status('active').assert_current_player_id(alice.id)


async def test_get_state_active_game_has_six_dice(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.state(game.id)
  game.assert_dice_count(6)


async def test_get_state_not_found(client: AsyncClient):
  game = await Game(client).state(999)
  game.assert_status(404).assert_has_detail()
