from datetime import datetime
from pydantic import BaseModel


class ModeStats(BaseModel):
  games_played: int
  high_score: int | None
  average_score: int | None
  bonus_count: int
  yatzy_hit_count: int


class PlayerStats(BaseModel):
  player_id: int
  player_name: str
  member_since: datetime
  total_games_played: int
  maxi: ModeStats
  maxi_sequential: ModeStats
  yatzy: ModeStats
  yatzy_sequential: ModeStats
