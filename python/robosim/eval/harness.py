"""Evaluation harness — turns env + fixed protocol into a benchmark number.

Credibility comes from protocol discipline, not harness complexity:
- a published, held-out eval seed list (``robosim.suite.EVAL_SEEDS``),
- the FROZEN sparse success predicate (``info["is_success"]``), never the
  shaped reward,
- deterministic, reproducible rollouts (same seeds -> identical metrics),
- per-episode raw scores recorded, not just the aggregate.

Deferred to a later milestone: rliable IQM + bootstrap CIs, performance
profiles, normalized scores. Until then a fixed seed set + success rate is the
cheapest credible number.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import gymnasium as gym
import numpy as np

from ..suite import EVAL_SEEDS

Policy = Callable[[np.ndarray], np.ndarray]
PolicyFn = Callable[[gym.Env], Policy]


@dataclass(frozen=True)
class EpisodeResult:
    seed: int
    episode_return: float
    success: bool
    length: int


@dataclass(frozen=True)
class EvalResult:
    env_id: str
    method: str
    benchmark_version: str
    num_eval_episodes: int
    success_rate: float
    mean_return: float
    episodes: tuple

    def row(self) -> dict:
        """The canonical, recordable results row (publishes per-episode scores)."""
        return {
            "method": self.method,
            "env_id": self.env_id,
            "benchmark_version": self.benchmark_version,
            "num_eval_episodes": self.num_eval_episodes,
            "success_rate": round(self.success_rate, 4),
            "mean_return": round(self.mean_return, 4),
            "raw_returns": [round(e.episode_return, 4) for e in self.episodes],
            "raw_success": [int(e.success) for e in self.episodes],
        }

    def format(self) -> str:
        return (
            f"{self.method:<12} {self.env_id:<16} "
            f"success={self.success_rate:5.2f}  return={self.mean_return:8.3f}  "
            f"(n={self.num_eval_episodes})"
        )


def run_episode(env: gym.Env, policy: Policy, seed: int) -> EpisodeResult:
    obs, _ = env.reset(seed=seed)
    if hasattr(policy, "reset"):
        policy.reset()
    total, success, length, done = 0.0, False, 0, False
    while not done:
        obs, reward, terminated, truncated, info = env.step(policy(obs))
        total += float(reward)
        length += 1
        success = success or bool(info.get("is_success", False))
        done = bool(terminated or truncated)
    return EpisodeResult(int(seed), total, success, length)


def evaluate(
    env_id: str,
    policy_fn: PolicyFn,
    *,
    method: str = "policy",
    seeds: Sequence[int] | None = None,
    benchmark_version: str = "0.0.0",
    env_kwargs: dict | None = None,
) -> EvalResult:
    """Run `policy_fn(env)` over the held-out eval seeds and aggregate metrics."""
    if seeds is None:
        seeds = EVAL_SEEDS[env_id]
    env = gym.make(env_id, **(env_kwargs or {}))
    try:
        policy = policy_fn(env)
        episodes = tuple(run_episode(env, policy, s) for s in seeds)
    finally:
        env.close()
    success_rate = float(np.mean([e.success for e in episodes]))
    mean_return = float(np.mean([e.episode_return for e in episodes]))
    return EvalResult(
        env_id, method, benchmark_version, len(episodes),
        success_rate, mean_return, episodes,
    )
