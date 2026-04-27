import aiomysql

from app.scoring.games_played import GamesPlayed, GamesPlayedSortBy

ORDER_BY_CLAUSE = {
  GamesPlayedSortBy.TOTAL: 'ORDER BY total DESC',
  GamesPlayedSortBy.MAXI: 'ORDER BY maxi DESC',
  GamesPlayedSortBy.MAXI_SEQUENTIAL: 'ORDER BY maxi_sequential DESC',
  GamesPlayedSortBy.YATZY: 'ORDER BY yatzy DESC',
  GamesPlayedSortBy.YATZY_SEQUENTIAL: 'ORDER BY yatzy_sequential DESC',
}


class GamesPlayedRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def list_top(self, sort_by: GamesPlayedSortBy) -> list[GamesPlayed]:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'SELECT p.id AS player_id, p.name AS player_name, '
        '  COUNT(*) AS total, '
        "  COUNT(CASE WHEN g.mode = 'maxi' THEN 1 END) AS maxi, "
        "  COUNT(CASE WHEN g.mode = 'maxi_sequential' THEN 1 END) AS maxi_sequential, "
        "  COUNT(CASE WHEN g.mode = 'yatzy' THEN 1 END) AS yatzy, "
        "  COUNT(CASE WHEN g.mode = 'yatzy_sequential' THEN 1 END) AS yatzy_sequential "
        'FROM games g '
        'JOIN game_players gp ON gp.game_id = g.id AND gp.deleted_at IS NULL '
        'JOIN players p ON p.id = gp.player_id AND p.deleted_at IS NULL '
        "WHERE g.status = 'finished' AND g.deleted_at IS NULL AND p.is_bot = FALSE "
        'GROUP BY p.id, p.name '
        + ORDER_BY_CLAUSE[sort_by]  # nosec B608
        + ' LIMIT 10'
      )
      rows = await cursor.fetchall()

    return [
      GamesPlayed(
        player_id=row['player_id'],
        player_name=row['player_name'],
        total=row['total'],
        maxi=row['maxi'],
        maxi_sequential=row['maxi_sequential'],
        yatzy=row['yatzy'],
        yatzy_sequential=row['yatzy_sequential'],
      )
      for row in rows
    ]
