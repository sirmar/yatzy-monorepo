from httpx import AsyncClient
from tests.e2e.players import create_player, update_player, delete_player


async def test_update_player_returns_updated_player(client: AsyncClient):
  created = (await create_player(client, 'Alice')).json()
  response = await update_player(client, created['id'], 'Bob')
  assert response.status_code == 200
  body = response.json()
  assert body['id'] == created['id']
  assert body['name'] == 'Bob'
  assert 'created_at' in body


async def test_update_player_not_found(client: AsyncClient):
  response = await update_player(client, 999999, 'Bob')
  assert response.status_code == 404


async def test_update_player_empty_name(client: AsyncClient):
  created = (await create_player(client, 'Alice')).json()
  response = await update_player(client, created['id'], '')
  assert response.status_code == 422


async def test_update_player_name_too_long(client: AsyncClient):
  created = (await create_player(client, 'Alice')).json()
  response = await update_player(client, created['id'], 'x' * 65)
  assert response.status_code == 422


async def test_update_deleted_player_returns_404(client: AsyncClient):
  created = (await create_player(client, 'Alice')).json()
  await delete_player(client, created['id'])
  response = await update_player(client, created['id'], 'Bob')
  assert response.status_code == 404
