import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class PlayerBase(BaseModel):
  name: str = Field(
    min_length=1, max_length=32, description='Display name of the player'
  )

  @field_validator('name')
  @classmethod
  def name_characters(cls, v: str) -> str:
    if not re.fullmatch(r'[^\W_]+([- _][^\W_]+)*', v, re.UNICODE):
      raise ValueError(
        'Name must start and end with a letter or number; spaces, hyphens, and underscores may only appear between words'
      )
    return v


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
  has_picture: bool = Field(
    default=False, description='Whether this player has a profile picture'
  )
  created_at: datetime = Field(description='When the player was created')
