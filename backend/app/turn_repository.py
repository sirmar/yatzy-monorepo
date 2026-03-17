import aiomysql


class TurnRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def create(self, game_id: int, player_id: int, turn_number: int) -> int:
    cursor = await self._conn.cursor()
    await cursor.execute(
      'INSERT INTO turns (game_id, player_id, turn_number) VALUES (%s, %s, %s)',
      (game_id, player_id, turn_number),
    )
    turn_id = cursor.lastrowid
    for die_index in range(6):
      await cursor.execute(
        'INSERT INTO turn_dice (turn_id, die_index) VALUES (%s, %s)',
        (turn_id, die_index),
      )
    await cursor.close()
    return turn_id
