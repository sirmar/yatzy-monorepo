import io
from PIL import Image
from tests.e2e.players import Player
from tests.e2e.utils import auth_headers


def _make_jpeg(width: int = 100, height: int = 100) -> bytes:
  buf = io.BytesIO()
  Image.new('RGB', (width, height), color=(100, 150, 200)).save(buf, 'JPEG')
  return buf.getvalue()


def _make_png() -> bytes:
  buf = io.BytesIO()
  Image.new('RGB', (100, 100), color=(200, 100, 50)).save(buf, 'PNG')
  return buf.getvalue()


async def _upload(client, player_id: int, data: bytes, content_type: str, token: str):
  return await client.post(
    f'/players/{player_id}/picture',
    files={'picture': ('photo.jpg', data, content_type)},
    headers=auth_headers(token),
  )


async def test_upload_jpeg_sets_has_picture(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  resp = await _upload(client, player.id, _make_jpeg(), 'image/jpeg', token)
  assert resp.status_code == 200
  assert resp.json()['has_picture'] is True


async def test_upload_png_sets_has_picture(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  resp = await _upload(client, player.id, _make_png(), 'image/png', token)
  assert resp.status_code == 200
  assert resp.json()['has_picture'] is True


async def test_upload_replaces_existing_picture(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  await _upload(client, player.id, _make_jpeg(), 'image/jpeg', token)
  resp = await _upload(client, player.id, _make_jpeg(), 'image/jpeg', token)
  assert resp.status_code == 200
  assert resp.json()['has_picture'] is True


async def test_delete_picture(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  await _upload(client, player.id, _make_jpeg(), 'image/jpeg', token)
  resp = await client.delete(
    f'/players/{player.id}/picture', headers=auth_headers(token)
  )
  assert resp.status_code == 204
  updated = await Player(client).get(player.id)
  assert updated.json['has_picture'] is False


async def test_delete_picture_not_found(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  resp = await client.delete(
    f'/players/{player.id}/picture', headers=auth_headers(token)
  )
  assert resp.status_code == 404


async def test_upload_wrong_content_type(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  resp = await _upload(client, player.id, b'data', 'image/gif', token)
  assert resp.status_code == 415


async def test_upload_too_large(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  resp = await _upload(
    client, player.id, b'x' * (5 * 1024 * 1024 + 1), 'image/jpeg', token
  )
  assert resp.status_code == 413


async def test_upload_non_owner_forbidden(client, make_token):
  token_a = make_token()
  token_b = make_token()
  player = await Player(client).create('Alice', token=token_a)
  resp = await _upload(client, player.id, _make_jpeg(), 'image/jpeg', token_b)
  assert resp.status_code == 403


async def test_upload_player_not_found(client, make_token):
  token = make_token()
  resp = await _upload(client, 999999, _make_jpeg(), 'image/jpeg', token)
  assert resp.status_code == 404
