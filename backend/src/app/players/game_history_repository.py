from collections import defaultdict
import aiomysql
from yatzy_rules.game_mode import GameMode
from yatzy_rules.game_variant import get_variant
from app.players.game_history import GameHistory, GameHistoryPlayer
from app.scoring.scoring_rules import calculate_bonus


class GameHistoryRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def list_for_player(self, player_id: int) -> list[GameHistory]:
    async with await self._conn.cursor(aiomysql.DictCursor) as cursor:
      await cursor.execute(
        'SELECT g.id AS game_id, g.mode, g.ended_at, p.id AS pid, p.name, p.is_bot, se.category, se.score '
        'FROM games g '
        'JOIN game_players gp_me ON gp_me.game_id = g.id AND gp_me.player_id = %s AND gp_me.deleted_at IS NULL '
        'JOIN game_players gp ON gp.game_id = g.id AND gp.deleted_at IS NULL '
        'JOIN players p ON p.id = gp.player_id AND p.deleted_at IS NULL '
        'LEFT JOIN scorecard_entries se ON se.game_id = g.id AND se.player_id = p.id AND se.deleted_at IS NULL '
        "WHERE g.status = 'finished' AND g.deleted_at IS NULL",
        (player_id,),
      )
      rows = await cursor.fetchall()

    games: dict[int, dict] = defaultdict(
      lambda: {
        'mode': None,
        'ended_at': None,
        'players': defaultdict(lambda: {'name': '', 'is_bot': False, 'scores': {}}),
      }
    )
    for row in rows:
      game_id = row['game_id']
      pid = row['pid']
      games[game_id]['mode'] = row['mode']
      games[game_id]['ended_at'] = row['ended_at']
      games[game_id]['players'][pid]['name'] = row['name']
      games[game_id]['players'][pid]['is_bot'] = row['is_bot']
      if row['category'] is not None and row['score'] is not None:
        games[game_id]['players'][pid]['scores'][row['category']] = row['score']

    result = []
    for game_id, game_data in games.items():
      variant = get_variant(GameMode(game_data['mode']))
      all_with_scores = []
      for pid, pdata in game_data['players'].items():
        base = sum(pdata['scores'].values())
        bonus = calculate_bonus(
          pdata['scores'], variant.bonus_threshold, variant.bonus_score
        )
        all_with_scores.append((pid, pdata['name'], pdata['is_bot'], base + bonus))

      all_with_scores.sort(key=lambda x: x[3], reverse=True)
      rank = next(
        (i + 1 for i, (pid, _, _, _) in enumerate(all_with_scores) if pid == player_id),
        0,
      )

      result.append(
        GameHistory(
          game_id=game_id,
          mode=game_data['mode'],
          finished_at=game_data['ended_at'],
          score=next((s for pid, _, _, s in all_with_scores if pid == player_id), 0),
          rank=rank,
          players=[
            GameHistoryPlayer(player_id=pid, player_name=name, score=score)
            for pid, name, is_bot, score in all_with_scores
          ],
        )
      )

    result.sort(key=lambda h: h.finished_at, reverse=True)
    return result
