from datetime import datetime
from pydantic import BaseModel


class HighScore(BaseModel):
  player_id: int
  player_name: str
  game_id: int
  finished_at: datetime
  total_score: int
