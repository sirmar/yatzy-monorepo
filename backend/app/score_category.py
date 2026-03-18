from enum import StrEnum


class ScoreCategory(StrEnum):
  ONES = 'ones'
  TWOS = 'twos'
  THREES = 'threes'
  FOURS = 'fours'
  FIVES = 'fives'
  SIXES = 'sixes'
  ONE_PAIR = 'one_pair'
  TWO_PAIRS = 'two_pairs'
  THREE_PAIRS = 'three_pairs'
  THREE_OF_A_KIND = 'three_of_a_kind'
  FOUR_OF_A_KIND = 'four_of_a_kind'
  FIVE_OF_A_KIND = 'five_of_a_kind'
  SMALL_STRAIGHT = 'small_straight'
  LARGE_STRAIGHT = 'large_straight'
  FULL_STRAIGHT = 'full_straight'
  FULL_HOUSE = 'full_house'
  VILLA = 'villa'
  TOWER = 'tower'
  CHANCE = 'chance'
  MAXI_YATZY = 'maxi_yatzy'
