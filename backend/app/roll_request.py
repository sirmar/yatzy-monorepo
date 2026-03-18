from pydantic import BaseModel, Field


class RollRequest(BaseModel):
  player_id: int = Field(gt=0)
  kept_dice: list[int] = []
