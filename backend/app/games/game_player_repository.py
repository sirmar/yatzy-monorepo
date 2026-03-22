import aiomysql


class GamePlayerRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def update_saved_rolls(self, game_id: int, player_id: int, value: int) -> None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE game_players SET saved_rolls = %s '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (value, game_id, player_id),
      )

  async def remove(self, game_id: int, player_id: int) -> None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE game_players SET deleted_at = NOW() '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (game_id, player_id),
      )

  async def add(self, game_id: int, player_id: int, join_order: int) -> None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'INSERT INTO game_players (game_id, player_id, join_order) VALUES (%s, %s, %s) '
        'ON DUPLICATE KEY UPDATE deleted_at = NULL, join_order = VALUES(join_order)',
        (game_id, player_id, join_order),
      )
