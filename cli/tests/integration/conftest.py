import os
import uuid

import httpx
import pytest

AUTH_URL = os.environ.get('AUTH_URL', 'http://auth:8001')
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:8000')


def unique_email() -> str:
  return f'test-{uuid.uuid4().hex[:8]}@example.com'


def register_and_login(email: str, password: str = 'password123') -> str:
  """Register, verify email via dev endpoint, and return access token."""
  with httpx.Client(base_url=AUTH_URL) as client:
    r = client.post('/register', json={'email': email, 'password': password})
    assert r.status_code == 201, f'Register failed: {r.text}'

    token_r = client.get(f'/dev/verification-token?email={email}')
    assert token_r.status_code == 200, f'Dev token endpoint failed: {token_r.text}'
    token = token_r.json()['token']

    verify_r = client.post('/verify-email', json={'token': token})
    assert verify_r.status_code == 200, f'Verify failed: {verify_r.text}'
    return verify_r.json()['access_token']


def create_player(access_token: str, name: str) -> int:
  with httpx.Client(base_url=BACKEND_URL) as client:
    r = client.post(
      '/players',
      json={'name': name},
      headers={'Authorization': f'Bearer {access_token}'},
    )
    assert r.status_code == 201, f'Create player failed: {r.text}'
    return int(r.json()['id'])


@pytest.fixture
def player_a() -> tuple[str, int]:
  """Returns (access_token, player_id) for player A."""
  token = register_and_login(unique_email())
  player_id = create_player(token, 'PlayerA')
  return token, player_id


@pytest.fixture
def player_b() -> tuple[str, int]:
  """Returns (access_token, player_id) for player B."""
  token = register_and_login(unique_email())
  player_id = create_player(token, 'PlayerB')
  return token, player_id
