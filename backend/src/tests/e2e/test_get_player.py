from tests.e2e.players import Player


async def test_get_player_returns_player(client, make_token):
  player = await Player(client).create('Alice', token=make_token())
  await player.get(player.id)
  (player.assert_status(200).assert_name('Alice').assert_has_created_at())


async def test_get_player_not_found(client):
  player = await Player(client).get(999999)
  player.assert_status(404)
