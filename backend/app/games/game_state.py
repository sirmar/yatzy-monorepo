from pydantic import BaseModel
from app.games.dice import Die
from app.games.game_status import GameStatus


class PlayerScore(BaseModel):
  player_id: int
  total: int


class GameState(BaseModel):
  status: GameStatus
  current_player_id: int | None = None
  dice: list[Die] | None = None
  winner_ids: list[int] | None = None
  final_scores: list[PlayerScore] | None = None
