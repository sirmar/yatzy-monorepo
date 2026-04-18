import asyncio
from app.bot_client import get_action
from app.config import Settings
from app.database import Database
from app.events import EventBus
from app.games.game_player_repository import GamePlayerRepository
from app.games.game_repository import GameRepository
from app.games.roll_repository import RollRepository
from app.games.turn_repository import TurnRepository
from app.players.player_repository import PlayerRepository
from app.scoring.score_calculator import calculate
from app.scoring.scorecard_repository import ScorecardRepository
from yatzy_rules.game_variant import get_variant


async def play_bot_turn(
  game_id: int,
  player_id: int,
  database: Database,
  settings: Settings,
  event_bus: EventBus,
) -> None:
  async with database._pool.acquire() as conn:  # type: ignore[union-attr]
    await _play_turn(game_id, player_id, conn, settings, event_bus)


async def _play_turn(game_id, player_id, conn, settings, event_bus):
  game_repo = GameRepository(conn)
  roll_repo = RollRepository(conn)
  scorecard_repo = ScorecardRepository(conn)
  turn_repo = TurnRepository(conn)
  gp_repo = GamePlayerRepository(conn)

  game = await game_repo.get_by_id(game_id)
  if not game:
    return
  variant = get_variant(game.mode)

  while True:
    turn_info = await roll_repo.get_turn_info(game_id)
    if not turn_info:
      return
    turn_id, current_player_id, rolls_remaining, saved_rolls = turn_info
    if current_player_id != player_id:
      return

    dice = await roll_repo.get_dice(turn_id)
    scores = await scorecard_repo.get_scores_dict(game_id, player_id)
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
      await roll_repo.execute(
        turn_id, game_id, player_id, rolls_remaining, kept_indices
      )
      event_bus.publish_game(game_id)
    else:
      await asyncio.sleep(4.0)
      category = response['category']
      dice_values = await roll_repo.get_dice_values(turn_id)
      score = calculate(category, dice_values)
      await scorecard_repo.save(game_id, player_id, category, score)

      new_saved = (saved_rolls + rolls_remaining) if variant.saves_rolls else 0
      await gp_repo.update_saved_rolls(game_id, player_id, new_saved)

      total_scored = await scorecard_repo.count_all_scored(game_id)
      game_ended = total_scored >= len(game.player_ids) * len(variant.categories)

      if game_ended:
        await game_repo.end(game_id)
        event_bus.publish_game(game_id)
        event_bus.publish_player(game.player_ids)
      else:
        current_index = game.player_ids.index(player_id)
        next_player_id = game.player_ids[(current_index + 1) % len(game.player_ids)]
        turn_number = await turn_repo.get_turn_number(turn_id)
        new_turn_id = await turn_repo.create(
          game_id, next_player_id, turn_number + 1, variant.dice_count
        )
        await game_repo.set_current_turn(game_id, new_turn_id)
        event_bus.publish_game(game_id)

        next_player = await PlayerRepository(conn).get_by_id(next_player_id)
        if next_player and next_player.is_bot:
          await _play_turn(game_id, next_player_id, conn, settings, event_bus)
      break
