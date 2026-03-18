import aiomysql
from app.score_category import ScoreCategory
from app.scorecard import ScoreEntry, Scorecard

UPPER_CATEGORIES = {
  ScoreCategory.ONES,
  ScoreCategory.TWOS,
  ScoreCategory.THREES,
  ScoreCategory.FOURS,
  ScoreCategory.FIVES,
  ScoreCategory.SIXES,
}
BONUS_THRESHOLD = 84
BONUS_SCORE = 100


class ScorecardRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  def _build_scorecard(self, rows: list[tuple]) -> Scorecard:
    scores = {row[0]: row[1] for row in rows}
    entries = [ScoreEntry(category=cat, score=scores.get(cat)) for cat in ScoreCategory]
    upper_total = sum(scores[cat] for cat in UPPER_CATEGORIES if cat in scores)
    bonus = BONUS_SCORE if upper_total >= BONUS_THRESHOLD else None
    total = sum(e.score for e in entries if e.score is not None)
    if bonus is not None:
      total += bonus
    return Scorecard(entries=entries, bonus=bonus, total=total)

  async def get(self, game_id: int, player_id: int) -> Scorecard | None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT id FROM games WHERE id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      if await cursor.fetchone() is None:
        return None
      await cursor.execute(
        'SELECT player_id FROM game_players '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (game_id, player_id),
      )
      if await cursor.fetchone() is None:
        return None
      await cursor.execute(
        'SELECT category, score FROM scorecard_entries '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (game_id, player_id),
      )
      rows = await cursor.fetchall()
    finally:
      await cursor.close()
    return self._build_scorecard(rows)
