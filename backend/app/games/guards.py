from fastapi import HTTPException
from app.games.game import Game
from app.games.game_status import GameStatus
from app.players.player import Player
from app.scoring.score_category import ScoreCategory

BASE_ROLLS_PER_TURN = 3


def assert_game_exists(game: Game | None) -> Game:
  if game is None:
    raise HTTPException(status_code=404, detail='Game not found')
  return game


def assert_game_active(game: Game) -> None:
  if game.status != GameStatus.ACTIVE:
    raise HTTPException(status_code=409, detail='Game is not active')


def assert_game_in_lobby(game: Game) -> None:
  if game.status != GameStatus.LOBBY:
    raise HTTPException(status_code=409, detail='Game is not in lobby')


def assert_game_deletable(game: Game) -> None:
  if game.status == GameStatus.ACTIVE:
    raise HTTPException(status_code=409, detail='Cannot delete an active game')


def assert_player_in_game(game: Game, player_id: int) -> None:
  if player_id not in game.player_ids:
    raise HTTPException(status_code=404, detail='Player not in game')


def assert_player_not_in_game(game: Game, player_id: int) -> None:
  if player_id in game.player_ids:
    raise HTTPException(status_code=409, detail='Player already in game')


def assert_game_not_full(game: Game) -> None:
  if len(game.player_ids) >= 6:
    raise HTTPException(status_code=409, detail='Game is full')


def assert_is_creator(game: Game, player_id: int) -> None:
  if player_id != game.creator_id:
    raise HTTPException(status_code=403, detail='Only the creator can start the game')


def assert_not_creator(game: Game, player_id: int) -> None:
  if player_id == game.creator_id:
    raise HTTPException(
      status_code=403, detail='Creator cannot leave — delete the game instead'
    )


def assert_turn_active(
  turn_info: tuple[int, int, int, int] | None,
) -> tuple[int, int, int, int]:
  if turn_info is None:
    raise HTTPException(status_code=409, detail='No active turn found')
  return turn_info


def assert_current_player(player_id: int, current_player_id: int) -> None:
  if player_id != current_player_id:
    raise HTTPException(status_code=403, detail='Not your turn')


def assert_rolls_remaining(rolls_remaining: int, saved_rolls: int) -> None:
  if rolls_remaining + saved_rolls == 0:
    raise HTTPException(status_code=409, detail='No rolls remaining')


def assert_has_rolled(rolls_remaining: int) -> None:
  if rolls_remaining == BASE_ROLLS_PER_TURN:
    raise HTTPException(status_code=409, detail='Must roll before scoring')


def assert_player_exists(player: Player | None) -> Player:
  if player is None:
    raise HTTPException(status_code=404, detail='Player not found')
  return player


def assert_player_owns(player: Player, account_id: str) -> None:
  if player.account_id != account_id:
    raise HTTPException(status_code=403, detail='Forbidden')


def assert_player_exists_and_owns(player: Player | None, account_id: str) -> Player:
  player = assert_player_exists(player)
  assert_player_owns(player, account_id)
  return player


def assert_sequential_category(
  categories: list[ScoreCategory],
  is_sequential: bool,
  scored: set[ScoreCategory],
  requested: ScoreCategory,
) -> None:
  if not is_sequential:
    return
  for cat in categories:
    if cat not in scored:
      if cat != requested:
        raise HTTPException(status_code=409, detail='Must score categories in order')
      return
