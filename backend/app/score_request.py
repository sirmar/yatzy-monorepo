from pydantic import BaseModel
from app.score_category import ScoreCategory


class ScoreRequest(BaseModel):
  category: ScoreCategory
