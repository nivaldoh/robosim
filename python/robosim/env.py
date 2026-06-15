"""The generic control loop (dm_control's L4 "Environment").

Ties a Physics and a Task together and decouples the agent's control timestep
from the physics substep (`n_substeps = control_timestep / dt`, integer). It is
deliberately NOT Gymnasium-aware: it returns (obs, reward, terminated, info);
truncation (the time limit) is the Gymnasium TimeLimit wrapper's job."""

from __future__ import annotations

import numpy as np

from .physics import Physics
from .tasks.base import Task


class Environment:
    def __init__(self, physics: Physics, task: Task, control_timestep: float = 0.02):
        self._physics = physics
        self._task = task
        self._control_timestep = float(control_timestep)
        ratio = control_timestep / physics.dt
        self._n_substeps = int(round(ratio))
        if self._n_substeps < 1 or abs(ratio - self._n_substeps) > 1e-9:
            raise ValueError(
                f"control_timestep ({control_timestep}) must be a positive integer "
                f"multiple of the physics dt ({physics.dt})."
            )

    @property
    def physics(self) -> Physics:
        return self._physics

    @property
    def task(self) -> Task:
        return self._task

    @property
    def control_timestep(self) -> float:
        return self._control_timestep

    def reset(self, rng: np.random.Generator) -> np.ndarray:
        self._task.initialize_episode(self._physics, rng)
        return self._task.get_observation(self._physics)

    def step(self, action):
        self._task.before_step(action, self._physics)
        self._physics.step(self._n_substeps)
        obs = self._task.get_observation(self._physics)
        reward = self._task.get_reward(self._physics)
        diverged = self._physics.diverged
        terminated = bool(self._task.get_terminated(self._physics) or diverged)
        info = {
            "is_success": bool(self._task.success(self._physics)),
            "diverged": bool(diverged),
        }
        return obs, float(reward), terminated, info
