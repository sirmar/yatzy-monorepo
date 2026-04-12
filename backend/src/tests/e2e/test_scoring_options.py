from httpx import AsyncClient
from tests.e2e.players import Player
from tests.e2e.scorecards import Scorecard
from tests.e2e.scoring_options import ScoringOptions
from tests.e2e.helpers import active_game, active_game_two_players, lobby_game


async def test_scoring_options_returns_200(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  so = await ScoringOptions(client).get(game.id, player.id)
  so.assert_status(200)


async def test_scoring_options_returns_only_nonzero_scores(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  so = await ScoringOptions(client).get(game.id, player.id)
  so.assert_all_scores_positive()


async def test_scoring_options_excludes_already_scored(client: AsyncClient):
  player, game = await active_game(client)
  await game.roll(game.id, player.id)
  await Scorecard(client).score(game.id, player.id, 'chance', token=player.token)
  await game.roll(game.id, player.id)
  so = await ScoringOptions(client).get(game.id, player.id)
  so.assert_excludes_category('chance')


async def test_scoring_options_game_not_found_returns_404(
  client: AsyncClient, make_token
):
  player = await Player(client).create('Alice', token=make_token())
  so = await ScoringOptions(client).get(999, player.id)
  so.assert_status(404).assert_has_detail()


async def test_scoring_options_player_not_in_game_returns_404(
  client: AsyncClient, make_token
):
  _, game = await active_game(client)
  other = await Player(client).create('Bob', token=make_token())
  so = await ScoringOptions(client).get(game.id, other.id)
  so.assert_status(404).assert_has_detail()


async def test_scoring_options_game_not_active_returns_409(client: AsyncClient):
  player, game = await lobby_game(client)
  so = await ScoringOptions(client).get(game.id, player.id)
  so.assert_status(409).assert_has_detail()


async def test_scoring_options_not_your_turn_returns_403(client: AsyncClient):
  p1, p2, game = await active_game_two_players(client)
  await game.roll(game.id, p1.id)
  so = await ScoringOptions(client).get(game.id, p2.id)
  so.assert_status(403).assert_has_detail()
