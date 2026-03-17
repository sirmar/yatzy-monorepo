import aiomysql
from app.game import Game


class GameRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  def _to_game(self, row: tuple, player_ids: list[int]) -> Game:
    return Game(
      id=row[0],
      status=row[1],
      creator_id=row[2],
      created_at=row[3],
      started_at=row[4],
      ended_at=row[5],
      player_ids=player_ids,
    )

  async def create(self, creator_id: int) -> Game:
    cursor = await self._conn.cursor()
    await cursor.execute(
      'INSERT INTO games (creator_id) VALUES (%s)',
      (creator_id,),
    )
    game_id = cursor.lastrowid
    await cursor.execute(
      'INSERT INTO game_players (game_id, player_id, join_order) VALUES (%s, %s, 1)',
      (game_id, creator_id),
    )
    await cursor.execute(
      'SELECT id, status, creator_id, created_at, started_at, ended_at '
      'FROM games WHERE id = %s AND deleted_at IS NULL',
      (game_id,),
    )
    row = await cursor.fetchone()
    await cursor.execute(
      'SELECT player_id FROM game_players '
      'WHERE game_id = %s AND deleted_at IS NULL ORDER BY join_order',
      (game_id,),
    )
    player_rows = await cursor.fetchall()
    await cursor.close()
    return self._to_game(row, [r[0] for r in player_rows])

  async def list_all(self) -> list[Game]:
    cursor = await self._conn.cursor()
    await cursor.execute(
      'SELECT id, status, creator_id, created_at, started_at, ended_at '
      'FROM games WHERE deleted_at IS NULL ORDER BY id',
    )
    rows = await cursor.fetchall()
    games = []
    for row in rows:
      await cursor.execute(
        'SELECT player_id FROM game_players '
        'WHERE game_id = %s AND deleted_at IS NULL ORDER BY join_order',
        (row[0],),
      )
      player_rows = await cursor.fetchall()
      games.append(self._to_game(row, [r[0] for r in player_rows]))
    await cursor.close()
    return games
