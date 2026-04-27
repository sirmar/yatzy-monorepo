import aiomysql


class TurnRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def get_turn_number(self, turn_id: int) -> int:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'SELECT turn_number FROM turns WHERE id = %s AND deleted_at IS NULL',
        (turn_id,),
      )
      row = await cursor.fetchone()
      if row is None:
        raise RuntimeError(f'Turn {turn_id} not found')
      return row['turn_number']

  async def create(
    self, game_id: int, player_id: int, turn_number: int, dice_count: int = 6
  ) -> int:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'INSERT INTO turns (game_id, player_id, turn_number) VALUES (%s, %s, %s)',
        (game_id, player_id, turn_number),
      )
      turn_id = cursor.lastrowid
      placeholders = ', '.join(['(%s, %s)'] * dice_count)
      values = [v for i in range(dice_count) for v in (turn_id, i)]
      await cursor.execute(
        'INSERT INTO turn_dice (turn_id, die_index) VALUES ' + placeholders,  # nosec B608
        values,
      )
      return turn_id
