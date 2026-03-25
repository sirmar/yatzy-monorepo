import aiomysql
from app.players.player_stats import PlayerStats
from app.scoring.scoring_rules import BONUS_THRESHOLD, BONUS_SCORE


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
        '  SUM(se.score) AS base_score, '
        '  SUM(CASE WHEN se.category IN '
        "    ('ones','twos','threes','fours','fives','sixes') "
        '    THEN se.score ELSE 0 END) AS upper_score, '
        "  SUM(CASE WHEN se.category = 'maxi_yatzy' AND se.score > 0 THEN 1 ELSE 0 END) AS yatzy_hit "
        'FROM games g '
        'JOIN scorecard_entries se ON se.game_id = g.id AND se.player_id = %s AND se.deleted_at IS NULL '
        "WHERE g.status = 'finished' AND g.deleted_at IS NULL "
        'GROUP BY se.game_id',
        (player_id,),
      )
      game_rows = await cursor.fetchall()

    games_played = len(game_rows)
    high_score: int | None = None
    average_score: int | None = None
    bonus_count = 0
    maxi_yatzy_count = 0
    total_score_sum = 0

    for base_score, upper_score, yatzy_hit in game_rows:
      bonus = BONUS_SCORE if (upper_score or 0) >= BONUS_THRESHOLD else 0
      total = (base_score or 0) + bonus
      total_score_sum += total
      high_score = max(high_score, total) if high_score is not None else total
      if bonus > 0:
        bonus_count += 1
      maxi_yatzy_count += yatzy_hit or 0

    if games_played > 0:
      average_score = round(total_score_sum / games_played)

    return PlayerStats(
      player_id=pid,
      player_name=name,
      member_since=created_at,
      games_played=games_played,
      high_score=high_score,
      average_score=average_score,
      bonus_count=bonus_count,
      maxi_yatzy_count=maxi_yatzy_count,
    )
