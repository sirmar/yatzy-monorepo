from app.sim.rule_bot import action
from app.sim.game_state import GameState, DICE_COUNT, CATEGORIES
from yatzy_rules.score_category import ScoreCategory as Category


def make_state(dice, rolls_remaining=2, saved_rolls=0, has_rolled=True, scores=None):
  return GameState(
    dice=dice,
    kept=[False] * DICE_COUNT,
    rolls_remaining=rolls_remaining,
    saved_rolls=saved_rolls,
    has_rolled=has_rolled,
    scores=scores or {},
  )


def test_must_roll_first_returns_keep_nothing():
  state = make_state([1, 2, 3, 4, 5, 6], has_rolled=False)
  act = action(state)
  assert not isinstance(act, Category)
  assert act == [False] * DICE_COUNT


def test_must_score_scores_something():
  state = make_state([6, 6, 6, 6, 6, 6], rolls_remaining=0, saved_rolls=0)
  act = action(state)
  assert isinstance(act, Category)


def test_maxi_yatzy_scored_immediately():
  state = make_state([6, 6, 6, 6, 6, 6])
  act = action(state)
  assert act == Category.MAXI_YATZY


def test_full_straight_scored_immediately():
  state = make_state([1, 2, 3, 4, 5, 6])
  act = action(state)
  assert act == Category.FULL_STRAIGHT


def test_large_straight_scored_immediately():
  state = make_state([2, 3, 4, 5, 6, 1], scores={Category.FULL_STRAIGHT: 0})
  act = action(state)
  assert act == Category.LARGE_STRAIGHT


def test_four_sixes_keeps_for_five_of_a_kind():
  state = make_state([6, 6, 6, 6, 1, 2])
  act = action(state)
  assert act == [True, True, True, True, False, False]


def test_four_of_kind_not_high_face_does_not_keep_for_five():
  state = make_state([3, 3, 3, 3, 1, 2])
  act = action(state)
  assert not isinstance(act, Category)


def test_must_score_sacrifices_lowest_value():
  scores = {cat: 0 for cat in CATEGORIES if cat != Category.CHANCE}
  state = make_state([1, 2, 3, 1, 2, 3], rolls_remaining=0, saved_rolls=0, scores=scores)
  act = action(state)
  assert act == Category.CHANCE


def test_no_rolls_with_saved_rolls_scores_upper_at_expected():
  # 5 sixes (30 >= expected 24) — five-of-a-kind check won't fire (30 != 24)
  state = make_state(
    [6, 6, 6, 6, 6, 1],
    rolls_remaining=0,
    saved_rolls=1,
    scores={cat: 0 for cat in CATEGORIES if cat != Category.SIXES},
  )
  act = action(state)
  assert act == Category.SIXES


def test_keeps_target_dice_when_rolling():
  state = make_state([6, 6, 6, 1, 2, 3], rolls_remaining=1)
  act = action(state)
  assert not isinstance(act, Category)
  assert act[:3] == [True, True, True]
