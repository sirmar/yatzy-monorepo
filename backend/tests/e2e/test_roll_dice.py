from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_roll_returns_200(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.roll(game.id, alice.id)
  game.assert_status(200)


async def test_roll_sets_dice_values(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.roll(game.id, alice.id)
  game.assert_dice_count(6).assert_dice_have_values()


async def test_roll_marks_kept_dice(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.roll(game.id, alice.id)
  await game.roll(game.id, alice.id, kept_dice=[0, 2])
  game.assert_die_is_kept(0).assert_die_is_kept(2)


async def test_roll_game_not_found(client: AsyncClient):
  game = await Game(client).roll(999, 1)
  game.assert_status(404).assert_has_detail()


async def test_roll_game_not_active(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.roll(game.id, alice.id)
  game.assert_status(409).assert_has_detail()


async def test_roll_not_your_turn(client: AsyncClient):
  alice = await Player(client).create('Alice')
  bob = await Player(client).create('Bob')
  game = await Game(client).create(alice.id)
  await game.join(game.id, bob.id)
  await game.start(game.id, alice.id)
  await game.roll(game.id, bob.id)
  game.assert_status(403).assert_has_detail()


async def test_roll_no_rolls_remaining(client: AsyncClient):
  alice = await Player(client).create('Alice')
  game = await Game(client).create(alice.id)
  await game.start(game.id, alice.id)
  await game.roll(game.id, alice.id)
  await game.roll(game.id, alice.id)
  await game.roll(game.id, alice.id)
  await game.roll(game.id, alice.id)
  game.assert_status(409).assert_has_detail()
