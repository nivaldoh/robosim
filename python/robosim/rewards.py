"""Smooth reward shaping, ported from dm_control's `rewards.tolerance`.

All shaped reward terms are kept in [0, 1] so they compose cleanly (by product
for AND, by mean for soft-OR). The frozen *sparse success predicate* lives on
the Task and is what the eval harness reports — never the shaped reward."""

from __future__ import annotations

import numpy as np


def _sigmoid(x, value_at_1, kind):
    """Maps distance x >= 0 to (0, 1], equal to 1 at x==0 and `value_at_1` at x==1."""
    if kind == "gaussian":
        scale = np.sqrt(-2.0 * np.log(value_at_1))
        return np.exp(-0.5 * (x * scale) ** 2)
    if kind == "long_tail":
        scale = np.sqrt(1.0 / value_at_1 - 1.0)
        return 1.0 / ((x * scale) ** 2 + 1.0)
    if kind == "linear":
        scale = 1.0 - value_at_1
        return np.clip(1.0 - x * scale, 0.0, 1.0)
    raise ValueError(f"unknown sigmoid {kind!r}")


def tolerance(
    x,
    bounds=(0.0, 0.0),
    margin=0.0,
    sigmoid="gaussian",
    value_at_margin=0.1,
):
    """1.0 when x is within `bounds`, falling smoothly to `value_at_margin` at a
    distance `margin` outside the bounds (and beyond, per the sigmoid)."""
    lower, upper = bounds
    if lower > upper:
        raise ValueError("bounds[0] must be <= bounds[1]")
    if margin < 0:
        raise ValueError("margin must be non-negative")

    x = np.asarray(x, dtype=float)
    in_bounds = np.logical_and(x >= lower, x <= upper)
    if margin == 0.0:
        value = np.where(in_bounds, 1.0, 0.0)
    else:
        d = np.where(x < lower, lower - x, x - upper) / margin
        value = np.where(in_bounds, 1.0, _sigmoid(d, value_at_margin, sigmoid))
    return float(value) if value.ndim == 0 else value
