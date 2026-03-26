from enum import StrEnum

from pydantic import BaseModel


class GamesPlayedSortBy(StrEnum):
  TOTAL = 'total'
  STANDARD = 'standard'
  SEQUENTIAL = 'sequential'


class GamesPlayed(BaseModel):
  player_id: int
  player_name: str
  total: int
  standard: int
  sequential: int
