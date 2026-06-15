"""Milestone 0 tracer-bullet demo for PointReach-3D.

Threads EVERY layer end-to-end:
  C++ physics -> pybind11 -> Task -> Environment -> Gymnasium env
  -> 3D viz (rerun .rrd) -> seeded eval harness (a reproducible benchmark row).

Run:
    python scripts/demo_pointreach.py
    python scripts/demo_pointreach.py --seed 1003 --rrd /tmp/pointreach.rrd
    rerun /tmp/pointreach.rrd      # to view the 3D recording
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import gymnasium as gym

import robosim
from robosim.baselines import PointReachPD, RandomPolicy
from robosim.eval import evaluate
from robosim.viz import PointReachViewer

ENV_ID = "PointReach-v0"


def record_episode(seed: int, rrd_path: Path, spawn: bool = False):
    """Run one PD episode, logging the 3D trajectory to a rerun recording."""
    env = gym.make(ENV_ID)
    viewer = PointReachViewer(spawn=spawn, save_path=rrd_path)
    obs, _ = env.reset(seed=seed)
    environment = env.unwrapped.environment
    viewer.reset(environment)

    pd = PointReachPD()
    done, total, steps, info = False, 0.0, 0, {}
    while not done:
        obs, reward, terminated, truncated, info = env.step(pd(obs))
        viewer.step(environment)
        total += reward
        steps += 1
        done = terminated or truncated
    viewer.close()
    env.close()
    return total, steps, bool(info.get("is_success", False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1000)
    parser.add_argument("--rrd", type=Path, default=Path("pointreach.rrd"))
    parser.add_argument("--spawn", action="store_true", help="open the native rerun viewer (needs a display)")
    args = parser.parse_args()

    print("== Milestone 0 tracer bullet: PointReach-3D ==\n")

    # 1) Render one PD episode to a rerun .rrd.
    total, steps, success = record_episode(args.seed, args.rrd, spawn=args.spawn)
    print(f"[viz]  PD episode (seed={args.seed}): return={total:.3f}  steps={steps}  success={success}")
    print(f"[viz]  wrote {args.rrd}  ->  view with:  rerun {args.rrd}\n")

    # 2) Reproducible benchmark row on the held-out eval seeds.
    pd = evaluate(ENV_ID, lambda e: PointReachPD(), method="pd")
    rand = evaluate(ENV_ID, lambda e: RandomPolicy(e.action_space), method="random")
    print("[eval] held-out seeds:", robosim.suite.EVAL_SEEDS[ENV_ID])
    print("[eval]", pd.format())
    print("[eval]", rand.format())
    print("\n[row]", json.dumps(pd.row(), indent=2))


if __name__ == "__main__":
    main()
