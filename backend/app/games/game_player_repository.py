import aiomysql


class GamePlayerRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def update_rolls_remaining(
    self, game_id: int, player_id: int, value: int
  ) -> None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'UPDATE game_players SET rolls_remaining = %s '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (value, game_id, player_id),
      )
    finally:
      await cursor.close()

  async def add(self, game_id: int, player_id: int, join_order: int) -> None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'INSERT INTO game_players (game_id, player_id, join_order) VALUES (%s, %s, %s)',
        (game_id, player_id, join_order),
      )
    finally:
      await cursor.close()
