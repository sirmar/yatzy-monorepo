from tests.e2e.players import Player


async def test_update_player_returns_updated_player(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  await player.update(player.id, 'Bob', token=token)
  (player.assert_status(200).assert_name('Bob').assert_has_created_at())


async def test_update_player_not_found(client, make_token):
  player = await Player(client).update(999999, 'Bob', token=make_token())
  player.assert_status(404)


async def test_update_player_empty_name(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  await player.update(player.id, '', token=token)
  player.assert_status(422)


async def test_update_player_name_too_long(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  await player.update(player.id, 'x' * 65, token=token)
  player.assert_status(422)


async def test_update_deleted_player_returns_404(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  await player.delete(player.id, token=token)
  await player.update(player.id, 'Bob', token=token)
  player.assert_status(404)
