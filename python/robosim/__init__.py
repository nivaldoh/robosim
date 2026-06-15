"""robosim — a minimal robotics benchmark built from scratch.

The compiled C++ core lives in the private ``robosim._core`` extension module;
the Python benchmark layer (Physics handle, Tasks, Environment, Gymnasium
adapter, eval, viz) is built on top of it.
"""

from . import baselines, rewards
from ._core import Model, System
from .env import Environment
from .physics import Physics
from .specs import BoundedArraySpec
from .tasks.base import Task
from .tasks.point_reach import PointReachTask

__all__ = [
    "Model",
    "System",
    "Physics",
    "Environment",
    "BoundedArraySpec",
    "Task",
    "PointReachTask",
    "rewards",
    "baselines",
]
__version__ = "0.0.0"

# Register Gymnasium environments when gymnasium is available (the `env` extra).
try:
    import gymnasium as _gym  # noqa: F401

    from . import suite
    from .gym_env import RoboEnv

    suite.register_envs()
    __all__ += ["suite", "RoboEnv"]
    _HAS_GYM = True
except ImportError:  # pragma: no cover
    _HAS_GYM = False
