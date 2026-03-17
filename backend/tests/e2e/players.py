from httpx import AsyncClient, Response


async def create_player(client: AsyncClient, name: str) -> Response:
  return await client.post('/players', json={'name': name})


async def list_players(client: AsyncClient) -> Response:
  return await client.get('/players')
