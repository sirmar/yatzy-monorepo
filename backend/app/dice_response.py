from pydantic import BaseModel
from app.die import Die


class DiceResponse(BaseModel):
  dice: list[Die]
