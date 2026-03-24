from app.config import Settings
from app.users.auth import create_access_token, decode_access_token, hash_password, verify_password


def make_settings(**kwargs) -> Settings:
  defaults = dict(
    database_url='mysql://root:root@localhost:3306/test',
    jwt_secret='test-secret-that-is-long-enough-for-hs256',
    jwt_algorithm='HS256',
    access_token_expire_minutes=15,
    refresh_token_expire_days=30,
  )
  return Settings(**{**defaults, **kwargs})


class TestHashPassword:
  def test_hashed_password_verifies(self):
    self.WhenHashed('mysecret')
    self.ThenVerifies('mysecret')

  def test_wrong_password_does_not_verify(self):
    self.WhenHashed('mysecret')
    self.ThenDoesNotVerify('wrongpassword')

  def WhenHashed(self, plain: str):
    self.hashed = hash_password(plain)

  def ThenVerifies(self, plain: str):
    assert verify_password(plain, self.hashed) is True

  def ThenDoesNotVerify(self, plain: str):
    assert verify_password(plain, self.hashed) is False


class TestCreateAccessToken:
  def setup_method(self):
    self.settings = make_settings()

  def test_token_decodes_to_correct_payload(self):
    self.WhenTokenCreated('user-123', 'user@example.com')
    self.ThenPayloadContains('user-123', 'user@example.com')

  def test_expired_token_raises_401(self):
    self.GivenExpiredSettings()
    self.WhenTokenCreated('user-123', 'user@example.com')
    self.ThenDecodeRaises401()

  def GivenExpiredSettings(self):
    self.settings = make_settings(access_token_expire_minutes=-1)

  def WhenTokenCreated(self, user_id: str, email: str):
    self.token = create_access_token(user_id, email, self.settings)

  def ThenPayloadContains(self, user_id: str, email: str):
    payload = decode_access_token(self.token, self.settings)
    assert payload['sub'] == user_id
    assert payload['email'] == email

  def ThenDecodeRaises401(self):
    from fastapi import HTTPException
    import pytest
    with pytest.raises(HTTPException) as exc:
      decode_access_token(self.token, self.settings)
    assert exc.value.status_code == 401
