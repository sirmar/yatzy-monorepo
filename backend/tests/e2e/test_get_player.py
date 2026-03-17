from tests.e2e.players import Player


async def test_get_player_returns_player(client):
  player = Player(client)
  await player.create('Alice')
  await player.get(player.id)
  player.assert_status(200)
  player.assert_name('Alice')
  player.assert_has_created_at()


async def test_get_player_not_found(client):
  player = Player(client)
  await player.get(999999)
  player.assert_status(404)
