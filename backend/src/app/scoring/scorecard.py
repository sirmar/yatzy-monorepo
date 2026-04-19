from pydantic import BaseModel, Field
from yatzy_rules.score_category import ScoreCategory


class ScoreEntry(BaseModel):
  category: ScoreCategory = Field(description='Scoring category')
  score: int | None = Field(
    default=None, description='Points scored; null if not yet filled'
  )
  last_scored: bool = Field(
    default=False,
    description='True if this was the most recently scored category for this player',
  )


class Scorecard(BaseModel):
  entries: list[ScoreEntry] = Field(description='One entry per scoring category')
  bonus: int | None = Field(
    default=None,
    description='Upper section bonus (100 points) if score reaches 84; null if not yet earned',
  )
  total: int = Field(description='Total score including bonus')


class ScoreRequest(BaseModel):
  category: ScoreCategory = Field(description='Category to score with the current dice')


class PlayerScorecard(BaseModel):
  player_id: int = Field(description='Player identifier')
  entries: list[ScoreEntry] = Field(description='One entry per scoring category')
  bonus: int | None = Field(
    default=None,
    description='Upper section bonus (100 points) if score reaches 84; null if not yet earned',
  )
  total: int = Field(description='Total score including bonus')


class ScoringOption(BaseModel):
  category: ScoreCategory = Field(description='Available scoring category')
  score: int = Field(
    description='Points that would be scored for this category with the current dice'
  )
