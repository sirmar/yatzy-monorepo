import aiomysql
from app.games.game import Game
from yatzy_rules.game_mode import GameMode
from app.games.game_status import GameStatus


class GameRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  def _to_game(
    self, row: dict, player_ids: list[int], current_player_id: int | None = None
  ) -> Game:
    return Game(
      id=row['id'],
      status=row['status'],
      mode=row['mode'],
      creator_id=row['creator_id'],
      created_at=row['created_at'],
      started_at=row['started_at'],
      ended_at=row['ended_at'],
      player_ids=player_ids,
      current_player_id=current_player_id,
    )

  async def _fetch_game(self, cursor: aiomysql.DictCursor, game_id: int) -> Game:
    await cursor.execute(
      'SELECT g.id, g.status, g.mode, g.creator_id, g.created_at, g.started_at, g.ended_at, '
      't.player_id '
      'FROM games g LEFT JOIN turns t ON t.id = g.current_turn AND t.deleted_at IS NULL '
      'WHERE g.id = %s AND g.deleted_at IS NULL',
      (game_id,),
    )
    row = await cursor.fetchone()
    if row is None:
      raise RuntimeError(f'Expected game {game_id} to exist in _fetch_game')
    current_player_id = row['player_id']
    await cursor.execute(
      'SELECT player_id FROM game_players '
      'WHERE game_id = %s AND deleted_at IS NULL ORDER BY join_order',
      (game_id,),
    )
    player_rows = await cursor.fetchall()
    return self._to_game(row, [r['player_id'] for r in player_rows], current_player_id)

  async def create(self, creator_id: int, mode: GameMode = GameMode.MAXI) -> Game:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'INSERT INTO games (creator_id, mode) VALUES (%s, %s)',
        (creator_id, mode),
      )
      game_id = cursor.lastrowid
      await cursor.execute(
        'INSERT INTO game_players (game_id, player_id, join_order) VALUES (%s, %s, 1)',
        (game_id, creator_id),
      )
      return await self._fetch_game(cursor, game_id)

  async def abort(self, game_id: int) -> Game | None:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'UPDATE games SET status = %s, ended_at = NOW() '
        'WHERE id = %s AND status = %s AND deleted_at IS NULL',
        (GameStatus.ABANDONED, game_id, GameStatus.ACTIVE),
      )
      if cursor.rowcount == 0:
        return None
      return await self._fetch_game(cursor, game_id)

  async def end(self, game_id: int) -> Game | None:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'UPDATE games SET status = %s, ended_at = NOW() '
        'WHERE id = %s AND status = %s AND deleted_at IS NULL',
        (GameStatus.FINISHED, game_id, GameStatus.ACTIVE),
      )
      if cursor.rowcount == 0:
        return None
      return await self._fetch_game(cursor, game_id)

  async def start(self, game_id: int, turn_id: int) -> Game | None:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'UPDATE games SET status = %s, started_at = NOW(), current_turn = %s '
        'WHERE id = %s AND status = %s AND deleted_at IS NULL',
        (GameStatus.ACTIVE, turn_id, game_id, GameStatus.LOBBY),
      )
      if cursor.rowcount == 0:
        return None
      return await self._fetch_game(cursor, game_id)

  async def get_by_id(self, game_id: int) -> Game | None:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'SELECT id FROM games WHERE id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      if await cursor.fetchone() is None:
        return None
      return await self._fetch_game(cursor, game_id)

  async def soft_delete(self, game_id: int) -> bool:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'UPDATE games SET deleted_at = NOW() '
        'WHERE id = %s AND status IN (%s, %s, %s) AND deleted_at IS NULL',
        (game_id, GameStatus.LOBBY, GameStatus.FINISHED, GameStatus.ABANDONED),
      )
      return cursor.rowcount > 0

  async def set_current_turn(self, game_id: int, turn_id: int) -> None:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'UPDATE games SET current_turn = %s WHERE id = %s AND deleted_at IS NULL',
        (turn_id, game_id),
      )

  async def list_all(
    self, status: GameStatus | None = None, player_id: int | None = None
  ) -> list[Game]:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      query = (
        'SELECT g.id, g.status, g.mode, g.creator_id, g.created_at, g.started_at, g.ended_at, '
        't.player_id '
        'FROM games g LEFT JOIN turns t ON t.id = g.current_turn AND t.deleted_at IS NULL '
        'WHERE g.deleted_at IS NULL'
      )
      params: tuple = ()
      if status is not None:
        query += ' AND g.status = %s'
        params += (status,)
      if player_id is not None:
        query += ' AND EXISTS (SELECT 1 FROM game_players WHERE game_id = g.id AND player_id = %s AND deleted_at IS NULL)'
        params += (player_id,)
      query += ' ORDER BY g.id'
      await cursor.execute(query, params)
      game_rows = await cursor.fetchall()
      if not game_rows:
        return []
      game_ids = [row['id'] for row in game_rows]
      placeholders = ', '.join(['%s'] * len(game_ids))
      await cursor.execute(
        'SELECT game_id, player_id FROM game_players '
        'WHERE game_id IN ('
        + placeholders  # nosec B608
        + ') AND deleted_at IS NULL ORDER BY game_id, join_order',
        game_ids,
      )
      player_rows = await cursor.fetchall()
      players_by_game: dict[int, list[int]] = {row['id']: [] for row in game_rows}
      for player_row in player_rows:
        players_by_game[player_row['game_id']].append(player_row['player_id'])
      return [
        self._to_game(row, players_by_game[row['id']], row['player_id'])
        for row in game_rows
      ]

  async def add_player(self, game_id: int, player_id: int, join_order: int) -> None:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'INSERT INTO game_players (game_id, player_id, join_order) VALUES (%s, %s, %s) AS new '
        'ON DUPLICATE KEY UPDATE deleted_at = NULL, join_order = new.join_order',
        (game_id, player_id, join_order),
      )

  async def remove_player(self, game_id: int, player_id: int) -> None:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'UPDATE game_players SET deleted_at = NOW() '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (game_id, player_id),
      )

  async def update_saved_rolls(self, game_id: int, player_id: int, value: int) -> None:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'UPDATE game_players SET saved_rolls = %s '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (value, game_id, player_id),
      )
