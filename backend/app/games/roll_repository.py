import random
import aiomysql
from app.games.dice import Die


class RollRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def get_turn_info(self, game_id: int) -> tuple[int, int, int, int] | None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT t.id, t.player_id, t.rolls_used, gp.rolls_remaining '
        'FROM games g '
        'JOIN turns t ON g.current_turn = t.id '
        'JOIN game_players gp ON g.id = gp.game_id AND t.player_id = gp.player_id '
        'WHERE g.id = %s AND g.deleted_at IS NULL',
        (game_id,),
      )
      return await cursor.fetchone()
    finally:
      await cursor.close()

  async def get_dice_values(self, turn_id: int) -> list[int]:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT value FROM turn_dice WHERE turn_id = %s ORDER BY die_index',
        (turn_id,),
      )
      rows = await cursor.fetchall()
      return [r[0] for r in rows]
    finally:
      await cursor.close()

  async def execute(self, turn_id: int, kept_dice: list[int]) -> list[Die]:
    cursor = await self._conn.cursor()
    try:
      kept_set = set(kept_dice)
      if kept_set:
        kept_indices = sorted(kept_set)
        placeholders = ', '.join(['%s'] * len(kept_indices))
        await cursor.execute(
          f'UPDATE turn_dice SET kept = TRUE WHERE turn_id = %s AND die_index IN ({placeholders})',  # nosec B608
          (turn_id, *kept_indices),
        )
      reroll_indices = sorted(i for i in range(6) if i not in kept_set)
      for idx in reroll_indices:
        value = random.randint(1, 6)
        await cursor.execute(
          'UPDATE turn_dice SET value = %s, kept = FALSE WHERE turn_id = %s AND die_index = %s',
          (value, turn_id, idx),
        )
      await cursor.execute(
        'UPDATE turns SET rolls_used = rolls_used + 1 WHERE id = %s',
        (turn_id,),
      )
      await cursor.execute(
        'SELECT die_index, value, kept FROM turn_dice WHERE turn_id = %s ORDER BY die_index',
        (turn_id,),
      )
      rows = await cursor.fetchall()
      return [Die(index=r[0], value=r[1], kept=bool(r[2])) for r in rows]
    finally:
      await cursor.close()
