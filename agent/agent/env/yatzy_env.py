import numpy as np
import gymnasium as gym
from gymnasium import spaces
from sim.game_state import GameState, CATEGORIES, DICE_COUNT
from sim import engine
from yatzy_rules.scoring_rules import UPPER_CATEGORIES
from yatzy_rules.score_category import ScoreCategory
from yatzy_rules.score_calculator import calculate
from yatzy_rules.game_variant import get_variant
from yatzy_rules.game_mode import GameMode

_VARIANT = get_variant(GameMode.MAXI)

# Actions 0-63: roll with keep bitmask (bit i = keep die i)
# Actions 64-83: score category index (0-19 mapped to CATEGORIES)
ROLL_ACTIONS = 2 ** DICE_COUNT  # 64
SCORE_ACTIONS = len(CATEGORIES)  # 20
TOTAL_ACTIONS = ROLL_ACTIONS + SCORE_ACTIONS  # 84

MAX_SAVED_ROLLS = 30

# Observation vector layout:
#   [0:6]   dice values (1-6)
#   [6:12]  kept flags (0/1)
#   [12]    rolls_remaining (0-3)
#   [13]    saved_rolls (0-MAX_SAVED_ROLLS)
#   [14]    has_rolled (0/1)
#   [15:35] category scores (-1 = unscored, else actual score)
OBS_SIZE = DICE_COUNT + DICE_COUNT + 1 + 1 + 1 + SCORE_ACTIONS  # 35

# Theoretical maximum score per category with 6 dice.
# Used to penalise zeroing a category: reward -= max_score if points == 0.
_CATEGORY_MAX: dict[ScoreCategory, int] = {
  cat: calculate(cat, [i + 1 for i in range(6) for _ in range(6)][:DICE_COUNT])
  for cat in CATEGORIES
}
# The brute-force above won't find all maxima (e.g. TOWER needs 4+2, not 6-of-a-kind).
# Override with exact values derived from scoring rules.
_CATEGORY_MAX.update({
  ScoreCategory.ONES:            6,   # [1,1,1,1,1,1]
  ScoreCategory.TWOS:            12,  # [2,2,2,2,2,2]
  ScoreCategory.THREES:          18,  # [3,3,3,3,3,3]
  ScoreCategory.FOURS:           24,  # [4,4,4,4,4,4]
  ScoreCategory.FIVES:           30,  # [5,5,5,5,5,5]
  ScoreCategory.SIXES:           36,  # [6,6,6,6,6,6]
  ScoreCategory.ONE_PAIR:        12,  # [6,6,_,_,_,_]
  ScoreCategory.TWO_PAIRS:       22,  # [6,6,5,5,_,_]
  ScoreCategory.THREE_PAIRS:     30,  # [6,6,5,5,4,4]
  ScoreCategory.THREE_OF_A_KIND: 18,  # [6,6,6,_,_,_]
  ScoreCategory.FOUR_OF_A_KIND:  24,  # [6,6,6,6,_,_]
  ScoreCategory.FIVE_OF_A_KIND:  30,  # [6,6,6,6,6,_]
  ScoreCategory.SMALL_STRAIGHT:  15,  # [1,2,3,4,5,_]
  ScoreCategory.LARGE_STRAIGHT:  20,  # [2,3,4,5,6,_]
  ScoreCategory.FULL_STRAIGHT:   21,  # [1,2,3,4,5,6]
  ScoreCategory.FULL_HOUSE:      28,  # [6,6,6,5,5,_] = 18+10
  ScoreCategory.VILLA:           33,  # [6,6,6,5,5,5] = 18+15
  ScoreCategory.TOWER:           34,  # [6,6,6,6,5,5] = 24+10
  ScoreCategory.CHANCE:          36,  # [6,6,6,6,6,6]
  ScoreCategory.MAXI_YATZY:      100,
})


def _observe(state: GameState) -> np.ndarray:
  obs = np.zeros(OBS_SIZE, dtype=np.float32)
  for i, v in enumerate(state.dice):
    obs[i] = v
  for i, k in enumerate(state.kept):
    obs[DICE_COUNT + i] = float(k)
  obs[12] = state.rolls_remaining
  obs[13] = min(state.saved_rolls, MAX_SAVED_ROLLS)
  obs[14] = float(state.has_rolled)
  for i, cat in enumerate(CATEGORIES):
    obs[15 + i] = state.scores[cat] if cat in state.scores else -1.0
  return obs


def _action_mask(state: GameState, mask_yatzy: bool = False) -> np.ndarray:
  mask = np.zeros(TOTAL_ACTIONS, dtype=np.int8)

  if not state.is_done:
    if state.can_roll and not state.must_score:
      mask[:ROLL_ACTIONS] = 1

    if state.has_rolled:
      for i, cat in enumerate(CATEGORIES):
        if cat not in state.scores:
          if mask_yatzy and cat == ScoreCategory.MAXI_YATZY:
            continue
          mask[ROLL_ACTIONS + i] = 1

  return mask


_UPPER_FACE = {
  ScoreCategory.ONES: 1,
  ScoreCategory.TWOS: 2,
  ScoreCategory.THREES: 3,
  ScoreCategory.FOURS: 4,
  ScoreCategory.FIVES: 5,
  ScoreCategory.SIXES: 6,
}

_BONUS_PER_CATEGORY = _VARIANT.bonus_score / len(_UPPER_FACE)


def _upper_bonus_progress(scores: dict) -> float:
  upper_total = sum(scores.get(cat, 0) for cat in UPPER_CATEGORIES)
  return min(upper_total / _VARIANT.bonus_threshold, 1.0) * _VARIANT.bonus_score


class YatzyEnv(gym.Env):
  metadata = {'render_modes': []}

  def __init__(self, mask_yatzy: bool = False) -> None:
    super().__init__()
    self._mask_yatzy = mask_yatzy
    self.observation_space = spaces.Box(
      low=np.array(
        [1.0] * DICE_COUNT +          # dice values min
        [0.0] * DICE_COUNT +          # kept flags min
        [0.0, 0.0, 0.0] +             # rolls_remaining, saved_rolls, has_rolled min
        [-1.0] * SCORE_ACTIONS,       # category scores min
        dtype=np.float32,
      ),
      high=np.array(
        [6.0] * DICE_COUNT +          # dice values max
        [1.0] * DICE_COUNT +          # kept flags max
        [3.0, float(MAX_SAVED_ROLLS), 1.0] +  # rolls_remaining, saved_rolls, has_rolled max
        [100.0] * SCORE_ACTIONS,      # category scores max
        dtype=np.float32,
      ),
      dtype=np.float32,
    )
    self.action_space = spaces.Discrete(TOTAL_ACTIONS)
    self._state: GameState = engine.new_game()

  def reset(
    self,
    *,
    seed: int | None = None,
    options: dict | None = None,
  ) -> tuple[np.ndarray, dict]:
    super().reset(seed=seed)
    self._state = engine.new_game()
    return _observe(self._state), {'action_mask': _action_mask(self._state, self._mask_yatzy)}

  def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict]:
    mask = _action_mask(self._state, self._mask_yatzy)
    if not mask[action]:
      valid = np.where(mask)[0]
      if len(valid) == 0:
        return _observe(self._state), 0.0, True, False, {'action_mask': mask}
      action = int(valid[0])

    if action < ROLL_ACTIONS:
      keep = [(action >> i) & 1 == 1 for i in range(DICE_COUNT)]
      self._state = engine.roll(self._state, keep)
      reward = 0.0
    else:
      category_index = action - ROLL_ACTIONS
      category = CATEGORIES[category_index]
      self._state, points = engine.score(self._state, category)
      reward = float(points)

      if category in _UPPER_FACE and points >= _UPPER_FACE[category] * 4:
        reward += _BONUS_PER_CATEGORY

      if self._state.is_done:
        reward += _upper_bonus_progress(self._state.scores)

    return (
      _observe(self._state),
      reward,
      self._state.is_done,
      False,  # truncated
      {'action_mask': _action_mask(self._state, self._mask_yatzy)},
    )

  def action_masks(self) -> np.ndarray:
    return _action_mask(self._state, self._mask_yatzy)
