from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player
from tests.e2e.scorecards import Scorecard
from tests.e2e.helpers import active_game, active_game_two_players


async def test_score_returns_200(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  sc = await Scorecard(client).score(game.id, player.id, 'chance')
  sc.assert_status(200)


async def test_score_returns_scorecard_with_all_categories(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  sc = await Scorecard(client).score(game.id, player.id, 'chance')
  sc.assert_status(200).assert_category_count(20)


async def test_score_records_score_for_category(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  sc = await Scorecard(client).score(game.id, player.id, 'chance')
  sc.assert_score_not_null('chance')


async def test_score_game_not_found_returns_404(client: AsyncClient):
  player = await Player(client).create('Alice')
  sc = await Scorecard(client).score(999, player.id, 'chance')
  sc.assert_status(404).assert_has_detail()


async def test_score_player_not_in_game_returns_404(client: AsyncClient):
  _, game = await active_game(client)
  other = await Player(client).create('Bob')
  sc = await Scorecard(client).score(game.id, other.id, 'chance')
  sc.assert_status(404).assert_has_detail()


async def test_score_not_your_turn_returns_403(client: AsyncClient):
  p1, p2, game = await active_game_two_players(client)
  await game.roll(game.id, p1.id)
  sc = await Scorecard(client).score(game.id, p2.id, 'chance')
  sc.assert_status(403).assert_has_detail()


async def test_score_already_scored_category_returns_409(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  await Scorecard(client).score(game.id, player.id, 'chance')
  await game.roll(game.id, player.id)
  sc = await Scorecard(client).score(game.id, player.id, 'chance')
  sc.assert_status(409).assert_has_detail()


async def test_score_advances_turn_to_next_player(client: AsyncClient):
  p1, p2, game = await active_game_two_players(client)
  await game.roll(game.id, p1.id)
  await Scorecard(client).score(game.id, p1.id, 'chance')
  state = await Game(client).state(game.id)
  state.assert_current_player_id(p2.id)


async def test_score_wraps_turn_back_to_first_player(client: AsyncClient):
  p1, p2, game = await active_game_two_players(client)
  await game.roll(game.id, p1.id)
  await Scorecard(client).score(game.id, p1.id, 'chance')
  await game.roll(game.id, p2.id)
  await Scorecard(client).score(game.id, p2.id, 'chance')
  state = await Game(client).state(game.id)
  state.assert_current_player_id(p1.id)
