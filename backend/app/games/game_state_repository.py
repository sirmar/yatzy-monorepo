import aiomysql
from app.games.dice import Die
from yatzy_rules.game_mode import GameMode
from app.games.game_state import GameState, PlayerScore
from app.games.game_status import GameStatus
from yatzy_rules.game_variant import get_variant
from app.scoring.scoring_rules import calculate_bonus


class GameStateRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def get(self, game_id: int) -> GameState | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT status, mode, current_turn FROM games WHERE id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      row = await cursor.fetchone()
      if row is None:
        return None
      status, mode, current_turn = row
      if status == GameStatus.FINISHED:
        await cursor.execute(
          'SELECT player_id FROM game_players WHERE game_id = %s AND deleted_at IS NULL',
          (game_id,),
        )
        player_rows = await cursor.fetchall()
        player_ids = [r[0] for r in player_rows]
        await cursor.execute(
          'SELECT player_id, category, score FROM scorecard_entries '
          'WHERE game_id = %s AND deleted_at IS NULL',
          (game_id,),
        )
        entry_rows = await cursor.fetchall()
        entries_by_player: dict[int, list[tuple]] = {pid: [] for pid in player_ids}
        for entry_pid, cat, score in entry_rows:
          if entry_pid in entries_by_player:
            entries_by_player[entry_pid].append((cat, score))
        variant = get_variant(GameMode(mode))
        final_scores = []
        for pid in player_ids:
          scores = {r[0]: r[1] for r in entries_by_player[pid]}
          bonus = calculate_bonus(
            scores,
            bonus_threshold=variant.bonus_threshold,
            bonus_score=variant.bonus_score,
          )
          total = sum(scores.values()) + bonus
          final_scores.append(PlayerScore(player_id=pid, total=total))
        max_total = max((ps.total for ps in final_scores), default=0)
        winner_ids = [ps.player_id for ps in final_scores if ps.total == max_total]
        return GameState(
          status=status, mode=mode, winner_ids=winner_ids, final_scores=final_scores
        )
      if status != GameStatus.ACTIVE or current_turn is None:
        return GameState(status=status, mode=mode)
      await cursor.execute(
        'SELECT t.player_id, t.rolls_remaining, gp.saved_rolls '
        'FROM turns t '
        'JOIN game_players gp ON t.player_id = gp.player_id AND gp.game_id = %s '
        'WHERE t.id = %s AND t.deleted_at IS NULL AND gp.deleted_at IS NULL',
        (game_id, current_turn),
      )
      turn_row = await cursor.fetchone()
      await cursor.execute(
        'SELECT die_index, value, kept FROM turn_dice WHERE turn_id = %s ORDER BY die_index',
        (current_turn,),
      )
      dice_rows = await cursor.fetchall()
      dice = [Die(index=r[0], value=r[1], kept=bool(r[2])) for r in dice_rows]
      return GameState(
        status=status,
        mode=mode,
        current_player_id=turn_row[0],
        dice=dice,
        rolls_remaining=turn_row[1],
        saved_rolls=turn_row[2],
      )
