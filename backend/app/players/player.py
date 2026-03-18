from datetime import datetime
from pydantic import BaseModel, Field


class PlayerBase(BaseModel):
  name: str = Field(min_length=1, max_length=64)


class PlayerCreate(PlayerBase):
  pass


class PlayerUpdate(PlayerBase):
  pass


class Player(BaseModel):
  id: int
  name: str
  created_at: datetime
