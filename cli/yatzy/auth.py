import os

import httpx

from yatzy.credentials import Credentials

AUTH_URL = os.environ.get('AUTH_URL', 'http://auth:8001')


class AuthError(Exception):
  pass


class AuthClient:
  def __init__(self, base_url: str = AUTH_URL) -> None:
    self._client = httpx.Client(base_url=base_url)

  def login(self, email: str, password: str) -> Credentials:
    r = self._client.post('/login', json={'email': email, 'password': password})
    if r.status_code == 403:
      raise AuthError('Email not verified. Check your inbox.')
    if r.status_code != 200:
      raise AuthError(r.json().get('detail', 'Login failed'))
    data = r.json()
    return Credentials(
      access_token=data['access_token'], refresh_token=data['refresh_token']
    )

  def register(self, email: str, password: str) -> None:
    r = self._client.post('/register', json={'email': email, 'password': password})
    if r.status_code != 201:
      raise AuthError(r.json().get('detail', 'Registration failed'))

  def refresh(self, refresh_token: str) -> Credentials:
    r = self._client.post('/refresh', json={'refresh_token': refresh_token})
    if r.status_code != 200:
      raise AuthError('Session expired. Please log in again.')
    data = r.json()
    return Credentials(
      access_token=data['access_token'], refresh_token=data['refresh_token']
    )

  def logout(self, refresh_token: str) -> None:
    self._client.post('/logout', json={'refresh_token': refresh_token})

  def close(self) -> None:
    self._client.close()
