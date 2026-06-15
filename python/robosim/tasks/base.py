"""Task base class (dm_control-style).

A Task defines what to observe, how to reward, and when an episode terminates,
plus the FROZEN sparse success predicate the eval harness reports. It receives
`physics` as an argument to every method and never caches it; one Physics can
back many Tasks."""

from __future__ import annotations

import abc

import numpy as np

from ..physics import Physics
from ..specs import BoundedArraySpec


class Task(abc.ABC):
    @abc.abstractmethod
    def initialize_episode(self, physics: Physics, rng: np.random.Generator) -> None:
        """Set the initial state (using `rng` for all randomization)."""

    @abc.abstractmethod
    def before_step(self, action: np.ndarray, physics: Physics) -> None:
        """Translate a normalized action into a control and apply it to physics."""

    @abc.abstractmethod
    def get_observation(self, physics: Physics) -> np.ndarray:
        """Return the observation (must match `observation_spec`)."""

    @abc.abstractmethod
    def get_reward(self, physics: Physics) -> float:
        """Return the (shaped) reward for the current state."""

    @abc.abstractmethod
    def get_terminated(self, physics: Physics) -> bool:
        """True iff the episode reached an MDP-terminal state (success/failure).

        This is NOT the time limit — truncation is the Gymnasium TimeLimit
        wrapper's job."""

    @abc.abstractmethod
    def success(self, physics: Physics) -> bool:
        """Frozen sparse success predicate, reported by the eval harness.

        Must be independent of the shaped `get_reward` so reward hacking can't
        masquerade as success."""

    @property
    @abc.abstractmethod
    def observation_spec(self) -> BoundedArraySpec: ...

    @property
    @abc.abstractmethod
    def action_spec(self) -> BoundedArraySpec: ...
