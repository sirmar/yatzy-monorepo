from datetime import datetime
from pydantic import BaseModel, Field


class GameCreate(BaseModel):
  creator_id: int = Field(gt=0)


class Game(BaseModel):
  id: int
  status: str
  creator_id: int
  player_ids: list[int]
  created_at: datetime
  started_at: datetime | None = None
  ended_at: datetime | None = None
