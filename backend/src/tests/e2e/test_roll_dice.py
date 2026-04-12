from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player
from tests.e2e.helpers import lobby_game, active_game
from tests.e2e.scorecards import Scorecard


async def test_roll_returns_200(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  game.assert_status(200)


async def test_roll_sets_dice_values(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  game.assert_dice_count(6).assert_dice_have_values()


async def test_roll_marks_kept_dice(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  await game.roll(game.id, player.id, kept_dice=[0, 2])
  game.assert_die_is_kept(0).assert_die_is_kept(2)


async def test_roll_game_not_found(client: AsyncClient, make_token):
  game = await Game(client).roll(999, 1, token=make_token())
  game.assert_status(404).assert_has_detail()


async def test_roll_game_not_active(client: AsyncClient):
  player, game = await lobby_game(client)
  await game.roll(game.id, player.id)
  game.assert_status(409).assert_has_detail()


async def test_roll_not_your_turn(client: AsyncClient, make_token):
  _, game = await active_game(client)
  p2 = await Player(client).create('Bob', token=make_token())
  await game.roll(game.id, p2.id, token=p2.token)
  game.assert_status(403).assert_has_detail()


async def test_roll_no_rolls_remaining(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  await game.roll(game.id, player.id)
  await game.roll(game.id, player.id)
  await game.roll(game.id, player.id)
  game.assert_status(409).assert_has_detail()


async def test_roll_uses_saved_rolls_when_regular_rolls_exhausted(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  await Scorecard(client).score(game.id, player.id, 'chance', token=player.token)
  await game.roll(game.id, player.id)
  await game.roll(game.id, player.id)
  await game.roll(game.id, player.id)
  await game.roll(game.id, player.id)
  game.assert_status(200)
