"""The `Physics` handle: a thin semantic wrapper over the C++ `System`.

This is dm_control's L2 "Physics" — it gives Tasks meaningful named accessors
(`position()`, `velocity()`) instead of raw qpos/qvel indices. For the
Milestone 0 point mass these are trivial, but this is the seam where richer
accessors (e.g. `fingertip_position()`) will live for articulated models."""

from __future__ import annotations

import numpy as np

from ._core import Model, System


class Physics:
    def __init__(self, model: Model):
        self._model = model
        self._system = System(model)

    @classmethod
    def point_mass(cls, mass=1.0, dt=0.01, gravity=(0.0, 0.0, 0.0)) -> "Physics":
        return cls(Model(mass=mass, dt=dt, gravity=np.asarray(gravity, dtype=float)))

    # --- state mutation ---
    def reset_state(self, position, velocity) -> None:
        self._system.reset(
            np.asarray(position, dtype=float), np.asarray(velocity, dtype=float)
        )

    def set_control(self, u) -> None:
        self._system.set_control(np.asarray(u, dtype=float))

    def step(self, n_substeps: int = 1) -> None:
        self._system.step(int(n_substeps))

    def seed(self, s: int) -> None:
        self._system.seed(int(s))

    # --- named accessors ---
    def position(self) -> np.ndarray:
        return np.array(self._system.qpos)

    def velocity(self) -> np.ndarray:
        return np.array(self._system.qvel)

    @property
    def time(self) -> float:
        return self._system.time

    @property
    def diverged(self) -> bool:
        return self._system.diverged

    @property
    def dt(self) -> float:
        return self._model.dt

    @property
    def model(self) -> Model:
        return self._model
