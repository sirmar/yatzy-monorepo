from app.scoring.scoring_rules import calculate_bonus


class TestCalculateBonus:
  def setup_method(self):
    self.scores: dict[str, int] = {}
    self.result: int | None = None

  def test_returns_bonus_at_threshold(self):
    self.GivenUpperScores({'ones': 3, 'twos': 6, 'threes': 9, 'fours': 16, 'fives': 20, 'sixes': 30})
    self.WhenBonusCalculated()
    self.ThenBonusIs(100)

  def test_returns_bonus_above_threshold(self):
    self.GivenUpperScores({'ones': 6, 'twos': 12, 'threes': 18, 'fours': 24, 'fives': 30, 'sixes': 36})
    self.WhenBonusCalculated()
    self.ThenBonusIs(100)

  def test_returns_zero_one_below_threshold(self):
    self.GivenUpperScores({'ones': 3, 'twos': 6, 'threes': 9, 'fours': 16, 'fives': 20, 'sixes': 29})
    self.WhenBonusCalculated()
    self.ThenBonusIs(0)

  def test_returns_zero_when_upper_total_is_low(self):
    self.GivenUpperScores({'ones': 1, 'twos': 2, 'threes': 3, 'fours': 4, 'fives': 5, 'sixes': 6})
    self.WhenBonusCalculated()
    self.ThenBonusIs(0)

  def test_ignores_lower_categories(self):
    self.GivenUpperScores({'maxi_yatzy': 100, 'chance': 30, 'full_straight': 21})
    self.WhenBonusCalculated()
    self.ThenBonusIs(0)

  def test_treats_missing_upper_categories_as_zero(self):
    self.GivenUpperScores({'sixes': 36})
    self.WhenBonusCalculated()
    self.ThenBonusIs(0)

  def test_yatzy_returns_50_at_threshold(self):
    self.GivenUpperScores({'ones': 3, 'twos': 6, 'threes': 9, 'fours': 12, 'fives': 15, 'sixes': 18})
    self.WhenBonusCalculated(threshold=63, score=50)
    self.ThenBonusIs(50)

  def test_yatzy_returns_zero_one_below_threshold(self):
    self.GivenUpperScores({'ones': 3, 'twos': 6, 'threes': 9, 'fours': 12, 'fives': 15, 'sixes': 17})
    self.WhenBonusCalculated(threshold=63, score=50)
    self.ThenBonusIs(0)

  def GivenUpperScores(self, scores: dict[str, int]):
    self.scores = scores

  def WhenBonusCalculated(self, threshold: int = 84, score: int = 100):
    self.result = calculate_bonus(self.scores, threshold, score)

  def ThenBonusIs(self, expected: int):
    assert self.result == expected
