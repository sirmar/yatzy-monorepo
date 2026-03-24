import pytest
from httpx import AsyncClient


async def register(client: AsyncClient, email: str = 'user@example.com', password: str = 'password123') -> dict:
  response = await client.post('/register', json={'email': email, 'password': password})
  return response


async def login(client: AsyncClient, email: str = 'user@example.com', password: str = 'password123') -> dict:
  response = await client.post('/login', json={'email': email, 'password': password})
  return response


class TestRegister:
  async def test_returns_tokens_on_success(self, client: AsyncClient):
    response = await register(client)
    assert response.status_code == 201
    body = response.json()
    assert 'access_token' in body
    assert 'refresh_token' in body
    assert body['token_type'] == 'bearer'

  async def test_rejects_duplicate_email(self, client: AsyncClient):
    await register(client)
    response = await register(client)
    assert response.status_code == 409

  async def test_rejects_short_password(self, client: AsyncClient):
    response = await register(client, password='short')
    assert response.status_code == 422

  async def test_rejects_invalid_email(self, client: AsyncClient):
    response = await register(client, email='not-an-email')
    assert response.status_code == 422


class TestLogin:
  async def test_returns_tokens_on_valid_credentials(self, client: AsyncClient):
    await register(client)
    response = await login(client)
    assert response.status_code == 200
    body = response.json()
    assert 'access_token' in body
    assert 'refresh_token' in body

  async def test_rejects_wrong_password(self, client: AsyncClient):
    await register(client)
    response = await login(client, password='wrongpassword')
    assert response.status_code == 401

  async def test_rejects_unknown_email(self, client: AsyncClient):
    response = await login(client, email='nobody@example.com')
    assert response.status_code == 401


class TestRefresh:
  async def test_returns_new_token_pair(self, client: AsyncClient):
    reg = (await register(client)).json()
    response = await client.post('/refresh', json={'refresh_token': reg['refresh_token']})
    assert response.status_code == 200
    body = response.json()
    assert 'access_token' in body
    assert 'refresh_token' in body
    assert body['refresh_token'] != reg['refresh_token']

  async def test_rejects_reused_refresh_token(self, client: AsyncClient):
    reg = (await register(client)).json()
    await client.post('/refresh', json={'refresh_token': reg['refresh_token']})
    response = await client.post('/refresh', json={'refresh_token': reg['refresh_token']})
    assert response.status_code == 401

  async def test_rejects_invalid_token(self, client: AsyncClient):
    response = await client.post('/refresh', json={'refresh_token': 'not-a-valid-token'})
    assert response.status_code == 401


class TestLogout:
  async def test_revokes_refresh_token(self, client: AsyncClient):
    reg = (await register(client)).json()
    response = await client.post('/logout', json={'refresh_token': reg['refresh_token']})
    assert response.status_code == 204
    refresh = await client.post('/refresh', json={'refresh_token': reg['refresh_token']})
    assert refresh.status_code == 401

  async def test_is_idempotent(self, client: AsyncClient):
    reg = (await register(client)).json()
    await client.post('/logout', json={'refresh_token': reg['refresh_token']})
    response = await client.post('/logout', json={'refresh_token': reg['refresh_token']})
    assert response.status_code == 204


class TestMe:
  async def test_returns_user_for_valid_token(self, client: AsyncClient):
    reg = (await register(client, email='me@example.com')).json()
    response = await client.get('/me', headers={'Authorization': f'Bearer {reg["access_token"]}'})
    assert response.status_code == 200
    body = response.json()
    assert body['email'] == 'me@example.com'

  async def test_rejects_missing_token(self, client: AsyncClient):
    response = await client.get('/me')
    assert response.status_code == 401

  async def test_rejects_invalid_token(self, client: AsyncClient):
    response = await client.get('/me', headers={'Authorization': 'Bearer invalid.token.here'})
    assert response.status_code == 401
