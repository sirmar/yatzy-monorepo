from pydantic import BaseModel


class Die(BaseModel):
  index: int
  value: int | None = None
  kept: bool


class DiceResponse(BaseModel):
  dice: list[Die]
