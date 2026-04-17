from yatzy_rules.score_calculator import calculate
from yatzy_rules.score_category import ScoreCategory


class TestUpperSection:
  def setup_method(self):
    pass

  def test_ones_sums_matching_dice(self):
    self.WhenCalculated(ScoreCategory.ONES, [3, 1, 5, 1, 4, 2])
    self.ThenScoreIs(2)

  def test_ones_returns_zero_when_no_match(self):
    self.WhenCalculated(ScoreCategory.ONES, [4, 2, 6, 3, 5, 2])
    self.ThenScoreIs(0)

  def test_twos_sums_matching_dice(self):
    self.WhenCalculated(ScoreCategory.TWOS, [2, 4, 2, 1, 2, 3])
    self.ThenScoreIs(6)

  def test_threes_sums_matching_dice(self):
    self.WhenCalculated(ScoreCategory.THREES, [3, 2, 3, 1, 3, 3])
    self.ThenScoreIs(12)

  def test_fours_sums_matching_dice(self):
    self.WhenCalculated(ScoreCategory.FOURS, [2, 4, 1, 4, 3, 5])
    self.ThenScoreIs(8)

  def test_fives_sums_matching_dice(self):
    self.WhenCalculated(ScoreCategory.FIVES, [5, 1, 5, 5, 5, 5])
    self.ThenScoreIs(25)

  def test_sixes_sums_matching_dice(self):
    self.WhenCalculated(ScoreCategory.SIXES, [6, 6, 6, 6, 6, 6])
    self.ThenScoreIs(36)

  def test_sixes_returns_zero_when_no_match(self):
    self.WhenCalculated(ScoreCategory.SIXES, [5, 2, 5, 1, 3, 4])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestOnePair:
  def setup_method(self):
    pass

  def test_scores_sum_of_pair(self):
    self.WhenCalculated(ScoreCategory.ONE_PAIR, [4, 1, 3, 1, 5, 2])
    self.ThenScoreIs(2)

  def test_scores_highest_pair_when_multiple(self):
    self.WhenCalculated(ScoreCategory.ONE_PAIR, [3, 5, 1, 5, 2, 3])
    self.ThenScoreIs(10)

  def test_returns_zero_when_no_pair(self):
    self.WhenCalculated(ScoreCategory.ONE_PAIR, [4, 1, 6, 2, 5, 3])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestTwoPairs:
  def setup_method(self):
    pass

  def test_scores_sum_of_two_pairs(self):
    self.WhenCalculated(ScoreCategory.TWO_PAIRS, [2, 1, 3, 2, 4, 1])
    self.ThenScoreIs(6)

  def test_scores_two_highest_pairs_when_three_available(self):
    self.WhenCalculated(ScoreCategory.TWO_PAIRS, [4, 6, 5, 4, 6, 5])
    self.ThenScoreIs(22)

  def test_returns_zero_when_only_one_pair(self):
    self.WhenCalculated(ScoreCategory.TWO_PAIRS, [5, 1, 3, 1, 4, 2])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestThreePairs:
  def setup_method(self):
    pass

  def test_scores_sum_of_three_pairs(self):
    self.WhenCalculated(ScoreCategory.THREE_PAIRS, [2, 1, 3, 2, 1, 3])
    self.ThenScoreIs(12)

  def test_returns_zero_when_four_of_a_kind_and_pair(self):
    self.WhenCalculated(ScoreCategory.THREE_PAIRS, [4, 3, 4, 4, 3, 4])
    self.ThenScoreIs(0)

  def test_returns_zero_when_only_two_pairs(self):
    self.WhenCalculated(ScoreCategory.THREE_PAIRS, [2, 1, 3, 2, 4, 1])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestThreeOfAKind:
  def setup_method(self):
    pass

  def test_scores_sum_of_three(self):
    self.WhenCalculated(ScoreCategory.THREE_OF_A_KIND, [1, 3, 4, 3, 2, 3])
    self.ThenScoreIs(9)

  def test_scores_highest_when_multiple(self):
    self.WhenCalculated(ScoreCategory.THREE_OF_A_KIND, [4, 5, 5, 4, 4, 5])
    self.ThenScoreIs(15)

  def test_returns_zero_when_no_three(self):
    self.WhenCalculated(ScoreCategory.THREE_OF_A_KIND, [2, 1, 3, 2, 4, 1])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestFourOfAKind:
  def setup_method(self):
    pass

  def test_scores_sum_of_four(self):
    self.WhenCalculated(ScoreCategory.FOUR_OF_A_KIND, [6, 1, 6, 6, 2, 6])
    self.ThenScoreIs(24)

  def test_returns_zero_when_only_three(self):
    self.WhenCalculated(ScoreCategory.FOUR_OF_A_KIND, [6, 3, 1, 6, 2, 6])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestFiveOfAKind:
  def setup_method(self):
    pass

  def test_scores_sum_of_five(self):
    self.WhenCalculated(ScoreCategory.FIVE_OF_A_KIND, [4, 4, 1, 4, 4, 4])
    self.ThenScoreIs(20)

  def test_returns_zero_when_only_four(self):
    self.WhenCalculated(ScoreCategory.FIVE_OF_A_KIND, [4, 4, 1, 4, 2, 4])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestStraights:
  def setup_method(self):
    pass

  def test_small_straight_scores_15(self):
    self.WhenCalculated(ScoreCategory.SMALL_STRAIGHT, [4, 1, 3, 5, 2, 5])
    self.ThenScoreIs(15)

  def test_small_straight_returns_zero_when_missing(self):
    self.WhenCalculated(ScoreCategory.SMALL_STRAIGHT, [4, 1, 3, 6, 2, 6])
    self.ThenScoreIs(0)

  def test_large_straight_scores_20(self):
    self.WhenCalculated(ScoreCategory.LARGE_STRAIGHT, [3, 6, 2, 5, 4, 6])
    self.ThenScoreIs(20)

  def test_large_straight_returns_zero_when_missing(self):
    self.WhenCalculated(ScoreCategory.LARGE_STRAIGHT, [3, 6, 1, 5, 4, 6])
    self.ThenScoreIs(0)

  def test_full_straight_scores_21(self):
    self.WhenCalculated(ScoreCategory.FULL_STRAIGHT, [4, 1, 6, 2, 5, 3])
    self.ThenScoreIs(21)

  def test_full_straight_returns_zero_when_not_all_unique(self):
    self.WhenCalculated(ScoreCategory.FULL_STRAIGHT, [4, 1, 5, 2, 5, 3])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestFullHouse:
  def setup_method(self):
    pass

  def test_scores_sum_of_three_and_pair(self):
    self.WhenCalculated(ScoreCategory.FULL_HOUSE, [5, 3, 1, 3, 5, 3])
    self.ThenScoreIs(19)

  def test_returns_zero_when_no_pair(self):
    self.WhenCalculated(ScoreCategory.FULL_HOUSE, [5, 3, 4, 3, 6, 3])
    self.ThenScoreIs(0)

  def test_returns_zero_when_no_three(self):
    self.WhenCalculated(ScoreCategory.FULL_HOUSE, [4, 3, 5, 3, 5, 4])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestVilla:
  def setup_method(self):
    pass

  def test_scores_sum_of_two_threes(self):
    self.WhenCalculated(ScoreCategory.VILLA, [5, 3, 5, 3, 5, 3])
    self.ThenScoreIs(24)

  def test_returns_zero_when_only_one_three(self):
    self.WhenCalculated(ScoreCategory.VILLA, [5, 3, 1, 3, 5, 3])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestTower:
  def setup_method(self):
    pass

  def test_scores_sum_of_four_and_pair(self):
    self.WhenCalculated(ScoreCategory.TOWER, [2, 6, 6, 2, 6, 6])
    self.ThenScoreIs(28)

  def test_returns_zero_when_no_pair(self):
    self.WhenCalculated(ScoreCategory.TOWER, [2, 6, 6, 3, 6, 6])
    self.ThenScoreIs(0)

  def test_returns_zero_when_no_four(self):
    self.WhenCalculated(ScoreCategory.TOWER, [2, 6, 6, 2, 1, 6])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestChance:
  def setup_method(self):
    pass

  def test_scores_sum_of_all_dice(self):
    self.WhenCalculated(ScoreCategory.CHANCE, [4, 1, 6, 2, 5, 3])
    self.ThenScoreIs(21)

  def test_scores_sum_of_all_dice_any_combination(self):
    self.WhenCalculated(ScoreCategory.CHANCE, [6, 6, 6, 6, 6, 6])
    self.ThenScoreIs(36)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestMaxiYatzy:
  def setup_method(self):
    pass

  def test_scores_100_when_all_same(self):
    self.WhenCalculated(ScoreCategory.MAXI_YATZY, [5, 5, 5, 5, 5, 5])
    self.ThenScoreIs(100)

  def test_returns_zero_when_not_all_same(self):
    self.WhenCalculated(ScoreCategory.MAXI_YATZY, [5, 4, 5, 5, 5, 5])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected


class TestYatzy:
  def setup_method(self):
    pass

  def test_scores_50_when_all_same(self):
    self.WhenCalculated(ScoreCategory.YATZY, [4, 4, 4, 4, 4])
    self.ThenScoreIs(50)

  def test_returns_zero_when_not_all_same(self):
    self.WhenCalculated(ScoreCategory.YATZY, [4, 4, 4, 4, 3])
    self.ThenScoreIs(0)

  def WhenCalculated(self, category, dice):
    self.result = calculate(category, dice)

  def ThenScoreIs(self, expected):
    assert self.result == expected
