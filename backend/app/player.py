from datetime import datetime
from pydantic import BaseModel, Field


class PlayerCreate(BaseModel):
  name: str = Field(min_length=1, max_length=64)


class PlayerUpdate(BaseModel):
  name: str = Field(min_length=1, max_length=64)


class Player(BaseModel):
  id: int
  name: str
  created_at: datetime
