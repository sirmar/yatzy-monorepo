from tests.e2e.players import Player


async def test_delete_player_returns_204(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  await player.delete(player.id, token=token)
  player.assert_status(204)


async def test_delete_player_not_found(client, make_token):
  player = await Player(client).delete(999999, token=make_token())
  player.assert_status(404)


async def test_delete_player_is_soft_deleted(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  await player.delete(player.id, token=token)
  await player.get(player.id)
  player.assert_status(404)
