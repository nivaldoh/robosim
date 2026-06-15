"""PointReach-3D — the Milestone 0 tracer-bullet task.

A point mass must reach a randomly placed target. Dynamics are a pure double
integrator (closed-form verifiable), and "reach a target" is the most basic
manipulation primitive, so this grows naturally into the 2-link reacher later.

Observation (9-D): [pos(3), vel(3), goal(3)]
Action (3-D):      normalized force in [-1, 1], scaled by `force_mag`
Reward:            smooth `tolerance` on distance-to-goal, minus a small control cost
Success (frozen):  ||pos - goal|| < success_radius
Terminated:        success (terminate on reaching the goal)
"""

from __future__ import annotations

import numpy as np

from .. import rewards
from ..physics import Physics
from ..specs import BoundedArraySpec
from .base import Task


class PointReachTask(Task):
    def __init__(
        self,
        workspace: float = 0.6,
        success_radius: float = 0.05,
        force_mag: float = 10.0,
        control_cost: float = 0.01,
        reward_margin: float = 0.4,
    ):
        self.workspace = float(workspace)
        self.success_radius = float(success_radius)
        self.force_mag = float(force_mag)
        self.control_cost = float(control_cost)
        self.reward_margin = float(reward_margin)
        self._goal = np.zeros(3)
        self._last_action = np.zeros(3)

    def initialize_episode(self, physics: Physics, rng: np.random.Generator) -> None:
        position = rng.uniform(-self.workspace, self.workspace, size=3)
        self._goal = rng.uniform(-self.workspace, self.workspace, size=3)
        self._last_action = np.zeros(3)
        physics.reset_state(position, np.zeros(3))

    def before_step(self, action: np.ndarray, physics: Physics) -> None:
        a = np.clip(np.asarray(action, dtype=float), -1.0, 1.0)
        self._last_action = a
        physics.set_control(a * self.force_mag)

    def get_observation(self, physics: Physics) -> np.ndarray:
        return np.concatenate(
            [physics.position(), physics.velocity(), self._goal]
        ).astype(np.float32)

    def _distance(self, physics: Physics) -> float:
        return float(np.linalg.norm(physics.position() - self._goal))

    def get_reward(self, physics: Physics) -> float:
        reach = rewards.tolerance(
            self._distance(physics),
            bounds=(0.0, self.success_radius),
            margin=self.reward_margin,
            sigmoid="long_tail",
        )
        ctrl_cost = self.control_cost * float(np.sum(np.square(self._last_action)))
        return float(reach) - ctrl_cost

    def get_terminated(self, physics: Physics) -> bool:
        return self.success(physics)

    def success(self, physics: Physics) -> bool:
        return self._distance(physics) < self.success_radius

    @property
    def goal(self) -> np.ndarray:
        return self._goal

    @property
    def observation_spec(self) -> BoundedArraySpec:
        inf = np.inf
        low = np.array(
            [-inf, -inf, -inf, -inf, -inf, -inf,
             -self.workspace, -self.workspace, -self.workspace],
            dtype=np.float32,
        )
        high = np.array(
            [inf, inf, inf, inf, inf, inf,
             self.workspace, self.workspace, self.workspace],
            dtype=np.float32,
        )
        return BoundedArraySpec((9,), low, high, np.float32, "observation")

    @property
    def action_spec(self) -> BoundedArraySpec:
        return BoundedArraySpec((3,), -1.0, 1.0, np.float32, "action")
