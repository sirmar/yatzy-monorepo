from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import lobby_game, active_game


async def test_get_state_returns_200(client: AsyncClient):
  _, game = await lobby_game(client)
  await game.state(game.id)
  game.assert_status(200)


async def test_get_state_lobby_game(client: AsyncClient):
  _, game = await lobby_game(client)
  await game.state(game.id)
  game.assert_state_status('lobby')


async def test_get_state_active_game_has_current_player(client: AsyncClient):
  player, game = await active_game(client)
  await game.state(game.id)
  game.assert_state_status('active').assert_current_player_id(player.id)


async def test_get_state_active_game_has_six_dice(client: AsyncClient):
  _, game = await active_game(client)
  await game.state(game.id)
  game.assert_dice_count(6)


async def test_get_state_not_found(client: AsyncClient):
  game = await Game(client).state(999)
  game.assert_status(404).assert_has_detail()
