import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def base_state():
  return {
    'game_mode': 'maxi',
    'dice': [1, 2, 3, 4, 5, 6],
    'kept': [False] * 6,
    'rolls_remaining': 2,
    'saved_rolls': 0,
    'has_rolled': True,
    'scores': {},
  }


@pytest.fixture
async def client():
  async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as c:
    yield c


async def test_post_action_returns_roll_or_score(client, base_state):
  response = await client.post('/action', json=base_state)
  assert response.status_code == 200
  data = response.json()
  assert data['action'] in ('roll', 'score')


async def test_full_straight_returns_score(client, base_state):
  response = await client.post('/action', json=base_state)
  assert response.status_code == 200
  data = response.json()
  assert data['action'] == 'score'
  assert data['category'] == 'full_straight'


async def test_roll_response_has_keep_list(client, base_state):
  base_state['dice'] = [1, 1, 1, 2, 3, 4]
  response = await client.post('/action', json=base_state)
  assert response.status_code == 200
  data = response.json()
  assert data['action'] == 'roll'
  assert len(data['keep']) == 6
  assert all(isinstance(k, bool) for k in data['keep'])


async def test_must_score_returns_score(client, base_state):
  base_state['rolls_remaining'] = 0
  base_state['saved_rolls'] = 0
  response = await client.post('/action', json=base_state)
  assert response.status_code == 200
  assert response.json()['action'] == 'score'


async def test_invalid_request_returns_422(client):
  response = await client.post('/action', json={'dice': 'bad'})
  assert response.status_code == 422


async def test_yatzy_mode(client, base_state):
  base_state['game_mode'] = 'yatzy'
  base_state['dice'] = [1, 2, 3, 4, 5, 5]
  base_state['scores'] = {}
  response = await client.post('/action', json=base_state)
  assert response.status_code == 200
  assert response.json()['action'] in ('roll', 'score')


async def test_maxi_sequential_mode(client, base_state):
  base_state['game_mode'] = 'maxi_sequential'
  response = await client.post('/action', json=base_state)
  assert response.status_code == 200
  assert response.json()['action'] in ('roll', 'score')


async def test_yatzy_sequential_mode(client, base_state):
  base_state['game_mode'] = 'yatzy_sequential'
  base_state['dice'] = [1, 2, 3, 4, 5, 5]
  response = await client.post('/action', json=base_state)
  assert response.status_code == 200
  assert response.json()['action'] in ('roll', 'score')


async def test_invalid_game_mode_returns_422(client, base_state):
  base_state['game_mode'] = 'invalid_mode'
  response = await client.post('/action', json=base_state)
  assert response.status_code == 422
