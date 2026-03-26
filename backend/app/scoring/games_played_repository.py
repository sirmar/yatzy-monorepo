import aiomysql

from app.scoring.games_played import GamesPlayed, GamesPlayedSortBy

ORDER_BY_CLAUSE = {
  GamesPlayedSortBy.TOTAL: 'ORDER BY total DESC',
  GamesPlayedSortBy.STANDARD: 'ORDER BY standard DESC',
  GamesPlayedSortBy.SEQUENTIAL: 'ORDER BY sequential DESC',
}


class GamesPlayedRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def list_top(self, sort_by: GamesPlayedSortBy) -> list[GamesPlayed]:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT p.id, p.name, '
        '  COUNT(*) AS total, '
        "  COUNT(CASE WHEN g.mode = 'standard' THEN 1 END) AS standard, "
        "  COUNT(CASE WHEN g.mode = 'sequential' THEN 1 END) AS sequential "
        'FROM games g '
        'JOIN game_players gp ON gp.game_id = g.id AND gp.deleted_at IS NULL '
        'JOIN players p ON p.id = gp.player_id AND p.deleted_at IS NULL '
        "WHERE g.status = 'finished' AND g.deleted_at IS NULL "
        'GROUP BY p.id, p.name '
        + ORDER_BY_CLAUSE[sort_by]  # nosec B608
        + ' LIMIT 10'
      )
      rows = await cursor.fetchall()

    return [
      GamesPlayed(
        player_id=player_id,
        player_name=player_name,
        total=total,
        standard=standard,
        sequential=sequential,
      )
      for player_id, player_name, total, standard, sequential in rows
    ]
