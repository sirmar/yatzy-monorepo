from httpx import AsyncClient
from tests.e2e.players import create_player, delete_player, get_player


async def test_delete_player_returns_204(client: AsyncClient):
  created = (await create_player(client, 'Alice')).json()
  response = await delete_player(client, created['id'])
  assert response.status_code == 204


async def test_delete_player_not_found(client: AsyncClient):
  response = await delete_player(client, 999999)
  assert response.status_code == 404


async def test_delete_player_is_soft_deleted(client: AsyncClient):
  created = (await create_player(client, 'Alice')).json()
  await delete_player(client, created['id'])
  response = await get_player(client, created['id'])
  assert response.status_code == 404
