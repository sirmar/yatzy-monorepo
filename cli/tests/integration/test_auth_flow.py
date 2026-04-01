import pytest

from yatzy.auth import AuthClient, AuthError
from yatzy.credentials import Credentials

from .conftest import AUTH_URL, unique_email


@pytest.mark.integration
class TestLogin:
  def setup_method(self) -> None:
    self.client = AuthClient(base_url=AUTH_URL)

  def teardown_method(self) -> None:
    self.client.close()

  def test_returns_credentials_on_valid_login(self) -> None:
    self.GivenRegisteredAndVerifiedUser('pass123xyz')
    result = self.WhenLogin()
    self.ThenCredentialsReturned(result)

  def test_raises_on_wrong_password(self) -> None:
    self.GivenRegisteredAndVerifiedUser('correctpassword')
    self.ThenRaisesAuthError('wrongpassword')

  def test_raises_on_unverified_email(self) -> None:
    email = unique_email()
    self.email = email
    self.password = 'password123'
    self.client._client.post(
      '/register', json={'email': email, 'password': 'password123'}
    )
    self.ThenRaisesAuthError('password123')

  def test_raises_on_unknown_email(self) -> None:
    self.email = 'nonexistent@example.com'
    self.password = 'password123'
    self.ThenRaisesAuthError('password123')

  def GivenRegisteredAndVerifiedUser(self, password: str) -> None:
    from .conftest import register_and_login

    email = unique_email()
    self.email = email
    self.password = password
    register_and_login(email, password)

  def WhenLogin(self) -> Credentials:
    return self.client.login(self.email, self.password)

  def ThenCredentialsReturned(self, result: Credentials) -> None:
    assert result.access_token
    assert result.refresh_token

  def ThenRaisesAuthError(self, password: str) -> None:
    with pytest.raises(AuthError):
      self.client.login(self.email, password)


@pytest.mark.integration
class TestRefresh:
  def setup_method(self) -> None:
    self.client = AuthClient(base_url=AUTH_URL)

  def teardown_method(self) -> None:
    self.client.close()

  def test_returns_new_credentials(self) -> None:
    self.GivenValidRefreshToken()
    result = self.WhenRefresh()
    self.ThenNewCredentialsReturned(result)

  def test_raises_on_invalid_token(self) -> None:
    self.ThenRaisesAuthErrorOnRefresh('invalid-token')

  def GivenValidRefreshToken(self) -> None:
    email = unique_email()
    creds = self.client.login(*self._register_and_get_creds(email))
    self.refresh_token = creds.refresh_token
    self.original_access_token = creds.access_token

  def _register_and_get_creds(self, email: str) -> tuple[str, str]:
    from .conftest import register_and_login

    password = 'password123'
    register_and_login(email, password)
    return email, password

  def WhenRefresh(self) -> Credentials:
    return self.client.refresh(self.refresh_token)

  def ThenNewCredentialsReturned(self, result: Credentials) -> None:
    assert result.access_token
    assert result.refresh_token

  def ThenRaisesAuthErrorOnRefresh(self, token: str) -> None:
    with pytest.raises(AuthError):
      self.client.refresh(token)


@pytest.mark.integration
class TestRegister:
  def setup_method(self) -> None:
    self.client = AuthClient(base_url=AUTH_URL)

  def teardown_method(self) -> None:
    self.client.close()

  def test_succeeds_with_valid_credentials(self) -> None:
    self.WhenRegister(unique_email(), 'password123')

  def test_raises_on_duplicate_email(self) -> None:
    email = unique_email()
    self.WhenRegister(email, 'password123')
    with pytest.raises(AuthError):
      self.WhenRegister(email, 'password123')

  def test_raises_on_short_password(self) -> None:
    with pytest.raises(AuthError):
      self.WhenRegister(unique_email(), 'short')

  def WhenRegister(self, email: str, password: str) -> None:
    self.client.register(email, password)
