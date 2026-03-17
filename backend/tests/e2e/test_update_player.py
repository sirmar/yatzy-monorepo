from tests.e2e.players import Player


async def test_update_player_returns_updated_player(client):
  player = Player(client)
  await player.create('Alice')
  await player.update(player.id, 'Bob')
  player.assert_status(200)
  player.assert_name('Bob')
  player.assert_has_created_at()


async def test_update_player_not_found(client):
  player = Player(client)
  await player.update(999999, 'Bob')
  player.assert_status(404)


async def test_update_player_empty_name(client):
  player = Player(client)
  await player.create('Alice')
  await player.update(player.id, '')
  player.assert_status(422)


async def test_update_player_name_too_long(client):
  player = Player(client)
  await player.create('Alice')
  await player.update(player.id, 'x' * 65)
  player.assert_status(422)


async def test_update_deleted_player_returns_404(client):
  player = Player(client)
  await player.create('Alice')
  await player.delete(player.id)
  await player.update(player.id, 'Bob')
  player.assert_status(404)
