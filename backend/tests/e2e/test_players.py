from httpx import AsyncClient


async def test_create_player(client: AsyncClient):
  response = await client.post('/players', json={'name': 'Alice'})
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
  response = await client.post('/players', json={'name': ''})
  assert response.status_code == 422
  assert 'detail' in response.json()


async def test_create_player_name_too_long(client: AsyncClient):
  response = await client.post('/players', json={'name': 'x' * 65})
  assert response.status_code == 422
  assert 'detail' in response.json()
