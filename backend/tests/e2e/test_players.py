from tests.e2e.players import Player


async def test_create_player(client):
  player = Player(client)
  await player.create('Alice')
  player.assert_status(201)
  player.assert_id_positive()
  player.assert_name('Alice')
  player.assert_has_created_at()


async def test_create_player_missing_name(client):
  player = Player(client)
  await player.create()
  player.assert_status(422)
  player.assert_has_detail()


async def test_create_player_empty_name(client):
  player = Player(client)
  await player.create('')
  player.assert_status(422)
  player.assert_has_detail()


async def test_create_player_name_too_long(client):
  player = Player(client)
  await player.create('x' * 65)
  player.assert_status(422)
  player.assert_has_detail()
