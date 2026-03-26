from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import active_game, lobby_game, make_token
from tests.e2e.players import Player
from tests.e2e.test_high_scores import _finish_one_player_game, _play_turn


async def test_stats_404_for_unknown_player(client: AsyncClient):
  response = await client.get('/players/999999/stats')
  assert response.status_code == 404


async def test_stats_no_finished_games(client: AsyncClient):
  player, _ = await lobby_game(client)

  response = await client.get(f'/players/{player.id}/stats')
  assert response.status_code == 200
  data = response.json()
  assert data['player_id'] == player.id
  assert data['player_name'] == player.json['name']
  assert data['member_since'] is not None
  assert data['games_played'] == 0
  assert data['high_score'] is None
  assert data['average_score'] is None
  assert data['bonus_count'] == 0
  assert data['maxi_yatzy_count'] == 0


async def test_stats_with_one_finished_game(client: AsyncClient):
  player, _ = await _finish_one_player_game(client)

  response = await client.get(f'/players/{player.id}/stats')
  assert response.status_code == 200
  data = response.json()
  assert data['games_played'] == 1
  assert data['high_score'] is not None
  assert data['high_score'] > 0
  assert data['average_score'] == data['high_score']


async def test_stats_active_game_not_counted(client: AsyncClient):
  player, _ = await active_game(client)

  response = await client.get(f'/players/{player.id}/stats')
  assert response.status_code == 200
  assert response.json()['games_played'] == 0


async def test_stats_multiple_finished_games(client: AsyncClient):
  token = make_token()
  player = await Player(client).create('StatsPlayer', token=token)

  for _ in range(2):
    game = await Game(client).create(player.id)
    await game.start(game.id, player.id)
    for _ in range(20):
      await _play_turn(client, game, game.id, player.id)

  response = await client.get(f'/players/{player.id}/stats')
  assert response.status_code == 200
  data = response.json()
  assert data['games_played'] == 2
  assert data['high_score'] >= data['average_score']
