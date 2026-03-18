from pydantic import BaseModel
from app.games.dice import Die
from app.games.game_status import GameStatus


class GameState(BaseModel):
  status: GameStatus
  current_player_id: int | None = None
  dice: list[Die] | None = None
