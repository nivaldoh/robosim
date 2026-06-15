"""Minimal array specs, decoupling Tasks from Gymnasium.

A Task describes its observation/action arrays with a plain `BoundedArraySpec`
(shape + bounds + dtype). The Gymnasium adapter converts these to `spaces.Box`.
This keeps the Task layer free of any Gymnasium dependency (dm_control-style)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class BoundedArraySpec:
    shape: tuple[int, ...]
    low: Any  # scalar or array-like, broadcastable to `shape`
    high: Any
    dtype: Any = np.float32
    name: str = field(default="")
