from httpx import AsyncClient
from tests.e2e.players import Player
from tests.e2e.scorecards import Scorecard
from tests.e2e.helpers import active_game


async def test_get_scorecard_returns_404_for_unknown_game(client: AsyncClient, make_token):
  player = await Player(client).create('Alice', token=make_token())
  sc = await Scorecard(client).get(999, player.id)
  sc.assert_status(404).assert_has_detail()


async def test_get_scorecard_returns_404_for_player_not_in_game(client: AsyncClient, make_token):
  _, game = await active_game(client)
  other = await Player(client).create('Bob', token=make_token())
  sc = await Scorecard(client).get(game.id, other.id)
  sc.assert_status(404).assert_has_detail()


async def test_get_scorecard_has_twenty_categories(client: AsyncClient):
  player, game = await active_game(client)
  sc = await Scorecard(client).get(game.id, player.id)
  sc.assert_status(200).assert_category_count(20)


async def test_get_scorecard_all_scores_null_initially(client: AsyncClient):
  player, game = await active_game(client)
  sc = await Scorecard(client).get(game.id, player.id)
  sc.assert_status(200).assert_all_scores_null()


async def test_get_scorecard_bonus_null_initially(client: AsyncClient):
  player, game = await active_game(client)
  sc = await Scorecard(client).get(game.id, player.id)
  sc.assert_status(200).assert_bonus_null()


async def test_get_scorecard_total_zero_initially(client: AsyncClient):
  player, game = await active_game(client)
  sc = await Scorecard(client).get(game.id, player.id)
  sc.assert_status(200).assert_total(0)
