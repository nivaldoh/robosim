---
name: bump-task-version
description: Detect a benchmark-breaking change to a robosim task (reward, success predicate, horizon, or reset distribution) and bump its versioned id (name-vN), flagging results for re-baseline. Use when editing an existing task's spec. STUB — to be filled when a task is first revised.
---

# bump-task-version (stub — fill on first task revision)

Hard rule #7: ANY change to a task's reward, success predicate, horizon, or reset
distribution requires bumping `name-vN` (e.g. `PointReach-v0` → `-v1`) and
flagging the results table for re-baseline. Will document the diff to watch and
the registration update in `suite.py`.
