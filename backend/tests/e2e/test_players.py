from httpx import AsyncClient
from tests.e2e.players import create_player


async def test_create_player(client: AsyncClient):
  response = await create_player(client, 'Alice')
  assert response.status_code == 201
  body = response.json()
  assert body['id'] > 0
  assert body['name'] == 'Alice'
  assert 'created_at' in body


async def test_create_player_missing_name(client: AsyncClient):
  response = await client.post('/players', json={})
  assert response.status_code == 422
  assert 'detail' in response.json()


async def test_create_player_empty_name(client: AsyncClient):
  response = await create_player(client, '')
  assert response.status_code == 422
  assert 'detail' in response.json()


async def test_create_player_name_too_long(client: AsyncClient):
  response = await create_player(client, 'x' * 65)
  assert response.status_code == 422
  assert 'detail' in response.json()
