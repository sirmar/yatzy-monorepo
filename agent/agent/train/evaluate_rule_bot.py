import numpy as np
from multiprocessing import Pool, cpu_count
from sim import engine, rule_bot
from yatzy_rules.scoring_rules import UPPER_CATEGORIES, BONUS_THRESHOLD, BONUS_SCORE
from yatzy_rules.score_category import ScoreCategory


def run_episode(verbose: bool = False) -> tuple[int, dict, int, int, int]:
  state = engine.new_game()
  rolls_banked = 0
  rolls_spent = 0
  turn = 0
  chance_turn = -1
  while not state.is_done:
    act = rule_bot.action(state)
    if isinstance(act, list):
      if state.rolls_remaining == 0:
        rolls_spent += 1
      if verbose and state.has_rolled:
        kept_dice = [d for d, k in zip(state.dice, act) if k]
        dice_str = ' '.join(str(d) for d in state.dice)
        keep_str = ' '.join(str(d) for d in kept_dice)
        print(f'  {"roll":<6}  [{dice_str}]  keep [{keep_str:<11}]  rolls_left={state.rolls_remaining}  saved={state.saved_rolls}')
      state = engine.roll(state, act)
    else:
      rolls_banked += state.rolls_remaining
      category = act
      turn += 1
      if category == ScoreCategory.CHANCE:
        chance_turn = turn
      if verbose:
        dice_str = ' '.join(str(d) for d in state.dice)
        print(f'  {"score":<6}  [{dice_str}]  keep [{dice_str:<11}]  rolls_left={state.rolls_remaining}  saved={state.saved_rolls}')
      state, points = engine.score(state, category)
      if verbose:
        print(f'  --> {category.name:<22} {points:>3} pts  (turn {turn})')
        print()
  return engine.final_score(state), dict(state.scores), rolls_banked, rolls_spent, chance_turn


def evaluate(n_episodes: int = 10000, verbose_episodes: int = 0, workers: int = cpu_count()) -> None:
  # Run verbose episodes sequentially first
  results = []
  for i in range(min(verbose_episodes, n_episodes)):
    print(f'\n=== Game {i + 1} ===')
    result = run_episode(verbose=True)
    upper_total = sum(result[1].get(cat, 0) for cat in UPPER_CATEGORIES)
    print(f'  Final score: {result[0]}  (upper: {upper_total})')
    results.append(result)

  # Run remaining episodes in parallel
  remaining = n_episodes - len(results)
  if remaining > 0:
    with Pool(workers) as pool:
      results += pool.map(run_episode, [False] * remaining)

  scores = []
  bonus_earned = 0
  yatzy_scored = 0
  upper_totals = []
  upper_cat_scores: dict[ScoreCategory, list[int]] = {cat: [] for cat in UPPER_CATEGORIES}
  upper_cat_zeros: dict[ScoreCategory, int] = {cat: 0 for cat in UPPER_CATEGORIES}
  total_banked = []
  total_spent = []
  chance_turns = []

  for final, scorecard, banked, spent, chance_turn in results:
    scores.append(final)
    total_banked.append(banked)
    total_spent.append(spent)
    upper_total = sum(scorecard.get(cat, 0) for cat in UPPER_CATEGORIES)
    upper_totals.append(upper_total)
    if upper_total >= BONUS_THRESHOLD:
      bonus_earned += 1
    if scorecard.get(ScoreCategory.MAXI_YATZY, 0) == 100:
      yatzy_scored += 1
    for cat in UPPER_CATEGORIES:
      score = scorecard.get(cat, 0)
      upper_cat_scores[cat].append(score)
      if score == 0:
        upper_cat_zeros[cat] += 1
    if chance_turn >= 0:
      chance_turns.append(chance_turn)

  scores_arr = np.array(scores)
  upper_arr = np.array(upper_totals)
  banked_arr = np.array(total_banked)
  spent_arr = np.array(total_spent)

  print(f'Episodes:     {n_episodes}')
  print(f'Mean score:   {scores_arr.mean():.1f}')
  print(f'Std:          {scores_arr.std():.1f}')
  print(f'Min:          {scores_arr.min()}')
  print(f'Max:          {scores_arr.max()}')
  print(f'Median:       {np.median(scores_arr):.1f}')
  print()
  print(f'Bonus earned: {bonus_earned}/{n_episodes} ({100 * bonus_earned / n_episodes:.1f}%)')
  print(f'Maxi Yatzy:   {yatzy_scored}/{n_episodes} ({100 * yatzy_scored / n_episodes:.1f}%)')
  print(f'Upper mean:   {upper_arr.mean():.1f} (threshold: {BONUS_THRESHOLD}, bonus: {BONUS_SCORE})')
  print()
  _face = {
    ScoreCategory.ONES: 1, ScoreCategory.TWOS: 2, ScoreCategory.THREES: 3,
    ScoreCategory.FOURS: 4, ScoreCategory.FIVES: 5, ScoreCategory.SIXES: 6,
  }
  _upper_target = {cat: _face[cat] * 4 for cat in UPPER_CATEGORIES}
  print(f'  {"category":<10}  {"avg":>5}  {"target":>6}  {"diff":>5}  {"zeros":>6}')
  for cat in sorted(UPPER_CATEGORIES, key=lambda c: _face[c]):
    avg = np.mean(upper_cat_scores[cat])
    target = _upper_target[cat]
    diff = avg - target
    zero_pct = 100 * upper_cat_zeros[cat] / n_episodes
    print(f'  {cat.name:<10}  {avg:>5.1f}  {target:>6}  {diff:>+5.1f}  {zero_pct:>5.1f}%')
  print()
  print(f'Rolls banked: {banked_arr.mean():.1f} avg, {banked_arr.sum()} total')
  print(f'Rolls spent:  {spent_arr.mean():.1f} avg, {spent_arr.sum()} total')
  wasted = banked_arr.sum() - spent_arr.sum()
  print(f'Rolls wasted: {wasted} total (banked but never spent)')
  print()
  chance_arr = np.array(chance_turns)
  print(f'Chance used:  {len(chance_turns)}/{n_episodes} games ({100 * len(chance_turns) / n_episodes:.1f}%)')
  if len(chance_turns):
    print(f'Chance turn:  avg={chance_arr.mean():.1f}  min={chance_arr.min()}  max={chance_arr.max()}')


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--episodes', type=int, default=10000)
  parser.add_argument('--verbose', type=int, default=0)
  parser.add_argument('--workers', type=int, default=cpu_count())
  args = parser.parse_args()
  evaluate(n_episodes=args.episodes, verbose_episodes=args.verbose, workers=args.workers)
