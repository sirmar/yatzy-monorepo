from pydantic import BaseModel, Field
from app.games.dice import Die
from yatzy_rules.game_mode import GameMode
from app.games.game_status import GameStatus


class PlayerScore(BaseModel):
  player_id: int = Field(description='Player identifier')
  total: int = Field(description='Final total score including bonus')


class GameState(BaseModel):
  status: GameStatus = Field(description='Current game status')
  mode: GameMode | None = Field(default=None, description='Game mode')
  current_player_id: int | None = Field(
    default=None,
    description='ID of the player whose turn it is; null when game is not active',
  )
  dice: list[Die] | None = Field(
    default=None, description='Current dice state; null when game is not active'
  )
  rolls_remaining: int | None = Field(
    default=None, description='Regular rolls left this turn'
  )
  saved_rolls: int | None = Field(
    default=None, description='Saved bonus rolls from previous turns'
  )
  winner_ids: list[int] | None = Field(
    default=None, description='IDs of the winner(s); set when game has ended'
  )
  final_scores: list[PlayerScore] | None = Field(
    default=None, description='Final scores for all players; set when game has ended'
  )
