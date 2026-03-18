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
