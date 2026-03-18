from pydantic import BaseModel, Field


class GameJoin(BaseModel):
  player_id: int = Field(gt=0)


class GameStart(BaseModel):
  player_id: int = Field(gt=0)


class RollRequest(BaseModel):
  player_id: int = Field(gt=0)
  kept_dice: list[int] = []
