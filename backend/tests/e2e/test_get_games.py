from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.helpers import lobby_game


async def test_list_games_empty(client: AsyncClient):
  response = await client.get('/games')
  assert response.status_code == 200
  assert response.json() == []


async def test_list_games_returns_created_games(client: AsyncClient):
  player, game1 = await lobby_game(client)
  game2 = await Game(client).create(player.id)
  response = await client.get('/games')
  assert response.status_code == 200
  ids = [g['id'] for g in response.json()]
  assert game1.id in ids
  assert game2.id in ids
