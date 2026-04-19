import httpx
import pytest
import respx

from yatzy.auth import AuthClient, AuthError
from yatzy.credentials import Credentials


@pytest.fixture
def client() -> AuthClient:
  return AuthClient(base_url='http://auth')


class TestLogin:
  @respx.mock
  def test_returns_credentials_on_success(self, client: AuthClient) -> None:
    respx.post('http://auth/login').mock(
      return_value=httpx.Response(
        200, json={'access_token': 'abc', 'refresh_token': 'xyz'}
      )
    )
    creds = client.login('user@example.com', 'pass')
    assert isinstance(creds, Credentials)
    assert creds.access_token == 'abc'
    assert creds.refresh_token == 'xyz'

  @respx.mock
  def test_raises_auth_error_on_403(self, client: AuthClient) -> None:
    respx.post('http://auth/login').mock(return_value=httpx.Response(403, json={}))
    with pytest.raises(AuthError, match='not verified'):
      client.login('user@example.com', 'pass')

  @respx.mock
  def test_raises_auth_error_with_detail_on_other_error(
    self, client: AuthClient
  ) -> None:
    respx.post('http://auth/login').mock(
      return_value=httpx.Response(401, json={'detail': 'Bad credentials'})
    )
    with pytest.raises(AuthError, match='Bad credentials'):
      client.login('user@example.com', 'wrong')

  @respx.mock
  def test_raises_auth_error_with_fallback_when_no_detail(
    self, client: AuthClient
  ) -> None:
    respx.post('http://auth/login').mock(return_value=httpx.Response(500, json={}))
    with pytest.raises(AuthError, match='Login failed'):
      client.login('user@example.com', 'pass')


class TestRegister:
  @respx.mock
  def test_succeeds_on_201(self, client: AuthClient) -> None:
    respx.post('http://auth/register').mock(return_value=httpx.Response(201, json={}))
    client.register('user@example.com', 'pass')

  @respx.mock
  def test_raises_auth_error_with_detail(self, client: AuthClient) -> None:
    respx.post('http://auth/register').mock(
      return_value=httpx.Response(409, json={'detail': 'Already registered'})
    )
    with pytest.raises(AuthError, match='Already registered'):
      client.register('user@example.com', 'pass')

  @respx.mock
  def test_raises_auth_error_with_fallback_when_no_detail(
    self, client: AuthClient
  ) -> None:
    respx.post('http://auth/register').mock(return_value=httpx.Response(500, json={}))
    with pytest.raises(AuthError, match='Registration failed'):
      client.register('user@example.com', 'pass')


class TestRefresh:
  @respx.mock
  def test_returns_new_credentials_on_success(self, client: AuthClient) -> None:
    respx.post('http://auth/refresh').mock(
      return_value=httpx.Response(
        200, json={'access_token': 'new-access', 'refresh_token': 'new-refresh'}
      )
    )
    creds = client.refresh('old-refresh')
    assert creds.access_token == 'new-access'
    assert creds.refresh_token == 'new-refresh'

  @respx.mock
  def test_raises_auth_error_on_non_200(self, client: AuthClient) -> None:
    respx.post('http://auth/refresh').mock(return_value=httpx.Response(401, json={}))
    with pytest.raises(AuthError, match='expired'):
      client.refresh('bad-token')


class TestLogout:
  @respx.mock
  def test_posts_to_logout_endpoint(self, client: AuthClient) -> None:
    route = respx.post('http://auth/logout').mock(
      return_value=httpx.Response(200, json={})
    )
    client.logout('my-refresh-token')
    assert route.called
    import json

    body = json.loads(route.calls[0].request.content)
    assert body['refresh_token'] == 'my-refresh-token'


class TestClose:
  def test_close_does_not_raise(self, client: AuthClient) -> None:
    client.close()
