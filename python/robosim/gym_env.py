"""Gymnasium adapter (L5).

Wraps a generic `Environment` as a `gymnasium.Env`: builds Box spaces from the
Task specs, routes all randomness through `self.np_random` (which also seeds the
C++ RNG), and returns the modern (obs, info) / 5-tuple API. Truncation is left
to the TimeLimit wrapper applied by `gymnasium.make`."""

from __future__ import annotations

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .env import Environment
from .specs import BoundedArraySpec


def _to_box(spec: BoundedArraySpec) -> spaces.Box:
    low = np.broadcast_to(np.asarray(spec.low, dtype=spec.dtype), spec.shape)
    high = np.broadcast_to(np.asarray(spec.high, dtype=spec.dtype), spec.shape)
    return spaces.Box(low=low.copy(), high=high.copy(), shape=spec.shape, dtype=spec.dtype)


class RoboEnv(gym.Env):
    metadata = {"render_modes": ["rgb_array", "rerun"], "render_fps": 50}

    def __init__(self, environment: Environment, render_mode: str | None = None):
        self._env = environment
        self.observation_space = _to_box(environment.task.observation_spec)
        self.action_space = _to_box(environment.task.action_spec)
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    @property
    def environment(self) -> Environment:
        """The underlying generic Environment (physics + task), for viz/eval."""
        return self._env

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        # Seed the C++ RNG from the same Gymnasium seed so the whole pipeline is
        # reproducible from one integer.
        self._env.physics.seed(int(self.np_random.integers(2**31 - 1)))
        obs = self._env.reset(self.np_random).astype(np.float32)
        return obs, {}

    def step(self, action):
        obs, reward, terminated, info = self._env.step(action)
        # TimeLimit wrapper owns truncation; the base env never truncates.
        return obs.astype(np.float32), reward, terminated, False, info

    def render(self):
        # 3D visualization is provided out-of-band by robosim.viz.PointReachViewer,
        # which logs the underlying Environment (see scripts/demo_pointreach.py).
        return None
