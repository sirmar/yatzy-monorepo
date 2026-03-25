from tests.e2e.players import Player


async def test_list_players_empty(client):
  player = Player(client)
  await player.list_all()
  player.assert_status(200)
  player.assert_is_empty_list()


async def test_list_players_returns_created_players(client, make_token):
  player = Player(client)
  await player.create('Alice', token=make_token())
  await player.create('Bob', token=make_token())
  await player.list_all()
  player.assert_names_include('Alice', 'Bob')
