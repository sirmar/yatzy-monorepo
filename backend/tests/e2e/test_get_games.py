from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def test_list_games_empty(client: AsyncClient):
  response = await client.get('/games')
  assert response.status_code == 200
  assert response.json() == []


async def test_list_games_returns_created_games(client: AsyncClient):
  player = await Player(client).create('Alice')
  game1 = await Game(client).create(player.id)
  game2 = await Game(client).create(player.id)
  response = await client.get('/games')
  assert response.status_code == 200
  ids = [g['id'] for g in response.json()]
  assert game1.id in ids
  assert game2.id in ids
