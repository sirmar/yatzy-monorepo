from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import active_game, lobby_game, make_token, play_turn
from tests.e2e.players import Player
from tests.e2e.test_high_scores import _finish_one_player_game


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
  assert data['total_games_played'] == 0
  assert data['maxi']['games_played'] == 0
  assert data['maxi']['high_score'] is None
  assert data['maxi']['average_score'] is None
  assert data['maxi']['bonus_count'] == 0
  assert data['maxi']['yatzy_hit_count'] == 0


async def test_stats_with_one_finished_game(client: AsyncClient):
  player, _ = await _finish_one_player_game(client)

  response = await client.get(f'/players/{player.id}/stats')
  assert response.status_code == 200
  data = response.json()
  assert data['total_games_played'] == 1
  assert data['maxi']['games_played'] == 1
  assert data['maxi']['high_score'] is not None
  assert data['maxi']['high_score'] > 0
  assert data['maxi']['average_score'] == data['maxi']['high_score']


async def test_stats_active_game_not_counted(client: AsyncClient):
  player, _ = await active_game(client)

  response = await client.get(f'/players/{player.id}/stats')
  assert response.status_code == 200
  assert response.json()['total_games_played'] == 0


async def test_stats_multiple_finished_games(client: AsyncClient):
  player = await Player(client).create('StatsPlayer', token=make_token())

  for _ in range(2):
    game = await Game(client).create(player.id, token=player.token)
    await game.start(game.id, player.id)
    for _ in range(20):
      await play_turn(client, game, game.id, player.id, player.token)

  response = await client.get(f'/players/{player.id}/stats')
  assert response.status_code == 200
  data = response.json()
  assert data['total_games_played'] == 2
  assert data['maxi']['games_played'] == 2
  assert data['maxi']['high_score'] >= data['maxi']['average_score']


async def test_stats_split_by_mode(client: AsyncClient):
  player = await Player(client).create('ModePlayer', token=make_token())

  standard_game = await Game(client).create(player.id, token=player.token)
  await standard_game.start(standard_game.id, player.id)
  for _ in range(20):
    await play_turn(client, standard_game, standard_game.id, player.id, player.token)

  yatzy_game = await Game(client).create(player.id, mode='yatzy', token=player.token)
  await yatzy_game.start(yatzy_game.id, player.id)
  for _ in range(15):
    await play_turn(client, yatzy_game, yatzy_game.id, player.id, player.token)

  response = await client.get(f'/players/{player.id}/stats')
  assert response.status_code == 200
  data = response.json()
  assert data['total_games_played'] == 2
  assert data['maxi']['games_played'] == 1
  assert data['yatzy']['games_played'] == 1
  assert data['maxi_sequential']['games_played'] == 0
  assert data['yatzy_sequential']['games_played'] == 0
