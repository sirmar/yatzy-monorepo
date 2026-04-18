from datetime import datetime
from pydantic import BaseModel, Field


class PlayerBase(BaseModel):
  name: str = Field(
    min_length=1, max_length=64, description='Display name of the player'
  )


class PlayerCreate(PlayerBase):
  pass


class PlayerUpdate(PlayerBase):
  pass


class Player(BaseModel):
  id: int = Field(description='Unique player identifier')
  account_id: str | None = Field(
    description='Auth account ID that owns this player; null for bot players'
  )
  name: str = Field(description='Display name of the player')
  is_bot: bool = Field(default=False, description='Whether this is an AI bot player')
  created_at: datetime = Field(description='When the player was created')
