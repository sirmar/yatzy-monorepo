from httpx import AsyncClient
from tests.e2e.games import Game
from tests.e2e.players import Player


async def lobby_game(client: AsyncClient) -> tuple[Player, Game]:
  player = await Player(client).create('Alice')
  game = await Game(client).create(player.id)
  return player, game


async def active_game(client: AsyncClient) -> tuple[Player, Game]:
  player, game = await lobby_game(client)
  await game.start(game.id, player.id)
  return player, game


async def active_game_two_players(client: AsyncClient) -> tuple[Player, Player, Game]:
  p1 = await Player(client).create('Alice')
  p2 = await Player(client).create('Bob')
  game = await Game(client).create(p1.id)
  await game.join(game.id, p2.id)
  await game.start(game.id, p1.id)
  return p1, p2, game
