from datetime import datetime
from pydantic import BaseModel, Field
from app.games.game_status import GameStatus


class GameCreate(BaseModel):
  creator_id: int = Field(gt=0, description='ID of the player creating the game')


class Game(BaseModel):
  id: int = Field(description='Unique game identifier')
  status: GameStatus = Field(description='Current status of the game')
  creator_id: int = Field(description='ID of the player who created the game')
  player_ids: list[int] = Field(description='IDs of all players who have joined')
  created_at: datetime = Field(description='When the game was created')
  started_at: datetime | None = Field(
    default=None, description='When the game was started'
  )
  ended_at: datetime | None = Field(default=None, description='When the game ended')
