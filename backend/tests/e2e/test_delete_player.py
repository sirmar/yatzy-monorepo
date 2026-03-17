from tests.e2e.players import Player


async def test_delete_player_returns_204(client):
  player = Player(client)
  await player.create('Alice')
  await player.delete(player.id)
  player.assert_status(204)


async def test_delete_player_not_found(client):
  player = Player(client)
  await player.delete(999999)
  player.assert_status(404)


async def test_delete_player_is_soft_deleted(client):
  player = Player(client)
  await player.create('Alice')
  await player.delete(player.id)
  await player.get(player.id)
  player.assert_status(404)
