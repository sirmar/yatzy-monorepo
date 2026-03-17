from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_get_game_returns_game(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.get(game.id)
  (game
    .assert_status(200)
    .assert_id_positive()
    .assert_game_status('lobby')
    .assert_creator_id(alice.id)
    .assert_player_ids_include(alice.id)
    .assert_has_created_at())


async def test_get_game_not_found(client: AsyncClient):
  game = await Game(client).get(999)
  game.assert_status(404).assert_has_detail()
