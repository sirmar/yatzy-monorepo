from collections import Counter
from app.sim.bot_core import keep_for_target
from app.sim.maxi_bot import _CONFIG as _maxi_config


def _keep_for_target(dice, cat):
  return keep_for_target(dice, cat, _maxi_config)
from app.sim.dice_keep import (
  keep_for_straight,
  keep_full_house,
  keep_n_of_face,
  keep_pairs_from_faces,
  keep_top_faces_with_limits,
)
from yatzy_rules.score_category import ScoreCategory as Category

_MAXI_STRAIGHTS = [{1, 2, 3, 4, 5, 6}, {2, 3, 4, 5, 6}, {1, 2, 3, 4, 5}]


def _keep_for_straight(dice):
  return keep_for_straight(dice, _MAXI_STRAIGHTS)


def _keep_n_of_face(dice, face, n):
  return keep_n_of_face(dice, face, n)


def _keep_pairs_from_faces(dice, faces):
  return keep_pairs_from_faces(dice, faces)


def _keep_top_faces_with_limits(dice, limits):
  return keep_top_faces_with_limits(dice, limits)


def _keep_full_house(dice):
  return keep_full_house(dice)


def test_keep_n_of_face_keeps_up_to_n():
  assert _keep_n_of_face([6, 6, 6, 1, 2, 3], 6, 2) == [True, True, False, False, False, False]


def test_keep_n_of_face_fewer_than_n_available():
  assert _keep_n_of_face([6, 1, 2, 3, 4, 5], 6, 3) == [True, False, False, False, False, False]


def test_keep_pairs_from_faces_two_pairs():
  assert _keep_pairs_from_faces([5, 5, 4, 4, 1, 2], [5, 4]) == [True, True, True, True, False, False]


def test_keep_for_straight_full():
  assert _keep_for_straight([1, 2, 3, 4, 5, 6]) == [True, True, True, True, True, True]


def test_keep_for_straight_large_keeps_one_of_each():
  assert _keep_for_straight([2, 3, 4, 5, 6, 6]) == [True, True, True, True, True, False]


def test_keep_for_straight_small_keeps_one_of_each():
  assert _keep_for_straight([1, 2, 3, 4, 5, 5]) == [True, True, True, True, True, False]


def test_keep_for_straight_four_matching_keeps_run():
  result = _keep_for_straight([1, 2, 3, 4, 6, 6])
  assert result == [True, True, True, True, True, False]


def test_keep_for_straight_no_run():
  assert _keep_for_straight([1, 1, 1, 6, 6, 6]) == [False, False, False, False, False, False]


def test_keep_top_faces_tower():
  result = _keep_top_faces_with_limits([6, 6, 6, 6, 5, 5], [4, 2])
  assert result == [True, True, True, True, True, True]


def test_keep_top_faces_villa():
  result = _keep_top_faces_with_limits([6, 6, 6, 5, 5, 5], [3, 3])
  assert result == [True, True, True, True, True, True]


def test_keep_full_house_with_trips_and_pair():
  result = _keep_full_house([6, 6, 6, 5, 5, 1])
  assert result == [True, True, True, True, True, False]


def test_keep_full_house_only_pair():
  # limits [3,2]: keeps up to 3 of best face (6,6) and up to 2 of second (4)
  result = _keep_full_house([6, 6, 1, 2, 3, 4])
  assert result == [True, True, False, False, False, True]


def test_keep_for_target_upper():
  result = _keep_for_target([6, 6, 1, 2, 3, 4], Category.SIXES)
  assert result == [True, True, False, False, False, False]


def test_keep_for_target_maxi_yatzy_keeps_dominant_face():
  result = _keep_for_target([5, 5, 5, 5, 1, 2], Category.MAXI_YATZY)
  assert result == [True, True, True, True, False, False]


def test_keep_for_target_chance_keeps_high_dice():
  result = _keep_for_target([6, 5, 4, 3, 2, 1], Category.CHANCE)
  assert result == [True, True, True, False, False, False]


def test_keep_for_target_one_pair_with_pair():
  result = _keep_for_target([6, 6, 1, 2, 3, 4], Category.ONE_PAIR)
  assert result == [True, True, False, False, False, False]


def test_keep_for_target_one_pair_no_pair_keeps_best():
  result = _keep_for_target([6, 5, 4, 3, 2, 1], Category.ONE_PAIR)
  assert sum(result) == 1
  assert result[0]


def test_keep_for_target_two_pairs():
  result = _keep_for_target([6, 6, 5, 5, 1, 2], Category.TWO_PAIRS)
  assert result == [True, True, True, True, False, False]


def test_keep_for_target_three_pairs():
  result = _keep_for_target([6, 6, 5, 5, 4, 4], Category.THREE_PAIRS)
  assert result == [True, True, True, True, True, True]


def test_keep_for_target_three_pairs_no_pairs_keeps_best():
  result = _keep_for_target([6, 5, 4, 3, 2, 1], Category.THREE_PAIRS)
  assert len(result) == 6
  assert sum(result) == 1
  assert result[0]


def test_keep_for_target_four_of_a_kind():
  result = _keep_for_target([6, 6, 6, 6, 1, 2], Category.FOUR_OF_A_KIND)
  assert result == [True, True, True, True, False, False]


def test_keep_for_target_tower():
  result = _keep_for_target([6, 6, 6, 6, 5, 5], Category.TOWER)
  assert result == [True, True, True, True, True, True]


def test_keep_for_target_villa():
  result = _keep_for_target([6, 6, 6, 5, 5, 1], Category.VILLA)
  assert result == [True, True, True, True, True, False]
