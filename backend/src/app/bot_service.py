import asyncio
from app.bot_client import get_action
from app.config import Settings
from app.database import Database
from app.events import EventBus
from app.games.game_repository import GameRepository
from app.games.turn_repository import TurnRepository
from app.games.turn_service import TurnService
from app.players.player_repository import PlayerRepository
from app.scoring.scorecard_repository import ScorecardRepository
from yatzy_rules.score_category import ScoreCategory


async def play_bot_turn(
  game_id: int,
  player_id: int,
  database: Database,
  settings: Settings,
  event_bus: EventBus,
) -> None:
  if database._pool is None:
    raise RuntimeError('Database.connect() must be called before play_bot_turn()')
  async with database._pool.acquire() as conn:
    await _play_turn(game_id, player_id, conn, settings, event_bus)


async def _play_turn(game_id, player_id, conn, settings, event_bus):
  game = await GameRepository(conn).get_by_id(game_id)
  if not game:
    return

  while True:
    turn_repo = TurnRepository(conn)
    turn_info = await turn_repo.get_turn_info(game_id)
    if not turn_info:
      return
    turn_id, current_player_id, rolls_remaining, saved_rolls = turn_info
    if current_player_id != player_id:
      return

    dice = await turn_repo.get_dice(turn_id)
    scores = await ScorecardRepository(conn).get_scores_dict(game_id, player_id)
    has_rolled = any(d.value is not None for d in dice)

    payload = {
      'game_mode': game.mode,
      'dice': [d.value or 0 for d in dice],
      'kept': [d.kept for d in dice],
      'rolls_remaining': rolls_remaining,
      'saved_rolls': saved_rolls,
      'has_rolled': has_rolled,
      'scores': scores,
    }

    response = await get_action(settings.bot_url, payload)

    if response['action'] == 'roll':
      await asyncio.sleep(1.0 if not has_rolled else 2.0)
      kept_indices = [i for i, k in enumerate(response['keep']) if k]
      await turn_repo.execute(
        turn_id, game_id, player_id, rolls_remaining, kept_indices
      )
      await conn.commit()
      event_bus.publish_game(game_id)
    else:
      await asyncio.sleep(4.0)
      result = await TurnService(conn).score_and_advance(
        game_id, player_id, ScoreCategory(response['category'])
      )
      await conn.commit()
      event_bus.publish_game(game_id)
      event_bus.publish_player(result.player_ids)
      if not result.game_ended and result.next_player_id is not None:
        next_player = await PlayerRepository(conn).get_by_id(result.next_player_id)
        if next_player and next_player.is_bot:
          await _play_turn(game_id, result.next_player_id, conn, settings, event_bus)
      break
