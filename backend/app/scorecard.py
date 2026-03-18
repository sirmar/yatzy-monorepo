from pydantic import BaseModel
from app.score_category import ScoreCategory


class ScoreEntry(BaseModel):
  category: ScoreCategory
  score: int | None = None


class Scorecard(BaseModel):
  entries: list[ScoreEntry]
  bonus: int | None = None
  total: int
