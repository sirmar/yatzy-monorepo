import argparse
import numpy as np
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.callbacks import MaskableEvalCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import CheckpointCallback
from agent.env.yatzy_env import YatzyEnv
from sim import engine
from yatzy_rules.scoring_rules import UPPER_CATEGORIES, BONUS_THRESHOLD
from yatzy_rules.score_category import ScoreCategory

_STAT_EPISODES = 50


def _collect_stats(model: MaskablePPO, env: YatzyEnv) -> tuple[float, float, float, float]:
  bonus, yatzy, scores = 0, 0, []
  for _ in range(_STAT_EPISODES):
    obs, _ = env.reset()
    done = False
    while not done:
      action = int(model.predict(obs, action_masks=env.action_masks(), deterministic=True)[0])
      obs, _, terminated, truncated, _ = env.step(action)
      done = terminated or truncated
    state = env.env._state
    scores.append(engine.final_score(state) if state.is_done else sum(state.scores.values()))
    upper = sum(state.scores.get(cat, 0) for cat in UPPER_CATEGORIES)
    if upper >= BONUS_THRESHOLD:
      bonus += 1
    if state.scores.get(ScoreCategory.MAXI_YATZY, 0) == 100:
      yatzy += 1
  arr = np.array(scores)
  return arr.mean(), arr.std(), bonus / _STAT_EPISODES * 100, yatzy / _STAT_EPISODES * 100


class QuietEvalCallback(MaskableEvalCallback):
  def __init__(self, *args, stat_env: YatzyEnv, **kwargs):
    super().__init__(*args, **kwargs)
    self._stat_env = stat_env

  def _on_step(self) -> bool:
    prev_best = self.best_mean_reward
    prev = self.last_mean_reward
    result = super()._on_step()
    if self.last_mean_reward != prev:
      new_best = self.best_mean_reward > prev_best
      mean, std, bonus_pct, yatzy_pct = _collect_stats(self.model, self._stat_env)
      suffix = '  (new best)' if new_best else ''
      print(f'  {self.num_timesteps:>10}  {self.last_mean_reward:>8.1f}  {mean:>7.1f}  {std:>6.1f}  {bonus_pct:>6.1f}%  {yatzy_pct:>6.1f}%{suffix}')
    return result


def mask_fn(env: YatzyEnv) -> list:
  return env.action_masks()


def make_env(mask_yatzy: bool = False):
  def _make():
    env = YatzyEnv(mask_yatzy=mask_yatzy)
    return ActionMasker(env, mask_fn)
  return _make


def make_callbacks(checkpoint_dir: str, log_dir: str, n_envs: int, mask_yatzy: bool, prefix: str):
  eval_env = make_vec_env(make_env(mask_yatzy), n_envs=8)
  stat_env = YatzyEnv(mask_yatzy=mask_yatzy)
  stat_env = ActionMasker(stat_env, mask_fn)
  return [
    CheckpointCallback(
      save_freq=max(100_000 // n_envs, 1),
      save_path=checkpoint_dir,
      name_prefix=prefix,
      verbose=0,
    ),
    QuietEvalCallback(
      eval_env,
      stat_env=stat_env,
      best_model_save_path=checkpoint_dir,
      log_path=log_dir,
      eval_freq=max(50_000 // n_envs, 1),
      n_eval_episodes=100,
      deterministic=True,
      verbose=0,
    ),
  ]


def train(
  phase1_timesteps: int,
  phase2_timesteps: int,
  n_envs: int,
  checkpoint_dir: str,
  log_dir: str,
  resume: str | None,
) -> None:
  if resume:
    vec_env = make_vec_env(make_env(mask_yatzy=False), n_envs=n_envs)
    model = MaskablePPO.load(resume, env=vec_env, verbose=0, tensorboard_log=log_dir)
    print(f'Resuming from {resume}')
    model.learn(
      total_timesteps=phase2_timesteps,
      callback=make_callbacks(checkpoint_dir, log_dir, n_envs, False, 'yatzy_ppo'),
      reset_num_timesteps=False,
    )
  else:
    vec_env = make_vec_env(make_env(mask_yatzy=True), n_envs=n_envs)
    model = MaskablePPO(
      'MlpPolicy',
      vec_env,
      verbose=0,
      tensorboard_log=log_dir,
      n_steps=4096,
      batch_size=512,
      policy_kwargs={'net_arch': [128, 128]},
    )

    if phase1_timesteps > 0:
      print(f'Phase 1: {phase1_timesteps} timesteps (Yatzy masked)')
      print(f'  {"timesteps":>10}  {"reward":>8}  {"score":>7}  {"std":>6}  {"bonus":>6}  {"yatzy":>6}')
      model.learn(
        total_timesteps=phase1_timesteps,
        callback=make_callbacks(checkpoint_dir, log_dir, n_envs, True, 'phase1'),
        reset_num_timesteps=True,
      )

    if phase2_timesteps > 0:
      print(f'Phase 2: {phase2_timesteps} timesteps (Yatzy unmasked)')
      print(f'  {"timesteps":>10}  {"reward":>8}  {"score":>7}  {"std":>6}  {"bonus":>6}  {"yatzy":>6}')
      vec_env2 = make_vec_env(make_env(mask_yatzy=False), n_envs=n_envs)
      model.set_env(vec_env2)
      model.learn(
        total_timesteps=phase2_timesteps,
        callback=make_callbacks(checkpoint_dir, log_dir, n_envs, False, 'phase2'),
        reset_num_timesteps=False,
      )

  model.save(f'{checkpoint_dir}/yatzy_ppo_final')
  print(f'Model saved to {checkpoint_dir}/yatzy_ppo_final')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--phase1-timesteps', type=int, default=2_000_000)
  parser.add_argument('--phase2-timesteps', type=int, default=1_000_000)
  parser.add_argument('--envs', type=int, default=32)
  parser.add_argument('--checkpoint-dir', type=str, default='checkpoints')
  parser.add_argument('--log-dir', type=str, default='logs')
  parser.add_argument('--resume', type=str, default=None, help='Resume phase 2 from checkpoint')
  args = parser.parse_args()

  train(
    phase1_timesteps=args.phase1_timesteps,
    phase2_timesteps=args.phase2_timesteps,
    n_envs=args.envs,
    checkpoint_dir=args.checkpoint_dir,
    log_dir=args.log_dir,
    resume=args.resume,
  )
