from tests.e2e.players import Player


async def test_player_crud_flow(client):
  player = Player(client)

  await player.create('Alice')
  player_id = player.id

  await player.get(player_id)
  player.assert_name('Alice')

  await player.update(player_id, 'Bob')
  player.assert_name('Bob')

  await player.get(player_id)
  player.assert_name('Bob')

  await player.list_all()
  player.assert_id_in_list(player_id)

  await player.delete(player_id)
  player.assert_status(204)

  await player.get(player_id)
  player.assert_status(404)

  await player.list_all()
  player.assert_id_not_in_list(player_id)
