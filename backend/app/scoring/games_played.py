from enum import StrEnum

from pydantic import BaseModel


class GamesPlayedSortBy(StrEnum):
  TOTAL = 'total'
  MAXI = 'maxi'
  MAXI_SEQUENTIAL = 'maxi_sequential'
  YATZY = 'yatzy'
  YATZY_SEQUENTIAL = 'yatzy_sequential'


class GamesPlayed(BaseModel):
  player_id: int
  player_name: str
  total: int
  maxi: int
  maxi_sequential: int
  yatzy: int
  yatzy_sequential: int
