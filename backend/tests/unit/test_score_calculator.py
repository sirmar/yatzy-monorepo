from app.scoring.score_calculator import calculate
from app.scoring.score_category import ScoreCategory


class TestUpperSection:
  def test_ones_sums_matching_dice(self):
    assert calculate(ScoreCategory.ONES, [3, 1, 5, 1, 4, 2]) == 2

  def test_ones_returns_zero_when_no_match(self):
    assert calculate(ScoreCategory.ONES, [4, 2, 6, 3, 5, 2]) == 0

  def test_twos_sums_matching_dice(self):
    assert calculate(ScoreCategory.TWOS, [2, 4, 2, 1, 2, 3]) == 6

  def test_threes_sums_matching_dice(self):
    assert calculate(ScoreCategory.THREES, [3, 2, 3, 1, 3, 3]) == 12

  def test_fours_sums_matching_dice(self):
    assert calculate(ScoreCategory.FOURS, [2, 4, 1, 4, 3, 5]) == 8

  def test_fives_sums_matching_dice(self):
    assert calculate(ScoreCategory.FIVES, [5, 1, 5, 5, 5, 5]) == 25

  def test_sixes_sums_matching_dice(self):
    assert calculate(ScoreCategory.SIXES, [6, 6, 6, 6, 6, 6]) == 36

  def test_sixes_returns_zero_when_no_match(self):
    assert calculate(ScoreCategory.SIXES, [5, 2, 5, 1, 3, 4]) == 0


class TestOnePair:
  def test_scores_sum_of_pair(self):
    assert calculate(ScoreCategory.ONE_PAIR, [4, 1, 3, 1, 5, 2]) == 2

  def test_scores_highest_pair_when_multiple(self):
    assert calculate(ScoreCategory.ONE_PAIR, [3, 5, 1, 5, 2, 3]) == 10

  def test_returns_zero_when_no_pair(self):
    assert calculate(ScoreCategory.ONE_PAIR, [4, 1, 6, 2, 5, 3]) == 0


class TestTwoPairs:
  def test_scores_sum_of_two_pairs(self):
    assert calculate(ScoreCategory.TWO_PAIRS, [2, 1, 3, 2, 4, 1]) == 6

  def test_scores_two_highest_pairs_when_three_available(self):
    assert calculate(ScoreCategory.TWO_PAIRS, [4, 6, 5, 4, 6, 5]) == 22

  def test_returns_zero_when_only_one_pair(self):
    assert calculate(ScoreCategory.TWO_PAIRS, [5, 1, 3, 1, 4, 2]) == 0


class TestThreePairs:
  def test_scores_sum_of_three_pairs(self):
    assert calculate(ScoreCategory.THREE_PAIRS, [2, 1, 3, 2, 1, 3]) == 12

  def test_returns_zero_when_four_of_a_kind_and_pair(self):
    assert calculate(ScoreCategory.THREE_PAIRS, [4, 3, 4, 4, 3, 4]) == 0

  def test_returns_zero_when_only_two_pairs(self):
    assert calculate(ScoreCategory.THREE_PAIRS, [2, 1, 3, 2, 4, 1]) == 0


class TestThreeOfAKind:
  def test_scores_sum_of_three(self):
    assert calculate(ScoreCategory.THREE_OF_A_KIND, [1, 3, 4, 3, 2, 3]) == 9

  def test_scores_highest_when_multiple(self):
    assert calculate(ScoreCategory.THREE_OF_A_KIND, [4, 5, 5, 4, 4, 5]) == 15

  def test_returns_zero_when_no_three(self):
    assert calculate(ScoreCategory.THREE_OF_A_KIND, [2, 1, 3, 2, 4, 1]) == 0


class TestFourOfAKind:
  def test_scores_sum_of_four(self):
    assert calculate(ScoreCategory.FOUR_OF_A_KIND, [6, 1, 6, 6, 2, 6]) == 24

  def test_returns_zero_when_only_three(self):
    assert calculate(ScoreCategory.FOUR_OF_A_KIND, [6, 3, 1, 6, 2, 6]) == 0


class TestFiveOfAKind:
  def test_scores_sum_of_five(self):
    assert calculate(ScoreCategory.FIVE_OF_A_KIND, [4, 4, 1, 4, 4, 4]) == 20

  def test_returns_zero_when_only_four(self):
    assert calculate(ScoreCategory.FIVE_OF_A_KIND, [4, 4, 1, 4, 2, 4]) == 0


class TestStraights:
  def test_small_straight_scores_15(self):
    assert calculate(ScoreCategory.SMALL_STRAIGHT, [4, 1, 3, 5, 2, 5]) == 15

  def test_small_straight_returns_zero_when_missing(self):
    assert calculate(ScoreCategory.SMALL_STRAIGHT, [4, 1, 3, 6, 2, 6]) == 0

  def test_large_straight_scores_20(self):
    assert calculate(ScoreCategory.LARGE_STRAIGHT, [3, 6, 2, 5, 4, 6]) == 20

  def test_large_straight_returns_zero_when_missing(self):
    assert calculate(ScoreCategory.LARGE_STRAIGHT, [3, 6, 1, 5, 4, 6]) == 0

  def test_full_straight_scores_21(self):
    assert calculate(ScoreCategory.FULL_STRAIGHT, [4, 1, 6, 2, 5, 3]) == 21

  def test_full_straight_returns_zero_when_not_all_unique(self):
    assert calculate(ScoreCategory.FULL_STRAIGHT, [4, 1, 5, 2, 5, 3]) == 0


class TestFullHouse:
  def test_scores_sum_of_three_and_pair(self):
    assert calculate(ScoreCategory.FULL_HOUSE, [5, 3, 1, 3, 5, 3]) == 19

  def test_returns_zero_when_no_pair(self):
    assert calculate(ScoreCategory.FULL_HOUSE, [5, 3, 4, 3, 6, 3]) == 0

  def test_returns_zero_when_no_three(self):
    assert calculate(ScoreCategory.FULL_HOUSE, [4, 3, 5, 3, 5, 4]) == 0


class TestVilla:
  def test_scores_sum_of_two_threes(self):
    assert calculate(ScoreCategory.VILLA, [5, 3, 5, 3, 5, 3]) == 24

  def test_returns_zero_when_only_one_three(self):
    assert calculate(ScoreCategory.VILLA, [5, 3, 1, 3, 5, 3]) == 0


class TestTower:
  def test_scores_sum_of_four_and_pair(self):
    assert calculate(ScoreCategory.TOWER, [2, 6, 6, 2, 6, 6]) == 28

  def test_returns_zero_when_no_pair(self):
    assert calculate(ScoreCategory.TOWER, [2, 6, 6, 3, 6, 6]) == 0

  def test_returns_zero_when_no_four(self):
    assert calculate(ScoreCategory.TOWER, [2, 6, 6, 2, 1, 6]) == 0


class TestChance:
  def test_scores_sum_of_all_dice(self):
    assert calculate(ScoreCategory.CHANCE, [4, 1, 6, 2, 5, 3]) == 21

  def test_scores_sum_of_all_dice_any_combination(self):
    assert calculate(ScoreCategory.CHANCE, [6, 6, 6, 6, 6, 6]) == 36


class TestMaxiYatzy:
  def test_scores_100_when_all_same(self):
    assert calculate(ScoreCategory.MAXI_YATZY, [5, 5, 5, 5, 5, 5]) == 100

  def test_returns_zero_when_not_all_same(self):
    assert calculate(ScoreCategory.MAXI_YATZY, [5, 4, 5, 5, 5, 5]) == 0
