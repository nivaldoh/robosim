---
name: define-reward
description: Build and validate a robosim shaped reward from rewards.tolerance blocks (all terms in [0,1], composed by product/mean), keeping it decoupled from the sparse success predicate. Use when designing/changing a task reward. STUB — to be filled at Milestone 1+.
---

# define-reward (stub — fill at Milestone 1)

Will document: compose shaped rewards from `robosim.rewards.tolerance` (all terms
in `[0,1]`; AND = product, soft-OR = mean); optionally wrap a dense term as a
potential difference `Φ = -dist` for policy-invariance; and ASSERT that the
sparse `success()` predicate is independent and is what eval reports.

Reference today: `tasks/point_reach.py::get_reward`, `rewards.py`.
