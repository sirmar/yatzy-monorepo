from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player
from tests.e2e.scorecards import Scorecard
from tests.e2e.helpers import active_game_two_players, play_turn


async def test_full_game_flow(client: AsyncClient, make_token):
  t1, t2 = make_token(), make_token()
  p1 = await Player(client).create('Alice', token=t1)
  p2 = await Player(client).create('Bob', token=t2)

  game = await Game(client).create(p1.id, token=t1)
  game.assert_status(201).assert_game_status('lobby').assert_player_ids_include(p1.id)

  await game.join(game.id, p2.id, token=t2)
  game.assert_status(200).assert_player_ids_include(p1.id, p2.id)

  await game.start(game.id, p1.id)
  game.assert_status(200).assert_game_status('active')

  state = await Game(client).state(game.id)
  state.assert_status(200).assert_state_status('active').assert_current_player_id(p1.id)

  await game.roll(game.id, p2.id, token=t2)
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

  await game.abort(game.id)
  game.assert_status(200).assert_game_status('abandoned')

  state = await Game(client).state(game.id)
  state.assert_status(200).assert_state_status('abandoned')


async def test_full_game_completes(client: AsyncClient):
  p1, p2, game = await active_game_two_players(client)

  for _ in range(20):
    await play_turn(client, game, game.id, p1.id, p1.token)
    await play_turn(client, game, game.id, p2.id, p2.token)

  state = await Game(client).state(game.id)
  state.assert_state_status(
    'finished'
  ).assert_has_winner_ids().assert_has_final_scores()

  for player in [p1, p2]:
    sc = await Scorecard(client).get(game.id, player.id)
    sc.assert_all_scored().assert_total_positive()
