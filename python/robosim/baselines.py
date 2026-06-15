"""Baseline policies for sanity-checking the pipeline.

A policy is a callable `policy(observation) -> action` with an optional
`reset()`. The PD controller is the Milestone 0 "end-to-end proof": it must beat
the random policy on PointReach, demonstrating that every layer is wired up."""

from __future__ import annotations

import numpy as np


class RandomPolicy:
    def __init__(self, action_space):
        self.action_space = action_space

    def reset(self) -> None:
        pass

    def __call__(self, observation) -> np.ndarray:
        return self.action_space.sample()


class PointReachPD:
    """PD controller for PointReach. Reads [pos(3), vel(3), goal(3)] from the
    observation and outputs a normalized force that drives the mass to the goal
    and settles (gains act in normalized action space, then are clipped)."""

    def __init__(self, kp: float = 10.0, kd: float = 3.0):
        self.kp = float(kp)
        self.kd = float(kd)

    def reset(self) -> None:
        pass

    def __call__(self, observation) -> np.ndarray:
        obs = np.asarray(observation, dtype=float)
        position, velocity, goal = obs[0:3], obs[3:6], obs[6:9]
        action = self.kp * (goal - position) - self.kd * velocity
        return np.clip(action, -1.0, 1.0).astype(np.float32)
