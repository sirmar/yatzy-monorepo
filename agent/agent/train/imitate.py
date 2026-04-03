import argparse
import numpy as np
import torch
from sb3_contrib import MaskablePPO
from agent.env.yatzy_env import YatzyEnv, ROLL_ACTIONS, _observe, _action_mask
from app.sim import engine, rule_bot
from app.sim.game_state import CATEGORIES
from yatzy_rules.score_category import ScoreCategory as Category


def _to_env_action(act: list[bool] | Category) -> int:
  if isinstance(act, list):
    return sum(1 << i for i, k in enumerate(act) if k)
  return ROLL_ACTIONS + CATEGORIES.index(act)


def collect_episodes(n_episodes: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
  all_obs, all_actions, all_masks = [], [], []
  for _ in range(n_episodes):
    state = engine.new_game()
    while not state.is_done:
      obs = _observe(state)
      mask = _action_mask(state)
      act = rule_bot.action(state)
      env_act = _to_env_action(act)
      all_obs.append(obs)
      all_actions.append(env_act)
      all_masks.append(mask)
      if isinstance(act, list):
        state = engine.roll(state, act)
      else:
        state, _ = engine.score(state, act)
  return np.array(all_obs), np.array(all_actions), np.array(all_masks)


def train(
  n_episodes: int = 50_000,
  epochs: int = 20,
  batch_size: int = 512,
  lr: float = 3e-4,
  output: str = 'checkpoints/imitation',
) -> None:
  print(f'Collecting {n_episodes} episodes...')
  obs_arr, act_arr, mask_arr = collect_episodes(n_episodes)
  n_samples = len(obs_arr)
  print(f'Collected {n_samples} samples')

  env = YatzyEnv()
  model = MaskablePPO(
    'MlpPolicy',
    env,
    policy_kwargs={'net_arch': [64, 64]},
    verbose=0,
  )

  obs_t = torch.FloatTensor(obs_arr).to(model.device)
  act_t = torch.LongTensor(act_arr).to(model.device)
  mask_t = torch.BoolTensor(mask_arr).to(model.device)

  optimizer = torch.optim.Adam(model.policy.parameters(), lr=lr)

  for epoch in range(1, epochs + 1):
    indices = np.random.permutation(n_samples)
    total_loss = 0.0
    n_batches = 0
    for start in range(0, n_samples, batch_size):
      idx = indices[start:start + batch_size]
      _, log_probs, _ = model.policy.evaluate_actions(
        obs_t[idx],
        act_t[idx],
        action_masks=mask_t[idx],
      )
      loss = -log_probs.mean()
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()
      total_loss += loss.item()
      n_batches += 1
    print(f'Epoch {epoch}/{epochs}  loss={total_loss / n_batches:.4f}')

  model.save(output)
  print(f'Saved to {output}')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--episodes', type=int, default=50_000)
  parser.add_argument('--epochs', type=int, default=20)
  parser.add_argument('--batch-size', type=int, default=512)
  parser.add_argument('--lr', type=float, default=3e-4)
  parser.add_argument('--output', type=str, default='checkpoints/imitation')
  args = parser.parse_args()
  train(
    n_episodes=args.episodes,
    epochs=args.epochs,
    batch_size=args.batch_size,
    lr=args.lr,
    output=args.output,
  )
