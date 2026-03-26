from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import active_game, active_game_two_players, lobby_game, make_token, play_turn
from tests.e2e.players import Player
from tests.e2e.scorecards import Scorecard
from tests.e2e.scoring_options import ScoringOptions


async def _finish_one_player_game(client: AsyncClient, mode: str = 'standard') -> tuple[Player, Game]:
  player = await Player(client).create('Alice', token=make_token())
  game = await Game(client).create(player.id, mode=mode, token=player.token)
  await game.start(game.id, player.id)
  for _ in range(20):
    await play_turn(client, game, game.id, player.id, player.token)
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
    await play_turn(client, game, game.id, p1.id, p1.token)
    await play_turn(client, game, game.id, p2.id, p2.token)

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


async def test_high_score_includes_mode(client: AsyncClient):
  await _finish_one_player_game(client, mode='standard')

  response = await client.get('/high-scores')
  assert response.status_code == 200
  scores = response.json()
  assert len(scores) == 1
  assert scores[0]['mode'] == 'standard'


async def test_sequential_game_high_score_has_sequential_mode(client: AsyncClient):
  await _finish_one_player_game(client, mode='sequential')

  response = await client.get('/high-scores')
  assert response.status_code == 200
  scores = response.json()
  assert len(scores) == 1
  assert scores[0]['mode'] == 'sequential'


async def test_high_scores_from_different_modes_returned_together(client: AsyncClient):
  await _finish_one_player_game(client, mode='standard')
  await _finish_one_player_game(client, mode='sequential')

  response = await client.get('/high-scores')
  assert response.status_code == 200
  scores = response.json()
  assert len(scores) == 2
  modes = {s['mode'] for s in scores}
  assert modes == {'standard', 'sequential'}
