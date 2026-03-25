from tests.e2e.players import Player


async def test_player_crud_flow(client, make_token):
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  player_id = player.id

  await player.get(player_id)
  player.assert_name('Alice')

  await player.update(player_id, 'Bob', token=token)
  player.assert_name('Bob')

  await player.get(player_id)
  player.assert_name('Bob')

  await player.list_all()
  player.assert_id_in_list(player_id)

  await player.delete(player_id, token=token)
  player.assert_status(204)

  await player.get(player_id)
  player.assert_status(404)

  await player.list_all()
  player.assert_id_not_in_list(player_id)
