import aiomysql


class TurnRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def get_turn_number(self, turn_id: int) -> int:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT turn_number FROM turns WHERE id = %s AND deleted_at IS NULL',
        (turn_id,),
      )
      row = await cursor.fetchone()
      return row[0]
    finally:
      await cursor.close()

  async def create(self, game_id: int, player_id: int, turn_number: int) -> int:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'INSERT INTO turns (game_id, player_id, turn_number) VALUES (%s, %s, %s)',
        (game_id, player_id, turn_number),
      )
      turn_id = cursor.lastrowid
      placeholders = ', '.join(['(%s, %s)'] * 6)
      values = [v for i in range(6) for v in (turn_id, i)]
      await cursor.execute(
        'INSERT INTO turn_dice (turn_id, die_index) VALUES ' + placeholders,  # nosec B608
        values,
      )
      return turn_id
    finally:
      await cursor.close()
