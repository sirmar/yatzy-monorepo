from httpx import AsyncClient
from tests.e2e.players import create_player, get_player


async def test_get_player_returns_player(client: AsyncClient):
  created = (await create_player(client, 'Alice')).json()
  response = await get_player(client, created['id'])
  assert response.status_code == 200
  body = response.json()
  assert body['id'] == created['id']
  assert body['name'] == 'Alice'
  assert 'created_at' in body


async def test_get_player_not_found(client: AsyncClient):
  response = await get_player(client, 999999)
  assert response.status_code == 404
