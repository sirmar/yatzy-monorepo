import argparse
import numpy as np
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from rl.env.yatzy_env import YatzyEnv, ROLL_ACTIONS
from app.sim import engine
from yatzy_rules.scoring_rules import UPPER_CATEGORIES, BONUS_THRESHOLD, BONUS_SCORE
from yatzy_rules.score_category import ScoreCategory


def mask_fn(env: YatzyEnv) -> list:
  return env.action_masks()


def run_episode(
  model: MaskablePPO, deterministic: bool = True
) -> tuple[int, dict, int, int]:
  env = YatzyEnv()
  obs, _ = env.reset()
  done = False
  rolls_banked = 0
  rolls_spent = 0

  while not done:
    action = int(
      model.predict(obs, action_masks=env.action_masks(), deterministic=deterministic)[
        0
      ]
    )

    if action < ROLL_ACTIONS:
      if env._state.rolls_remaining == 0:
        rolls_spent += 1
    else:
      rolls_banked += env._state.rolls_remaining

    obs, _, terminated, truncated, _ = env.step(action)
    done = terminated or truncated

  final = engine.final_score(env._state)
  return final, dict(env._state.scores), rolls_banked, rolls_spent


def _worker(args: tuple) -> tuple[int, dict, int, int]:
  model_path, deterministic = args
  import os
  import sys

  env = ActionMasker(YatzyEnv(), mask_fn)
  with open(os.devnull, 'w') as devnull:
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = devnull, devnull
    try:
      model = MaskablePPO.load(model_path, env=env, device='cpu')
    finally:
      sys.stdout, sys.stderr = old_out, old_err
  return run_episode(model, deterministic=deterministic)


def evaluate(
  model_path: str, n_episodes: int, deterministic: bool, workers: int
) -> None:
  scores = []
  bonus_earned = 0
  yatzy_scored = 0
  upper_totals = []
  total_banked = []
  total_spent = []

  with Pool(workers) as pool:
    results = list(
      tqdm(
        pool.imap_unordered(_worker, [(model_path, deterministic)] * n_episodes),
        total=n_episodes,
      )
    )

  for final, scorecard, banked, spent in results:
    scores.append(final)
    total_banked.append(banked)
    total_spent.append(spent)

    upper_total = sum(scorecard.get(cat, 0) for cat in UPPER_CATEGORIES)
    upper_totals.append(upper_total)
    if upper_total >= BONUS_THRESHOLD:
      bonus_earned += 1
    if scorecard.get(ScoreCategory.MAXI_YATZY, 0) == 100:
      yatzy_scored += 1

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
  print(
    f'Bonus earned: {bonus_earned}/{n_episodes} ({100 * bonus_earned / n_episodes:.1f}%)'
  )
  print(
    f'Maxi Yatzy:   {yatzy_scored}/{n_episodes} ({100 * yatzy_scored / n_episodes:.1f}%)'
  )
  print(
    f'Upper mean:   {upper_arr.mean():.1f} (threshold: {BONUS_THRESHOLD}, bonus: {BONUS_SCORE})'
  )
  print()
  print(f'Rolls banked: {banked_arr.mean():.1f} avg, {banked_arr.sum()} total')
  print(f'Rolls spent:  {spent_arr.mean():.1f} avg, {spent_arr.sum()} total')
  wasted = banked_arr.sum() - spent_arr.sum()
  print(f'Rolls wasted: {wasted} total (banked but never spent)')

  env = ActionMasker(YatzyEnv(), mask_fn)
  model = MaskablePPO.load(model_path, env=env, device='cpu')
  _, scorecard, _, _ = run_episode(model, deterministic=deterministic)
  upper_total = sum(scorecard.get(cat, 0) for cat in UPPER_CATEGORIES)
  print(f'\nSample scorecard (upper total: {upper_total}):')
  for cat, pts in scorecard.items():
    marker = ' *' if cat in UPPER_CATEGORIES else ''
    print(f'  {str(cat):<25} {pts}{marker}')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--model', type=str, required=True)
  parser.add_argument('--episodes', type=int, default=1000)
  parser.add_argument('--stochastic', action='store_true')
  parser.add_argument('--workers', type=int, default=cpu_count())
  args = parser.parse_args()

  evaluate(
    model_path=args.model,
    n_episodes=args.episodes,
    deterministic=not args.stochastic,
    workers=args.workers,
  )
