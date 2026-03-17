from pydantic import BaseModel, Field


class GameJoin(BaseModel):
  player_id: int = Field(gt=0)
