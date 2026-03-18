import aiomysql
from app.games.game import Game
from app.games.game_status import GameStatus


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

  async def _fetch_game(self, cursor: aiomysql.Cursor, game_id: int) -> Game:
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
    return self._to_game(row, [r[0] for r in player_rows])

  async def create(self, creator_id: int) -> Game:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'INSERT INTO games (creator_id) VALUES (%s)',
        (creator_id,),
      )
      game_id = cursor.lastrowid
      await cursor.execute(
        'INSERT INTO game_players (game_id, player_id, join_order) VALUES (%s, %s, 1)',
        (game_id, creator_id),
      )
      return await self._fetch_game(cursor, game_id)
    finally:
      await cursor.close()

  async def end(self, game_id: int) -> Game | None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'UPDATE games SET status = %s, ended_at = NOW() '
        'WHERE id = %s AND status = %s AND deleted_at IS NULL',
        (GameStatus.FINISHED, game_id, GameStatus.ACTIVE),
      )
      if cursor.rowcount == 0:
        return None
      return await self._fetch_game(cursor, game_id)
    finally:
      await cursor.close()

  async def start(self, game_id: int, turn_id: int) -> Game | None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'UPDATE games SET status = %s, started_at = NOW(), current_turn = %s '
        'WHERE id = %s AND status = %s AND deleted_at IS NULL',
        (GameStatus.ACTIVE, turn_id, game_id, GameStatus.LOBBY),
      )
      if cursor.rowcount == 0:
        return None
      return await self._fetch_game(cursor, game_id)
    finally:
      await cursor.close()

  async def get_by_id(self, game_id: int) -> Game | None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT id, status, creator_id, created_at, started_at, ended_at '
        'FROM games WHERE id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      row = await cursor.fetchone()
      if row is None:
        return None
      await cursor.execute(
        'SELECT player_id FROM game_players '
        'WHERE game_id = %s AND deleted_at IS NULL ORDER BY join_order',
        (game_id,),
      )
      player_rows = await cursor.fetchall()
      return self._to_game(row, [r[0] for r in player_rows])
    finally:
      await cursor.close()

  async def soft_delete(self, game_id: int) -> bool:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'UPDATE games SET deleted_at = NOW() '
        'WHERE id = %s AND status IN (%s, %s) AND deleted_at IS NULL',
        (game_id, GameStatus.LOBBY, GameStatus.FINISHED),
      )
      return cursor.rowcount > 0
    finally:
      await cursor.close()

  async def set_current_turn(self, game_id: int, turn_id: int) -> None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'UPDATE games SET current_turn = %s WHERE id = %s AND deleted_at IS NULL',
        (turn_id, game_id),
      )
    finally:
      await cursor.close()

  async def list_all(self) -> list[Game]:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT id, status, creator_id, created_at, started_at, ended_at '
        'FROM games WHERE deleted_at IS NULL ORDER BY id',
      )
      game_rows = await cursor.fetchall()
      if not game_rows:
        return []
      game_ids = [row[0] for row in game_rows]
      placeholders = ', '.join(['%s'] * len(game_ids))
      await cursor.execute(
        'SELECT game_id, player_id FROM game_players '
        'WHERE game_id IN ('
        + placeholders  # nosec B608
        + ') AND deleted_at IS NULL ORDER BY game_id, join_order',
        game_ids,
      )
      player_rows = await cursor.fetchall()
      players_by_game: dict[int, list[int]] = {row[0]: [] for row in game_rows}
      for game_id, player_id in player_rows:
        players_by_game[game_id].append(player_id)
      return [self._to_game(row, players_by_game[row[0]]) for row in game_rows]
    finally:
      await cursor.close()
