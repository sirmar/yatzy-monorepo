from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import active_game, lobby_game, make_token, play_turn
from tests.e2e.players import Player
from tests.e2e.test_high_scores import _finish_one_player_game


async def test_empty_leaderboard(client: AsyncClient):
  response = await client.get('/games-played-leaderboard', params={'sort_by': 'total'})
  assert response.status_code == 200
  assert response.json() == []


async def test_finished_game_appears_in_total(client: AsyncClient):
  player, _ = await _finish_one_player_game(client)

  response = await client.get('/games-played-leaderboard', params={'sort_by': 'total'})
  assert response.status_code == 200
  entries = response.json()
  assert len(entries) == 1
  entry = entries[0]
  assert entry['player_id'] == player.id
  assert entry['player_name'] == player.json['name']
  assert entry['total'] == 1
  assert entry['maxi'] == 1
  assert entry['maxi_sequential'] == 0


async def test_standard_game_appears_in_standard_sort(client: AsyncClient):
  player, _ = await _finish_one_player_game(client, mode='maxi')

  response = await client.get('/games-played-leaderboard', params={'sort_by': 'maxi'})
  assert response.status_code == 200
  entries = response.json()
  assert len(entries) == 1
  assert entries[0]['maxi'] == 1
  assert entries[0]['maxi_sequential'] == 0


async def test_sequential_game_appears_in_sequential_sort(client: AsyncClient):
  player, _ = await _finish_one_player_game(client, mode='maxi_sequential')

  response = await client.get('/games-played-leaderboard', params={'sort_by': 'maxi_sequential'})
  assert response.status_code == 200
  entries = response.json()
  assert len(entries) == 1
  assert entries[0]['maxi_sequential'] == 1
  assert entries[0]['maxi'] == 0


async def test_unfinished_games_excluded(client: AsyncClient):
  await lobby_game(client)
  await active_game(client)

  response = await client.get('/games-played-leaderboard', params={'sort_by': 'total'})
  assert response.status_code == 200
  assert response.json() == []


async def test_results_ordered_by_sort_field_descending(client: AsyncClient):
  p1 = await Player(client).create('Alice', token=make_token())
  p2 = await Player(client).create('Bob', token=make_token())

  for _ in range(2):
    game = await Game(client).create(p1.id, mode='maxi', token=p1.token)
    await game.start(game.id, p1.id)
    for _ in range(20):
      await play_turn(client, game, game.id, p1.id, p1.token)

  game = await Game(client).create(p2.id, mode='maxi', token=p2.token)
  await game.start(game.id, p2.id)
  for _ in range(20):
    await play_turn(client, game, game.id, p2.id, p2.token)

  response = await client.get('/games-played-leaderboard', params={'sort_by': 'total'})
  assert response.status_code == 200
  entries = response.json()
  assert entries[0]['player_id'] == p1.id
  assert entries[1]['player_id'] == p2.id


async def test_sort_by_sequential_ranks_by_sequential_count(client: AsyncClient):
  p1 = await Player(client).create('Alice', token=make_token())
  p2 = await Player(client).create('Bob', token=make_token())

  game = await Game(client).create(p1.id, mode='maxi', token=p1.token)
  await game.start(game.id, p1.id)
  for _ in range(20):
    await play_turn(client, game, game.id, p1.id, p1.token)

  for _ in range(2):
    game = await Game(client).create(p2.id, mode='maxi_sequential', token=p2.token)
    await game.start(game.id, p2.id)
    for _ in range(20):
      await play_turn(client, game, game.id, p2.id, p2.token)

  response = await client.get('/games-played-leaderboard', params={'sort_by': 'maxi_sequential'})
  assert response.status_code == 200
  entries = response.json()
  assert entries[0]['player_id'] == p2.id


async def test_capped_at_ten_entries(client: AsyncClient):
  for i in range(11):
    token = make_token()
    player = await Player(client).create(f'Player{i}', token=token)
    game = await Game(client).create(player.id, mode='maxi', token=player.token)
    await game.start(game.id, player.id)
    for _ in range(20):
      await play_turn(client, game, game.id, player.id, player.token)

  response = await client.get('/games-played-leaderboard', params={'sort_by': 'total'})
  assert response.status_code == 200
  assert len(response.json()) == 10


async def test_invalid_sort_by_returns_422(client: AsyncClient):
  response = await client.get('/games-played-leaderboard', params={'sort_by': 'invalid'})
  assert response.status_code == 422
