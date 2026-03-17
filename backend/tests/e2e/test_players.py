from tests.e2e.players import Player


async def test_create_player(client):
  player = await Player(client).create('Alice')
  (player
    .assert_status(201)
    .assert_id_positive()
    .assert_name('Alice')
    .assert_has_created_at())


async def test_create_player_missing_name(client):
  player = await Player(client).create()
  player.assert_status(422).assert_has_detail()


async def test_create_player_empty_name(client):
  player = await Player(client).create('')
  player.assert_status(422).assert_has_detail()


async def test_create_player_name_too_long(client):
  player = await Player(client).create('x' * 65)
  player.assert_status(422).assert_has_detail()
