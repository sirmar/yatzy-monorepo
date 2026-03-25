from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player
from tests.e2e.scorecards import Scorecard
from tests.e2e.scoring_options import ScoringOptions
from tests.e2e.helpers import active_game, active_game_two_players, lobby_game


async def _play_turn(client: AsyncClient, game: Game, game_id: int, player_id: int) -> None:
  await game.roll(game_id, player_id)
  options = await ScoringOptions(client).get(game_id, player_id)
  if options.json:
    category = options.json[0]['category']
  else:
    sc = await Scorecard(client).get(game_id, player_id)
    category = next(e['category'] for e in sc.json['entries'] if e['score'] is None)
  await Scorecard(client).score(game_id, player_id, category)


async def _finish_one_player_game(client: AsyncClient) -> tuple[Player, Game]:
  player, game = await active_game(client)
  for _ in range(20):
    await _play_turn(client, game, game.id, player.id)
  return player, game


async def test_finished_game_appears_in_high_scores(client: AsyncClient):
  player, game = await _finish_one_player_game(client)

  response = await client.get('/high-scores')
  assert response.status_code == 200
  scores = response.json()
  assert len(scores) == 1
  entry = scores[0]
  assert entry['player_id'] == player.id
  assert entry['player_name'] == player.json['name']
  assert entry['game_id'] == game.id
  assert entry['finished_at'] is not None
  assert entry['total_score'] > 0


async def test_unfinished_games_not_in_high_scores(client: AsyncClient):
  await lobby_game(client)
  await active_game(client)

  response = await client.get('/high-scores')
  assert response.status_code == 200
  assert response.json() == []


async def test_two_players_each_appear_separately(client: AsyncClient):
  p1, p2, game = await active_game_two_players(client)
  for _ in range(20):
    await _play_turn(client, game, game.id, p1.id)
    await _play_turn(client, game, game.id, p2.id)

  response = await client.get('/high-scores')
  assert response.status_code == 200
  scores = response.json()
  assert len(scores) == 2
  player_ids = {s['player_id'] for s in scores}
  assert p1.id in player_ids
  assert p2.id in player_ids
  assert all(s['game_id'] == game.id for s in scores)


async def test_results_sorted_by_total_score_descending(client: AsyncClient):
  for _ in range(3):
    await _finish_one_player_game(client)

  response = await client.get('/high-scores')
  assert response.status_code == 200
  scores = response.json()
  totals = [s['total_score'] for s in scores]
  assert totals == sorted(totals, reverse=True)
