import uuid
import jwt as pyjwt
from httpx import AsyncClient
from app.main import settings
from tests.e2e.games import Game
from tests.e2e.players import Player


def make_token() -> str:
  uid = str(uuid.uuid4())
  payload = {'sub': uid, 'email': f'{uid}@test.example'}
  return pyjwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def lobby_game(client: AsyncClient) -> tuple[Player, Game]:
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  game = await Game(client).create(player.id)
  return player, game


async def active_game(client: AsyncClient) -> tuple[Player, Game]:
  player, game = await lobby_game(client)
  await game.start(game.id, player.id)
  return player, game


async def abandoned_game(client: AsyncClient) -> tuple[Player, Game]:
  player, game = await active_game(client)
  await game.abort(game.id)
  return player, game


async def active_game_two_players(client: AsyncClient) -> tuple[Player, Player, Game]:
  t1, t2 = make_token(), make_token()
  p1 = await Player(client).create('Alice', token=t1)
  p2 = await Player(client).create('Bob', token=t2)
  game = await Game(client).create(p1.id)
  await game.join(game.id, p2.id)
  await game.start(game.id, p1.id)
  return p1, p2, game


async def active_sequential_game(client: AsyncClient) -> tuple[Player, Game]:
  token = make_token()
  player = await Player(client).create('Alice', token=token)
  game = await Game(client).create(player.id, mode='sequential')
  await game.start(game.id, player.id)
  return player, game
