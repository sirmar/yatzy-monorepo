from pydantic import BaseModel, Field


class GameStart(BaseModel):
  player_id: int = Field(gt=0)
