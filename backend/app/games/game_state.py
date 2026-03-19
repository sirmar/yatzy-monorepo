from pydantic import BaseModel, Field
from app.games.dice import Die
from app.games.game_status import GameStatus


class PlayerScore(BaseModel):
  player_id: int = Field(description='Player identifier')
  total: int = Field(description='Final total score including bonus')


class GameState(BaseModel):
  status: GameStatus = Field(description='Current game status')
  current_player_id: int | None = Field(
    default=None,
    description='ID of the player whose turn it is; null when game is not active',
  )
  dice: list[Die] | None = Field(
    default=None, description='Current dice state; null when game is not active'
  )
  winner_ids: list[int] | None = Field(
    default=None, description='IDs of the winner(s); set when game has ended'
  )
  final_scores: list[PlayerScore] | None = Field(
    default=None, description='Final scores for all players; set when game has ended'
  )
