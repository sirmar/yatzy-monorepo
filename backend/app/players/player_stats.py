from datetime import datetime
from pydantic import BaseModel


class PlayerStats(BaseModel):
  player_id: int
  player_name: str
  member_since: datetime
  games_played: int
  high_score: int | None
  average_score: int | None
  bonus_count: int
  maxi_yatzy_count: int
