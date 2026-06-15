"""3D visualization via rerun.io (L8 of the stack).

The C++ core exposes body world positions; this logs the point mass, its target,
and a trail to a rerun recording. Two ways to view:

- **save** (default, headless/WSL-friendly): pass ``save_path=...`` and open the
  resulting file with ``rerun episode.rrd`` (or the web viewer).
- **spawn** (desktop with a display): pass ``spawn=True`` to open the native
  viewer live.

Tested against rerun-sdk 0.33 (time API: ``set_time(timeline, sequence=/duration=)``).
"""

from __future__ import annotations

import numpy as np


class PointReachViewer:
    GOAL_COLOR = (40, 200, 80)
    MASS_COLOR = (60, 120, 255)
    TRAIL_COLOR = (220, 220, 70)
    MASS_RADIUS = 0.04

    def __init__(self, app_id: str = "robosim/PointReach", *, spawn=False, save_path=None):
        import rerun as rr

        self._rr = rr
        self._rec = rr.RecordingStream(app_id)
        if save_path is not None:
            self._rec.save(str(save_path))
        if spawn:
            self._rec.spawn()  # requires a display; use save on headless/WSL
        self._trail: list[np.ndarray] = []
        self._step = 0

    def _set_time(self, environment) -> None:
        self._rec.set_time("step", sequence=self._step)
        self._rec.set_time("sim_time", duration=float(environment.physics.time))

    def reset(self, environment) -> None:
        self._trail = []
        self._step = 0
        self._set_time(environment)
        goal = np.asarray(environment.task.goal, dtype=float)
        radius = float(environment.task.success_radius)
        self._rec.log(
            "world/goal",
            self._rr.Points3D([goal], radii=[radius], colors=[self.GOAL_COLOR]),
        )
        self._log_mass(environment)

    def step(self, environment) -> None:
        self._step += 1
        self._set_time(environment)
        self._log_mass(environment)

    def _log_mass(self, environment) -> None:
        pos = np.asarray(environment.physics.position(), dtype=float)
        self._rec.log(
            "world/mass",
            self._rr.Points3D([pos], radii=[self.MASS_RADIUS], colors=[self.MASS_COLOR]),
        )
        self._trail.append(pos.copy())
        if len(self._trail) >= 2:
            self._rec.log(
                "world/trail",
                self._rr.LineStrips3D(
                    [np.asarray(self._trail)], colors=[self.TRAIL_COLOR]
                ),
            )

    def close(self) -> None:
        try:
            self._rec.flush()
        except Exception:
            pass

    def __enter__(self) -> "PointReachViewer":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
