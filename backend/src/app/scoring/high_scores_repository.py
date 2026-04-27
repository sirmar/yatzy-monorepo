from collections import defaultdict
import aiomysql
from yatzy_rules.game_mode import GameMode
from yatzy_rules.game_variant import get_variant
from app.scoring.high_score import HighScore
from app.scoring.scoring_rules import calculate_bonus


class HighScoresRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def list_all(self) -> list[HighScore]:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'SELECT p.id AS player_id, p.name AS player_name, g.id AS game_id, g.ended_at, g.mode, se.category, se.score '
        'FROM games g '
        'JOIN game_players gp ON gp.game_id = g.id AND gp.deleted_at IS NULL '
        'JOIN players p ON p.id = gp.player_id AND p.deleted_at IS NULL '
        'LEFT JOIN scorecard_entries se '
        '  ON se.game_id = g.id AND se.player_id = p.id AND se.deleted_at IS NULL '
        "WHERE g.status = 'finished' AND g.deleted_at IS NULL AND p.is_bot = FALSE"
      )
      rows = await cursor.fetchall()

    entries: dict[tuple[int, int], dict] = defaultdict(
      lambda: {'player_name': '', 'finished_at': None, 'mode': None, 'scores': {}}
    )
    for row in rows:
      key = (row['player_id'], row['game_id'])
      entries[key]['player_name'] = row['player_name']
      entries[key]['finished_at'] = row['ended_at']
      entries[key]['mode'] = row['mode']
      if row['category'] is not None and row['score'] is not None:
        entries[key]['scores'][row['category']] = row['score']

    result = []
    for (player_id, game_id), data in entries.items():
      scores = data['scores']
      base = sum(scores.values())
      variant = get_variant(GameMode(data['mode']))
      bonus = calculate_bonus(scores, variant.bonus_threshold, variant.bonus_score)
      result.append(
        HighScore(
          player_id=player_id,
          player_name=data['player_name'],
          game_id=game_id,
          finished_at=data['finished_at'],
          total_score=base + bonus,
          mode=data['mode'],
        )
      )

    result.sort(key=lambda h: h.total_score, reverse=True)
    return result
