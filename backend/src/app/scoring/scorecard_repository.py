import aiomysql
from yatzy_rules.game_variant import GameVariant
from yatzy_rules.score_category import ScoreCategory
from app.scoring.scorecard import PlayerScorecard, ScoreEntry, Scorecard
from app.scoring.scoring_rules import calculate_bonus


class ScorecardRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  def _build_scorecard(
    self, scores: dict[str, int], variant: GameVariant, last_category: str | None = None
  ) -> Scorecard:
    entries = [
      ScoreEntry(
        category=cat, score=scores.get(cat), last_scored=(cat == last_category)
      )
      for cat in variant.categories
    ]
    bonus_value = calculate_bonus(scores, variant.bonus_threshold, variant.bonus_score)
    bonus = bonus_value if bonus_value > 0 else None
    total = sum(e.score for e in entries if e.score is not None) + bonus_value
    return Scorecard(entries=entries, bonus=bonus, total=total)

  async def is_category_scored(
    self, game_id: int, player_id: int, category: ScoreCategory
  ) -> bool:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'SELECT id FROM scorecard_entries '
        'WHERE game_id = %s AND player_id = %s AND category = %s AND deleted_at IS NULL',
        (game_id, player_id, category),
      )
      return await cursor.fetchone() is not None

  async def save(
    self, game_id: int, player_id: int, category: ScoreCategory, score: int
  ) -> None:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'INSERT INTO scorecard_entries (game_id, player_id, category, score) '
        'VALUES (%s, %s, %s, %s)',
        (game_id, player_id, category, score),
      )

  async def count_all_scored(self, game_id: int) -> int:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'SELECT COUNT(*) AS cnt FROM scorecard_entries '
        'WHERE game_id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      row = await cursor.fetchone()
      return row['cnt']

  async def get_scores_dict(self, game_id: int, player_id: int) -> dict[str, int]:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'SELECT category, score FROM scorecard_entries '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (game_id, player_id),
      )
      rows = await cursor.fetchall()
      return {row['category']: row['score'] for row in rows}

  async def get_scored_categories(
    self, game_id: int, player_id: int
  ) -> set[ScoreCategory]:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'SELECT category FROM scorecard_entries '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (game_id, player_id),
      )
      rows = await cursor.fetchall()
      return {ScoreCategory(row['category']) for row in rows}

  async def get_all(self, game_id: int, variant: GameVariant) -> list[PlayerScorecard]:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'SELECT player_id FROM game_players WHERE game_id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      player_rows = await cursor.fetchall()
      player_ids = [r['player_id'] for r in player_rows]
      if not player_ids:
        return []
      await cursor.execute(
        'SELECT player_id, category, score, id FROM scorecard_entries '
        'WHERE game_id = %s AND deleted_at IS NULL',
        (game_id,),
      )
      entry_rows = await cursor.fetchall()
      scores_by_player: dict[int, dict[str, int]] = {pid: {} for pid in player_ids}
      last_id_by_player: dict[int, tuple[int, str]] = {}
      for row in entry_rows:
        pid = row['player_id']
        if pid in scores_by_player:
          scores_by_player[pid][row['category']] = row['score']
          if pid not in last_id_by_player or row['id'] > last_id_by_player[pid][0]:
            last_id_by_player[pid] = (row['id'], row['category'])
      result = []
      for pid in player_ids:
        last_cat = last_id_by_player[pid][1] if pid in last_id_by_player else None
        sc = self._build_scorecard(scores_by_player[pid], variant, last_cat)
        result.append(
          PlayerScorecard(
            player_id=pid, entries=sc.entries, bonus=sc.bonus, total=sc.total
          )
        )
      return result

  async def get(
    self, game_id: int, player_id: int, variant: GameVariant
  ) -> Scorecard | None:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
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
        'SELECT category, score, id FROM scorecard_entries '
        'WHERE game_id = %s AND player_id = %s AND deleted_at IS NULL',
        (game_id, player_id),
      )
      rows = await cursor.fetchall()
      last_cat = max(rows, key=lambda r: r['id'])['category'] if rows else None
      scores = {row['category']: row['score'] for row in rows}
      return self._build_scorecard(scores, variant, last_cat)
