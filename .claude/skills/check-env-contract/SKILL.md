---
name: check-env-contract
description: Verify a robosim Gymnasium environment obeys the benchmark contract — API shape, terminated vs truncated semantics, seeding/determinism, frozen success predicate, and baseline-beats-random. Use when adding or changing a Task or env, before calling a milestone done.
---

# check-env-contract

Every robosim env must obey the Gymnasium contract AND the benchmark discipline.
The canonical implementation is `tests/py/test_env_contract.py`.

## Checklist

1. **PassiveEnvChecker** — `gymnasium.utils.env_checker.check_env(env.unwrapped,
   skip_render_check=True)`. (±inf obs-bound warnings are acceptable when a
   quantity is genuinely unbounded — finite bounds that rollouts can exit are
   worse and cause real failures.)
2. **API shape** — `reset(seed)` → `(obs, info)`; `step(action)` → 5-tuple;
   `obs ∈ observation_space`; reward scalar; `terminated`/`truncated` are bools.
3. **`terminated` ≠ `truncated`** — a never-solving policy must TRUNCATE at
   `max_episode_steps` with `terminated=False`; a solving policy must TERMINATE
   before the limit with `truncated=False` and `info["is_success"]`. Never
   hand-count steps; `TimeLimit` owns truncation.
4. **Seeding / determinism** — `super().reset(seed=seed)` is the first line of
   `reset()`; the C++ RNG is seeded from `np_random`; `reset(seed=k)` twice ⇒
   identical obs; same seed + same actions ⇒ identical trajectory.
5. **Frozen success predicate** — `Task.success()` is independent of
   `get_reward()`; eval reports `info["is_success"]`, never the shaped reward.
6. **Baseline sanity** — a hand-written controller (e.g. `PointReachPD`) beats
   `RandomPolicy` on the held-out eval seeds. This is the end-to-end proof that
   every layer is wired.

## How to run

```bash
pytest tests/py/test_env_contract.py tests/py/test_eval.py
```

## When adding a new Task

- Define obs/action via `BoundedArraySpec` (`specs.py`); the Gym adapter builds
  Box spaces.
- Register a versioned id + `max_episode_steps` in `suite.py`; add its
  published, held-out `EVAL_SEEDS`.
- Add a beats-random contract test. (See the `add-task` skill.)
