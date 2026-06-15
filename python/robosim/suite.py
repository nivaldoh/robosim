"""The benchmark suite: a registry mapping versioned ids to (task, config) plus
the published held-out evaluation seeds.

Bumping a task version is required on ANY change to its reward, success
predicate, horizon, or reset distribution (see docs/DESIGN.md, hard rule #7)."""

from __future__ import annotations

import gymnasium as gym

from .env import Environment
from .gym_env import RoboEnv
from .physics import Physics
from .tasks.point_reach import PointReachTask

# --- PointReach-v0 -----------------------------------------------------------
POINT_REACH_DT = 0.01
POINT_REACH_CONTROL_TIMESTEP = 0.02
POINT_REACH_MAX_STEPS = 100


def make_point_reach(render_mode: str | None = None, **task_kwargs) -> RoboEnv:
    physics = Physics.point_mass(mass=1.0, dt=POINT_REACH_DT, gravity=(0.0, 0.0, 0.0))
    task = PointReachTask(**task_kwargs)
    env = Environment(physics, task, control_timestep=POINT_REACH_CONTROL_TIMESTEP)
    return RoboEnv(env, render_mode=render_mode)


# Held-out evaluation seeds (published, disjoint from any training seeds).
EVAL_SEEDS: dict[str, list[int]] = {
    "PointReach-v0": list(range(1000, 1020)),
}

_REGISTERED = False


def register_envs() -> None:
    """Register robosim environments with Gymnasium (idempotent)."""
    global _REGISTERED
    if _REGISTERED:
        return
    gym.register(
        id="PointReach-v0",
        entry_point="robosim.suite:make_point_reach",
        max_episode_steps=POINT_REACH_MAX_STEPS,
    )
    _REGISTERED = True
