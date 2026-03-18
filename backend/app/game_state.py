from pydantic import BaseModel
from app.die import Die
from app.game_status import GameStatus


class GameState(BaseModel):
  status: GameStatus
  current_player_id: int | None = None
  dice: list[Die] | None = None
