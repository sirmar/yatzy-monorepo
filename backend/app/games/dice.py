from pydantic import BaseModel, Field


class Die(BaseModel):
  index: int = Field(description='Die position (0–5)')
  value: int | None = Field(
    default=None, description='Face value (1–6), null if not yet rolled'
  )
  kept: bool = Field(description='Whether this die is held for the next roll')


class DiceResponse(BaseModel):
  dice: list[Die] = Field(description='All six dice after the roll')
