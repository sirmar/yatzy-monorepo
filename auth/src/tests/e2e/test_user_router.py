from httpx import AsyncClient


async def register(
  client: AsyncClient, email: str = 'user@example.com', password: str = 'password123'
) -> dict:
  response = await client.post('/register', json={'email': email, 'password': password})
  return response


async def verify_email(client: AsyncClient, email: str = 'user@example.com') -> dict:
  token_response = await client.get(f'/dev/verification-token?email={email}')
  token = token_response.json()['token']
  return await client.post('/verify-email', json={'token': token})


async def register_and_verify(
  client: AsyncClient, email: str = 'user@example.com', password: str = 'password123'
) -> dict:
  await register(client, email, password)
  return await verify_email(client, email)


async def login(
  client: AsyncClient, email: str = 'user@example.com', password: str = 'password123'
) -> dict:
  response = await client.post('/login', json={'email': email, 'password': password})
  return response


class TestRegister:
  async def test_returns_message_on_success(self, client: AsyncClient):
    response = await register(client)
    assert response.status_code == 201
    assert response.json()['message'] == 'Verification email sent'

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


class TestVerifyEmail:
  async def test_returns_tokens_on_success(self, client: AsyncClient):
    await register(client)
    response = await verify_email(client)
    assert response.status_code == 200
    body = response.json()
    assert 'access_token' in body
    assert 'refresh_token' in body
    assert body['token_type'] == 'bearer'

  async def test_rejects_invalid_token(self, client: AsyncClient):
    response = await client.post('/verify-email', json={'token': 'not-a-valid-token'})
    assert response.status_code == 400

  async def test_rejects_reused_token(self, client: AsyncClient):
    await register(client)
    token_response = await client.get('/dev/verification-token?email=user@example.com')
    token = token_response.json()['token']
    await client.post('/verify-email', json={'token': token})
    response = await client.post('/verify-email', json={'token': token})
    assert response.status_code == 400


class TestLogin:
  async def test_returns_tokens_on_valid_credentials(self, client: AsyncClient):
    await register_and_verify(client)
    response = await login(client)
    assert response.status_code == 200
    body = response.json()
    assert 'access_token' in body
    assert 'refresh_token' in body

  async def test_rejects_unverified_user(self, client: AsyncClient):
    await register(client)
    response = await login(client)
    assert response.status_code == 403

  async def test_rejects_wrong_password(self, client: AsyncClient):
    await register_and_verify(client)
    response = await login(client, password='wrongpassword')
    assert response.status_code == 401

  async def test_rejects_unknown_email(self, client: AsyncClient):
    response = await login(client, email='nobody@example.com')
    assert response.status_code == 401


class TestForgotPassword:
  async def test_always_returns_200_for_known_email(self, client: AsyncClient):
    await register_and_verify(client)
    response = await client.post('/forgot-password', json={'email': 'user@example.com'})
    assert response.status_code == 200

  async def test_always_returns_200_for_unknown_email(self, client: AsyncClient):
    response = await client.post(
      '/forgot-password', json={'email': 'nobody@example.com'}
    )
    assert response.status_code == 200


class TestResetPassword:
  async def test_resets_password_successfully(self, client: AsyncClient):
    await register_and_verify(client)
    await client.post('/forgot-password', json={'email': 'user@example.com'})
    token_response = await client.get('/dev/reset-token?email=user@example.com')
    token = token_response.json()['token']
    response = await client.post(
      '/reset-password', json={'token': token, 'new_password': 'newpassword456'}
    )
    assert response.status_code == 204
    login_response = await login(client, password='newpassword456')
    assert login_response.status_code == 200

  async def test_revokes_sessions_on_reset(self, client: AsyncClient):
    tokens = (await register_and_verify(client)).json()
    await client.post('/forgot-password', json={'email': 'user@example.com'})
    token_response = await client.get('/dev/reset-token?email=user@example.com')
    token = token_response.json()['token']
    await client.post(
      '/reset-password', json={'token': token, 'new_password': 'newpassword456'}
    )
    refresh_response = await client.post(
      '/refresh', json={'refresh_token': tokens['refresh_token']}
    )
    assert refresh_response.status_code == 401

  async def test_rejects_invalid_token(self, client: AsyncClient):
    response = await client.post(
      '/reset-password', json={'token': 'invalid', 'new_password': 'newpassword456'}
    )
    assert response.status_code == 400

  async def test_rejects_short_new_password(self, client: AsyncClient):
    await register_and_verify(client)
    await client.post('/forgot-password', json={'email': 'user@example.com'})
    token_response = await client.get('/dev/reset-token?email=user@example.com')
    token = token_response.json()['token']
    response = await client.post(
      '/reset-password', json={'token': token, 'new_password': 'short'}
    )
    assert response.status_code == 422

  async def test_rejects_reused_token(self, client: AsyncClient):
    await register_and_verify(client)
    await client.post('/forgot-password', json={'email': 'user@example.com'})
    token_response = await client.get('/dev/reset-token?email=user@example.com')
    token = token_response.json()['token']
    await client.post(
      '/reset-password', json={'token': token, 'new_password': 'newpassword456'}
    )
    response = await client.post(
      '/reset-password', json={'token': token, 'new_password': 'anotherpassword'}
    )
    assert response.status_code == 400


class TestRefresh:
  async def test_returns_new_token_pair(self, client: AsyncClient):
    reg = (await register_and_verify(client)).json()
    response = await client.post(
      '/refresh', json={'refresh_token': reg['refresh_token']}
    )
    assert response.status_code == 200
    body = response.json()
    assert 'access_token' in body
    assert 'refresh_token' in body
    assert body['refresh_token'] != reg['refresh_token']

  async def test_rejects_reused_refresh_token(self, client: AsyncClient):
    reg = (await register_and_verify(client)).json()
    await client.post('/refresh', json={'refresh_token': reg['refresh_token']})
    response = await client.post(
      '/refresh', json={'refresh_token': reg['refresh_token']}
    )
    assert response.status_code == 401

  async def test_rejects_invalid_token(self, client: AsyncClient):
    response = await client.post(
      '/refresh', json={'refresh_token': 'not-a-valid-token'}
    )
    assert response.status_code == 401


class TestLogout:
  async def test_revokes_refresh_token(self, client: AsyncClient):
    reg = (await register_and_verify(client)).json()
    response = await client.post(
      '/logout', json={'refresh_token': reg['refresh_token']}
    )
    assert response.status_code == 204
    refresh = await client.post(
      '/refresh', json={'refresh_token': reg['refresh_token']}
    )
    assert refresh.status_code == 401

  async def test_is_idempotent(self, client: AsyncClient):
    reg = (await register_and_verify(client)).json()
    await client.post('/logout', json={'refresh_token': reg['refresh_token']})
    response = await client.post(
      '/logout', json={'refresh_token': reg['refresh_token']}
    )
    assert response.status_code == 204


class TestMe:
  async def test_returns_user_for_valid_token(self, client: AsyncClient):
    reg = (await register_and_verify(client, email='me@example.com')).json()
    response = await client.get(
      '/me', headers={'Authorization': f'Bearer {reg["access_token"]}'}
    )
    assert response.status_code == 200
    body = response.json()
    assert body['email'] == 'me@example.com'
    assert body['email_verified'] is True

  async def test_rejects_missing_token(self, client: AsyncClient):
    response = await client.get('/me')
    assert response.status_code == 401

  async def test_rejects_invalid_token(self, client: AsyncClient):
    response = await client.get(
      '/me', headers={'Authorization': 'Bearer invalid.token.here'}
    )
    assert response.status_code == 401


class TestChangePassword:
  async def test_changes_password_successfully(self, client: AsyncClient):
    reg = (await register_and_verify(client)).json()
    response = await client.put(
      '/password',
      json={'current_password': 'password123', 'new_password': 'newpassword456'},
      headers={'Authorization': f'Bearer {reg["access_token"]}'},
    )
    assert response.status_code == 204
    login_response = await login(client, password='newpassword456')
    assert login_response.status_code == 200

  async def test_rejects_wrong_current_password(self, client: AsyncClient):
    reg = (await register_and_verify(client)).json()
    response = await client.put(
      '/password',
      json={'current_password': 'wrongpassword', 'new_password': 'newpassword456'},
      headers={'Authorization': f'Bearer {reg["access_token"]}'},
    )
    assert response.status_code == 401

  async def test_rejects_short_new_password(self, client: AsyncClient):
    reg = (await register_and_verify(client)).json()
    response = await client.put(
      '/password',
      json={'current_password': 'password123', 'new_password': 'short'},
      headers={'Authorization': f'Bearer {reg["access_token"]}'},
    )
    assert response.status_code == 422

  async def test_rejects_unauthenticated_request(self, client: AsyncClient):
    response = await client.put(
      '/password',
      json={'current_password': 'password123', 'new_password': 'newpassword456'},
    )
    assert response.status_code == 401


class TestDeleteAccount:
  async def test_deletes_account_successfully(self, client: AsyncClient):
    reg = (await register_and_verify(client)).json()
    response = await client.delete(
      '/me',
      headers={'Authorization': f'Bearer {reg["access_token"]}'},
    )
    assert response.status_code == 204
    login_response = await login(client)
    assert login_response.status_code == 401

  async def test_revokes_refresh_tokens_on_delete(self, client: AsyncClient):
    reg = (await register_and_verify(client)).json()
    await client.delete(
      '/me', headers={'Authorization': f'Bearer {reg["access_token"]}'}
    )
    refresh_response = await client.post(
      '/refresh', json={'refresh_token': reg['refresh_token']}
    )
    assert refresh_response.status_code == 401

  async def test_rejects_unauthenticated_request(self, client: AsyncClient):
    response = await client.delete('/me')
    assert response.status_code == 401
