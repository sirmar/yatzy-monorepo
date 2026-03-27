from app.scoring.score_category import ScoreCategory

UPPER_CATEGORIES = {
  ScoreCategory.ONES,
  ScoreCategory.TWOS,
  ScoreCategory.THREES,
  ScoreCategory.FOURS,
  ScoreCategory.FIVES,
  ScoreCategory.SIXES,
}
BONUS_THRESHOLD = 84
BONUS_SCORE = 100


def calculate_bonus(
  scores: dict[str, int],
  bonus_threshold: int = BONUS_THRESHOLD,
  bonus_score: int = BONUS_SCORE,
) -> int:
  upper_total = sum(scores.get(cat, 0) for cat in UPPER_CATEGORIES)
  return bonus_score if upper_total >= bonus_threshold else 0
