from datetime import datetime
from pydantic import BaseModel
from app.games.game_mode import GameMode


class HighScore(BaseModel):
  player_id: int
  player_name: str
  game_id: int
  finished_at: datetime
  total_score: int
  mode: GameMode
