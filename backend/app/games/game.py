from datetime import datetime
from pydantic import BaseModel, Field
from app.games.game_status import GameStatus


class GameCreate(BaseModel):
  creator_id: int = Field(gt=0)


class Game(BaseModel):
  id: int
  status: GameStatus
  creator_id: int
  player_ids: list[int]
  created_at: datetime
  started_at: datetime | None = None
  ended_at: datetime | None = None
