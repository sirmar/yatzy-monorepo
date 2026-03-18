from pydantic import BaseModel
from app.die import Die


class GameState(BaseModel):
  status: str
  current_player_id: int | None = None
  dice: list[Die] | None = None
