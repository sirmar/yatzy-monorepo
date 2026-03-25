from collections import defaultdict
import aiomysql
from app.scoring.high_score import HighScore
from app.scoring.scoring_rules import calculate_bonus


class HighScoresRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def list_all(self) -> list[HighScore]:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT p.id, p.name, g.id, g.ended_at, se.category, se.score '
        'FROM games g '
        'JOIN game_players gp ON gp.game_id = g.id AND gp.deleted_at IS NULL '
        'JOIN players p ON p.id = gp.player_id AND p.deleted_at IS NULL '
        'LEFT JOIN scorecard_entries se '
        '  ON se.game_id = g.id AND se.player_id = p.id AND se.deleted_at IS NULL '
        "WHERE g.status = 'finished' AND g.deleted_at IS NULL"
      )
      rows = await cursor.fetchall()

    entries: dict[tuple[int, int], dict] = defaultdict(
      lambda: {'player_name': '', 'finished_at': None, 'scores': {}}
    )
    for player_id, player_name, game_id, ended_at, category, score in rows:
      key = (player_id, game_id)
      entries[key]['player_name'] = player_name
      entries[key]['finished_at'] = ended_at
      if category is not None and score is not None:
        entries[key]['scores'][category] = score

    result = []
    for (player_id, game_id), data in entries.items():
      scores = data['scores']
      base = sum(scores.values())
      bonus = calculate_bonus(scores)
      result.append(
        HighScore(
          player_id=player_id,
          player_name=data['player_name'],
          game_id=game_id,
          finished_at=data['finished_at'],
          total_score=base + bonus,
        )
      )

    result.sort(key=lambda h: h.total_score, reverse=True)
    return result
