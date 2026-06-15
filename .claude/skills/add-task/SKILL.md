---
name: add-task
description: Scaffold a new robosim benchmark Task and register it as a versioned env. Use when adding a task (e.g. Pendulum, CartPole, Reacher). STUB — to be filled at Milestone 1+.
---

# add-task (stub — fill at Milestone 1)

Will document the uniform recipe for a new Task:
- subclass `robosim.tasks.base.Task`: `initialize_episode` (randomize via `rng`),
  `before_step`, `get_observation`, `get_reward`, `get_terminated`, `success`,
  and `observation_spec`/`action_spec` (via `BoundedArraySpec`);
- keep the frozen `success()` predicate decoupled from the shaped `get_reward()`;
- register a versioned id + `max_episode_steps` + held-out `EVAL_SEEDS` in
  `suite.py`;
- pin random/oracle reference scores; emit a results-row.

Reference today: `tasks/point_reach.py`. See also `check-env-contract`.
