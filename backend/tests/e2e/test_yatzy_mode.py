from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import active_yatzy_game, active_yatzy_sequential_game, make_token
from tests.e2e.players import Player
from tests.e2e.scorecards import Scorecard
from tests.e2e.scoring_options import ScoringOptions


async def test_create_yatzy_game_returns_mode(client: AsyncClient):
  player = await Player(client).create('Alice', token=make_token())
  game = await Game(client).create(player.id, mode='yatzy', token=player.token)
  game.assert_status(201).assert_mode('yatzy')


async def test_create_yatzy_sequential_game_returns_mode(client: AsyncClient):
  player = await Player(client).create('Alice', token=make_token())
  game = await Game(client).create(player.id, mode='yatzy_sequential', token=player.token)
  game.assert_status(201).assert_mode('yatzy_sequential')


async def test_start_yatzy_game_returns_200(client: AsyncClient):
  player = await Player(client).create('Alice', token=make_token())
  game = await Game(client).create(player.id, mode='yatzy', token=player.token)
  await game.start(game.id, player.id)
  game.assert_status(200)


async def test_yatzy_scorecard_has_15_categories(client: AsyncClient):
  player, game = await active_yatzy_game(client)
  sc = await Scorecard(client).get(game.id, player.id)
  sc.assert_status(200).assert_category_count(15)


async def test_yatzy_scorecard_does_not_include_maxi_yatzy(client: AsyncClient):
  player, game = await active_yatzy_game(client)
  sc = await Scorecard(client).get(game.id, player.id)
  sc.assert_status(200)
  categories = [e['category'] for e in sc.json['entries']]
  assert 'maxi_yatzy' not in categories


async def test_yatzy_scorecard_includes_yatzy(client: AsyncClient):
  player, game = await active_yatzy_game(client)
  sc = await Scorecard(client).get(game.id, player.id)
  sc.assert_status(200)
  categories = [e['category'] for e in sc.json['entries']]
  assert 'yatzy' in categories


async def test_yatzy_game_has_5_dice(client: AsyncClient):
  player, game = await active_yatzy_game(client)
  await game.roll(game.id, player.id)
  state = await game.state(game.id)
  state.assert_status(200)
  assert len(state.json['dice']) == 5


async def test_yatzy_sequential_allows_first_category(client: AsyncClient):
  player, game = await active_yatzy_sequential_game(client)
  await game.roll(game.id, player.id)
  sc = await Scorecard(client).score(game.id, player.id, 'ones', token=player.token)
  sc.assert_status(200)


async def test_yatzy_sequential_rejects_out_of_order_category(client: AsyncClient):
  player, game = await active_yatzy_sequential_game(client)
  await game.roll(game.id, player.id)
  sc = await Scorecard(client).score(game.id, player.id, 'twos', token=player.token)
  sc.assert_status(409).assert_has_detail()


async def test_yatzy_sequential_scoring_options_returns_at_most_one(client: AsyncClient):
  player, game = await active_yatzy_sequential_game(client)
  await game.roll(game.id, player.id)
  opts = await ScoringOptions(client).get(game.id, player.id)
  opts.assert_status(200).assert_count_at_most(1)


async def test_yatzy_scoring_options_excludes_maxi_categories(client: AsyncClient):
  player, game = await active_yatzy_game(client)
  await game.roll(game.id, player.id)
  opts = await ScoringOptions(client).get(game.id, player.id)
  opts.assert_status(200)
  maxi_only = {'three_pairs', 'five_of_a_kind', 'full_straight', 'villa', 'tower', 'maxi_yatzy'}
  returned_categories = {o['category'] for o in opts.json}
  assert returned_categories.isdisjoint(maxi_only)



async def test_yatzy_unused_rolls_are_not_saved(client: AsyncClient):
  player, game = await active_yatzy_game(client)
  await game.roll(game.id, player.id)
  await Scorecard(client).score(game.id, player.id, 'ones', token=player.token)
  state = await game.state(game.id)
  state.assert_status(200)
  assert state.json['saved_rolls'] == 0


YATZY_SEQUENTIAL_CATEGORIES = [
  'ones', 'twos', 'threes', 'fours', 'fives', 'sixes',
  'one_pair', 'two_pairs',
  'three_of_a_kind', 'four_of_a_kind',
  'small_straight', 'large_straight',
  'full_house',
  'chance', 'yatzy',
]


YATZY_CATEGORIES = [
  'ones', 'twos', 'threes', 'fours', 'fives', 'sixes',
  'one_pair', 'two_pairs',
  'three_of_a_kind', 'four_of_a_kind',
  'small_straight', 'large_straight',
  'full_house',
  'chance', 'yatzy',
]


async def test_full_yatzy_game_final_score_matches_scorecard(client: AsyncClient):
  player, game = await active_yatzy_game(client)

  for category in YATZY_CATEGORIES:
    await game.roll(game.id, player.id)
    sc = await Scorecard(client).score(game.id, player.id, category, token=player.token)
    sc.assert_status(200)

  state = await game.state(game.id)
  state.assert_status(200).assert_state_status('finished').assert_has_final_scores()

  sc = await Scorecard(client).get(game.id, player.id)
  sc.assert_all_scored()

  final_total = next(s['total'] for s in state.json['final_scores'] if s['player_id'] == player.id)
  assert final_total == sc.json['total']


async def test_full_yatzy_sequential_game_completes(client: AsyncClient):
  player, game = await active_yatzy_sequential_game(client)

  for category in YATZY_SEQUENTIAL_CATEGORIES:
    await game.roll(game.id, player.id)
    sc = await Scorecard(client).score(game.id, player.id, category, token=player.token)
    sc.assert_status(200)

  state = await game.state(game.id)
  state.assert_status(200).assert_state_status('finished').assert_has_winner_ids().assert_has_final_scores()

  sc = await Scorecard(client).get(game.id, player.id)
  sc.assert_all_scored()

  final_total = next(s['total'] for s in state.json['final_scores'] if s['player_id'] == player.id)
  assert final_total == sc.json['total']
