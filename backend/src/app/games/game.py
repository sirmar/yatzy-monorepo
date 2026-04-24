from datetime import datetime
from pydantic import BaseModel, Field
from yatzy_rules.game_mode import GameMode
from app.games.game_status import GameStatus


class GameCreate(BaseModel):
  creator_id: int = Field(gt=0, description='ID of the player creating the game')
  mode: GameMode = Field(default=GameMode.MAXI, description='Game mode')
  bot_count: int = Field(
    default=0, ge=0, le=5, description='Number of bot players to add'
  )


class Game(BaseModel):
  id: int = Field(description='Unique game identifier')
  status: GameStatus = Field(description='Current status of the game')
  mode: GameMode = Field(description='Game mode')
  creator_id: int = Field(description='ID of the player who created the game')
  player_ids: list[int] = Field(description='IDs of all players who have joined')
  current_player_id: int | None = Field(
    default=None, description='ID of the player whose turn it currently is'
  )
  created_at: datetime = Field(description='When the game was created')
  started_at: datetime | None = Field(
    default=None, description='When the game was started'
  )
  ended_at: datetime | None = Field(default=None, description='When the game ended')
