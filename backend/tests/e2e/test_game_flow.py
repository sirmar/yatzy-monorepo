from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_full_game_flow(client: AsyncClient):
  p1 = await Player(client).create('Alice')
  p2 = await Player(client).create('Bob')

  game = await Game(client).create(p1.id)
  game.assert_status(201).assert_game_status('lobby').assert_player_ids_include(p1.id)

  await game.join(game.id, p2.id)
  game.assert_status(200).assert_player_ids_include(p1.id, p2.id)

  await game.start(game.id, p1.id)
  game.assert_status(200).assert_game_status('active')

  state = await Game(client).state(game.id)
  state.assert_status(200).assert_state_status('active').assert_current_player_id(p1.id)

  await game.roll(game.id, p2.id)
  game.assert_status(403)

  await game.roll(game.id, p1.id)
  game.assert_status(200).assert_dice_count(6).assert_dice_have_values()

  first_die_value = game.json['dice'][0]['value']
  await game.roll(game.id, p1.id, kept_dice=[0])
  game.assert_status(200).assert_die_is_kept(0)
  assert game.json['dice'][0]['value'] == first_die_value

  await game.roll(game.id, p1.id)
  game.assert_status(200)

  await game.roll(game.id, p1.id)
  game.assert_status(409)

  await game.end(game.id)
  game.assert_status(200).assert_game_status('finished')

  state = await Game(client).state(game.id)
  state.assert_status(200).assert_state_status('finished')
