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
  account_id: str = Field(description='Auth account ID that owns this player')
  name: str = Field(description='Display name of the player')
  created_at: datetime = Field(description='When the player was created')
