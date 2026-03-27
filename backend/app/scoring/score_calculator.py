from collections import Counter
from app.scoring.score_category import ScoreCategory


def calculate(category: ScoreCategory, dice: list[int]) -> int:
  counts = Counter(dice)

  if category == ScoreCategory.ONES:
    return counts[1] * 1
  if category == ScoreCategory.TWOS:
    return counts[2] * 2
  if category == ScoreCategory.THREES:
    return counts[3] * 3
  if category == ScoreCategory.FOURS:
    return counts[4] * 4
  if category == ScoreCategory.FIVES:
    return counts[5] * 5
  if category == ScoreCategory.SIXES:
    return counts[6] * 6

  if category == ScoreCategory.ONE_PAIR:
    pairs = sorted([v for v, c in counts.items() if c >= 2], reverse=True)
    return pairs[0] * 2 if pairs else 0

  if category == ScoreCategory.TWO_PAIRS:
    pairs = sorted([v for v, c in counts.items() if c >= 2], reverse=True)
    return sum(v * 2 for v in pairs[:2]) if len(pairs) >= 2 else 0

  if category == ScoreCategory.THREE_PAIRS:
    pairs = [v for v, c in counts.items() if c >= 2]
    return sum(v * 2 for v in pairs) if len(pairs) >= 3 else 0

  if category == ScoreCategory.THREE_OF_A_KIND:
    trips = [v for v, c in counts.items() if c >= 3]
    return max(trips) * 3 if trips else 0

  if category == ScoreCategory.FOUR_OF_A_KIND:
    fours = [v for v, c in counts.items() if c >= 4]
    return max(fours) * 4 if fours else 0

  if category == ScoreCategory.FIVE_OF_A_KIND:
    fives = [v for v, c in counts.items() if c >= 5]
    return max(fives) * 5 if fives else 0

  if category == ScoreCategory.SMALL_STRAIGHT:
    return 15 if {1, 2, 3, 4, 5}.issubset(counts) else 0

  if category == ScoreCategory.LARGE_STRAIGHT:
    return 20 if {2, 3, 4, 5, 6}.issubset(counts) else 0

  if category == ScoreCategory.FULL_STRAIGHT:
    return 21 if set(counts) == {1, 2, 3, 4, 5, 6} else 0

  if category == ScoreCategory.FULL_HOUSE:
    trips = sorted([v for v, c in counts.items() if c >= 3], reverse=True)
    if not trips:
      return 0
    best_trip = trips[0]
    pairs = [v for v, c in counts.items() if c >= 2 and v != best_trip]
    return best_trip * 3 + max(pairs) * 2 if pairs else 0

  if category == ScoreCategory.VILLA:
    trips = [v for v, c in counts.items() if c >= 3]
    if len(trips) < 2:
      return 0
    top2 = sorted(trips, reverse=True)[:2]
    return sum(v * 3 for v in top2)

  if category == ScoreCategory.TOWER:
    fours = sorted([v for v, c in counts.items() if c >= 4], reverse=True)
    if not fours:
      return 0
    best_four = fours[0]
    pairs = [v for v, c in counts.items() if c >= 2 and v != best_four]
    return best_four * 4 + max(pairs) * 2 if pairs else 0

  if category == ScoreCategory.CHANCE:
    return sum(dice)

  if category == ScoreCategory.MAXI_YATZY:
    return 100 if len(counts) == 1 else 0

  if category == ScoreCategory.YATZY:
    return 50 if len(counts) == 1 else 0

  return 0
