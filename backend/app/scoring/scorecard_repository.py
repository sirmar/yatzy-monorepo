import aiomysql
from app.scoring.score_category import ScoreCategory
from app.scoring.scorecard import PlayerScorecard, ScoreEntry, Scorecard
from app.scoring.scoring_rules import BONUS_SCORE, BONUS_THRESHOLD, UPPER_CATEGORIES


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

  async def is_category_scored(
    self, game_id: int, player_id: int, category: ScoreCategory
  ) -> bool:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT id FROM scorecard_entries '
        'WHERE game_id = %s AND player_id = %s AND category = %s AND deleted_at IS NULL',
        (game_id, player_id, category),
      )
      return await cursor.fetchone() is not None
    finally:
      await cursor.close()

  async def save(
    self, game_id: int, player_id: int, category: ScoreCategory, score: int
  ) -> None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'INSERT INTO scorecard_entries (game_id, player_id, category, score) '
        'VALUES (%s, %s, %s, %s)',
        (game_id, player_id, category, score),
      )
    finally:
      await cursor.close()

  async def count_all_scored(self, game_id: int) -> int:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT COUNT(*) FROM scorecard_entries '
        'WHERE game_id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      row = await cursor.fetchone()
      return row[0]
    finally:
      await cursor.close()

  async def get_scored_categories(
    self, game_id: int, player_id: int
  ) -> set[ScoreCategory]:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT category FROM scorecard_entries '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (game_id, player_id),
      )
      rows = await cursor.fetchall()
      return {ScoreCategory(row[0]) for row in rows}
    finally:
      await cursor.close()

  async def get_all(self, game_id: int) -> list[PlayerScorecard]:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT player_id FROM game_players WHERE game_id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      player_rows = await cursor.fetchall()
      player_ids = [r[0] for r in player_rows]
      if not player_ids:
        return []
      await cursor.execute(
        'SELECT player_id, category, score FROM scorecard_entries '
        'WHERE game_id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      entry_rows = await cursor.fetchall()
      entries_by_player: dict[int, list[tuple]] = {pid: [] for pid in player_ids}
      for pid, cat, score in entry_rows:
        if pid in entries_by_player:
          entries_by_player[pid].append((cat, score))
      result = []
      for pid in player_ids:
        sc = self._build_scorecard(entries_by_player[pid])
        result.append(
          PlayerScorecard(
            player_id=pid, entries=sc.entries, bonus=sc.bonus, total=sc.total
          )
        )
      return result
    finally:
      await cursor.close()

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
      return self._build_scorecard(rows)
    finally:
      await cursor.close()
