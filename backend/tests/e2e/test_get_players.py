from tests.e2e.players import create_player, list_players


async def test_list_players_empty(client):
  response = await list_players(client)
  assert response.status_code == 200
  assert response.json() == []


async def test_list_players_returns_created_players(client):
  await create_player(client, 'Alice')
  await create_player(client, 'Bob')
  response = await list_players(client)
  assert response.status_code == 200
  names = [p['name'] for p in response.json()]
  assert 'Alice' in names
  assert 'Bob' in names
