from httpx import AsyncClient, Response


async def create_player(client: AsyncClient, name: str) -> Response:
  return await client.post('/players', json={'name': name})


async def list_players(client: AsyncClient) -> Response:
  return await client.get('/players')


async def get_player(client: AsyncClient, player_id: int) -> Response:
  return await client.get(f'/players/{player_id}')


async def update_player(client: AsyncClient, player_id: int, name: str) -> Response:
  return await client.put(f'/players/{player_id}', json={'name': name})


async def delete_player(client: AsyncClient, player_id: int) -> Response:
  return await client.delete(f'/players/{player_id}')
