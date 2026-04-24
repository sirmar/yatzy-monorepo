from datetime import datetime
from pydantic import BaseModel
from yatzy_rules.game_mode import GameMode


class GameHistoryPlayer(BaseModel):
  player_id: int
  player_name: str
  score: int


class GameHistory(BaseModel):
  game_id: int
  mode: GameMode
  finished_at: datetime
  score: int
  rank: int
  players: list[GameHistoryPlayer]
