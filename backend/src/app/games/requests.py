from pydantic import BaseModel, Field


class GameJoin(BaseModel):
  player_id: int = Field(gt=0, description='ID of the player joining the game')


class GameStart(BaseModel):
  player_id: int = Field(gt=0, description='ID of the creator starting the game')


class RollRequest(BaseModel):
  player_id: int = Field(gt=0, description='ID of the current player')
  kept_dice: list[int] = Field(
    default_factory=list,
    description='Indices (0–5) of dice to keep; all others are rerolled',
  )
