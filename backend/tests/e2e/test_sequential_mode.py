from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import active_sequential_game, make_token
from tests.e2e.players import Player
from tests.e2e.scorecards import Scorecard
from tests.e2e.scoring_options import ScoringOptions


async def test_start_sequential_game_returns_200(client: AsyncClient):
  player = await Player(client).create('Alice', token=make_token())
  game = await Game(client).create(player.id, mode='sequential', token=player.token)
  await game.start(game.id, player.id)
  game.assert_status(200)


async def test_start_sequential_game_returns_sequential_mode(client: AsyncClient):
  player = await Player(client).create('Alice', token=make_token())
  game = await Game(client).create(player.id, mode='sequential', token=player.token)
  await game.start(game.id, player.id)
  game.assert_status(200).assert_mode('sequential')


async def test_create_sequential_game_returns_mode(client: AsyncClient):
  player = await Player(client).create('Alice', token=make_token())
  game = await Game(client).create(player.id, mode='sequential', token=player.token)
  game.assert_status(201).assert_mode('sequential')


async def test_create_standard_game_returns_mode(client: AsyncClient):
  player = await Player(client).create('Alice', token=make_token())
  game = await Game(client).create(player.id, token=player.token)
  game.assert_status(201).assert_mode('standard')


async def test_get_sequential_game_includes_mode(client: AsyncClient):
  player = await Player(client).create('Alice', token=make_token())
  created = await Game(client).create(player.id, mode='sequential', token=player.token)
  fetched = await Game(client).get(created.id)
  fetched.assert_status(200).assert_mode('sequential')


async def test_game_state_includes_mode(client: AsyncClient):
  player, game = await active_sequential_game(client)
  state = await game.state(game.id)
  state.assert_status(200)
  assert state.json['mode'] == 'sequential'


async def test_sequential_allows_first_category(client: AsyncClient):
  player, game = await active_sequential_game(client)
  await game.roll(game.id, player.id)
  sc = await Scorecard(client).score(game.id, player.id, 'ones', token=player.token)
  sc.assert_status(200)


async def test_sequential_rejects_out_of_order_category(client: AsyncClient):
  player, game = await active_sequential_game(client)
  await game.roll(game.id, player.id)
  sc = await Scorecard(client).score(game.id, player.id, 'twos', token=player.token)
  sc.assert_status(409).assert_has_detail()


async def test_sequential_allows_second_category_after_first(client: AsyncClient):
  player, game = await active_sequential_game(client)
  await game.roll(game.id, player.id)
  await Scorecard(client).score(game.id, player.id, 'ones', token=player.token)
  await game.roll(game.id, player.id)
  sc = await Scorecard(client).score(game.id, player.id, 'twos', token=player.token)
  sc.assert_status(200)


async def test_sequential_rejects_skipping_mid_game(client: AsyncClient):
  player, game = await active_sequential_game(client)
  await game.roll(game.id, player.id)
  await Scorecard(client).score(game.id, player.id, 'ones', token=player.token)
  await game.roll(game.id, player.id)
  sc = await Scorecard(client).score(game.id, player.id, 'threes', token=player.token)
  sc.assert_status(409).assert_has_detail()


async def test_scoring_options_returns_at_most_one_in_sequential(client: AsyncClient):
  player, game = await active_sequential_game(client)
  await game.roll(game.id, player.id)
  opts = await ScoringOptions(client).get(game.id, player.id)
  opts.assert_status(200).assert_count_at_most(1)


async def test_scoring_options_only_shows_next_category_in_sequential(client: AsyncClient):
  player, game = await active_sequential_game(client)
  await game.roll(game.id, player.id)
  await Scorecard(client).score(game.id, player.id, 'ones', token=player.token)
  await game.roll(game.id, player.id)
  opts = await ScoringOptions(client).get(game.id, player.id)
  opts.assert_status(200).assert_count_at_most(1).assert_only_category('twos')


SEQUENTIAL_CATEGORIES = [
  'ones', 'twos', 'threes', 'fours', 'fives', 'sixes',
  'one_pair', 'two_pairs', 'three_pairs',
  'three_of_a_kind', 'four_of_a_kind', 'five_of_a_kind',
  'small_straight', 'large_straight', 'full_straight',
  'full_house', 'villa', 'tower',
  'chance', 'maxi_yatzy',
]


async def test_full_sequential_game_completes(client: AsyncClient):
  player, game = await active_sequential_game(client)

  for category in SEQUENTIAL_CATEGORIES:
    await game.roll(game.id, player.id)
    sc = await Scorecard(client).score(game.id, player.id, category, token=player.token)
    sc.assert_status(200)

  state = await game.state(game.id)
  state.assert_status(200).assert_state_status('finished').assert_has_winner_ids().assert_has_final_scores()

  sc = await Scorecard(client).get(game.id, player.id)
  sc.assert_all_scored()
