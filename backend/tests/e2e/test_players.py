from tests.e2e.players import Player


async def test_create_player(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  (player
    .assert_status(201)
    .assert_id_positive()
    .assert_name('Alice')
    .assert_has_created_at())


async def test_create_player_missing_name(client, make_token):
  player = await Player(client).create(token=make_token())
  player.assert_status(422).assert_has_detail()


async def test_create_player_empty_name(client, make_token):
  player = await Player(client).create('', token=make_token())
  player.assert_status(422).assert_has_detail()


async def test_create_player_name_too_long(client, make_token):
  player = await Player(client).create('x' * 65, token=make_token())
  player.assert_status(422).assert_has_detail()


async def test_create_player_no_token_returns_401(client):
  player = await Player(client).create('Alice')
  player.assert_status(401)


async def test_create_player_duplicate_account_returns_409(client, make_token):
  token = make_token()
  await Player(client).create('Alice', token=token)
  player = await Player(client).create('Bob', token=token)
  player.assert_status(409)


async def test_update_player_wrong_owner_returns_403(client, make_token):
  t1, t2 = make_token(), make_token()
  player = await Player(client).create('Alice', token=t1)
  other = await Player(client).update(player.id, 'Bob', token=t2)
  other.assert_status(403)


async def test_update_player_no_token_returns_401(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  result = await Player(client).update(player.id, 'Bob')
  result.assert_status(401)


async def test_delete_player_wrong_owner_returns_403(client, make_token):
  t1, t2 = make_token(), make_token()
  player = await Player(client).create('Alice', token=t1)
  result = await Player(client).delete(player.id, token=t2)
  result.assert_status(403)


async def test_delete_player_no_token_returns_401(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  result = await Player(client).delete(player.id)
  result.assert_status(401)


async def test_get_me_returns_own_player(client, make_token):
  import uuid
  account_id = str(uuid.uuid4())
  token = make_token(account_id)
  await Player(client).create('Alice', token=token)
  me = await Player(client).get_me(token)
  me.assert_status(200).assert_name('Alice').assert_account_id(account_id)


async def test_get_me_no_player_returns_404(client, make_token):
  me = await Player(client).get_me(make_token())
  me.assert_status(404)
