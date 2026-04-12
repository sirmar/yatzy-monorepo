from collections import defaultdict
import aiomysql
from yatzy_rules.game_mode import GameMode
from yatzy_rules.game_variant import get_variant
from app.players.player_stats import ModeStats, PlayerStats


def _compute_mode_stats(game_rows: list[tuple]) -> ModeStats:
  high_score: int | None = None
  total_score_sum = 0
  bonus_count = 0
  yatzy_hit_count = 0

  for mode, base_score, upper_score, yatzy_hit in game_rows:
    variant = get_variant(GameMode(mode))
    bonus = variant.bonus_score if (upper_score or 0) >= variant.bonus_threshold else 0
    total = (base_score or 0) + bonus
    total_score_sum += total
    high_score = max(high_score, total) if high_score is not None else total
    if bonus > 0:
      bonus_count += 1
    yatzy_hit_count += yatzy_hit or 0

  games_played = len(game_rows)
  average_score = round(total_score_sum / games_played) if games_played > 0 else None
  return ModeStats(
    games_played=games_played,
    high_score=high_score,
    average_score=average_score,
    bonus_count=bonus_count,
    yatzy_hit_count=yatzy_hit_count,
  )


class PlayerStatsRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def get(self, player_id: int) -> PlayerStats | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT id, name, created_at FROM players WHERE id = %s AND deleted_at IS NULL',
        (player_id,),
      )
      row = await cursor.fetchone()
      if row is None:
        return None
      pid, name, created_at = row

      await cursor.execute(
        'SELECT '
        '  g.mode, '
        '  SUM(se.score) AS base_score, '
        '  SUM(CASE WHEN se.category IN '
        "    ('ones','twos','threes','fours','fives','sixes') "
        '    THEN se.score ELSE 0 END) AS upper_score, '
        '  SUM(CASE WHEN se.category IN '
        "    ('maxi_yatzy','yatzy') AND se.score > 0 THEN 1 ELSE 0 END) AS yatzy_hit "
        'FROM games g '
        'JOIN scorecard_entries se ON se.game_id = g.id AND se.player_id = %s AND se.deleted_at IS NULL '
        "WHERE g.status = 'finished' AND g.deleted_at IS NULL "
        'GROUP BY g.id, g.mode',
        (player_id,),
      )
      game_rows = await cursor.fetchall()

    by_mode: dict[str, list[tuple]] = defaultdict(list)
    for row in game_rows:
      by_mode[row[0]].append(row)

    return PlayerStats(
      player_id=pid,
      player_name=name,
      member_since=created_at,
      total_games_played=len(game_rows),
      maxi=_compute_mode_stats(by_mode[GameMode.MAXI]),
      maxi_sequential=_compute_mode_stats(by_mode[GameMode.MAXI_SEQUENTIAL]),
      yatzy=_compute_mode_stats(by_mode[GameMode.YATZY]),
      yatzy_sequential=_compute_mode_stats(by_mode[GameMode.YATZY_SEQUENTIAL]),
    )
