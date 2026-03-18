import aiomysql
from app.die import Die
from app.game_state import GameState


class GameStateRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def get(self, game_id: int) -> GameState | None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT status, current_turn FROM games WHERE id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      row = await cursor.fetchone()
      if row is None:
        return None
      status, current_turn = row
      if current_turn is None:
        return GameState(status=status)
      await cursor.execute(
        'SELECT player_id FROM turns WHERE id = %s AND deleted_at IS NULL',
        (current_turn,),
      )
      turn_row = await cursor.fetchone()
      await cursor.execute(
        'SELECT die_index, value, kept FROM turn_dice WHERE turn_id = %s ORDER BY die_index',
        (current_turn,),
      )
      dice_rows = await cursor.fetchall()
      dice = [Die(index=r[0], value=r[1], kept=bool(r[2])) for r in dice_rows]
      return GameState(status=status, current_player_id=turn_row[0], dice=dice)
    finally:
      await cursor.close()
