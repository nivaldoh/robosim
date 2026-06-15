# Milestones

Tracer-bullet roadmap. Each milestone adds one capability **and** the runnable
test that proves it. Don't advance until the prior milestone is green.

## ✅ Milestone 0 — `PointReach-3D` (the tracer bullet) — DONE

A point mass reaching a random 3D target, threaded end-to-end through every
layer. Physics is a pure double integrator, so correctness is checkable in
closed form.

**Verified by:**
- `tests/cpp/test_physics.cpp` — trajectory matches the closed-form
  semi-implicit-Euler recurrence to ~1e-12; impulse–momentum exact; divergence
  guard; step composition. (5 Catch2 tests)
- `tests/py/test_bindings.py` — Python results equal the C++ closed form; NumPy
  round-trip; deterministic stepping.
- `tests/py/test_env_contract.py` — Gymnasium `check_env`; (obs,info)/5-tuple;
  `terminated`≠`truncated`; same-seed determinism; PD beats random.
- `tests/py/test_eval.py` — fixed seeds ⇒ identical metrics; per-episode raw
  scores recorded; PD solves (success 1.00), random does not.
- `tests/py/test_viz.py` — a full episode writes a non-empty rerun `.rrd`.
- `scripts/demo_pointreach.py` — make → reset → PD → render(`.rrd`) → eval row.

## Milestone 1 — Pendulum (the real dynamics engine)

Single hinge in generalized coordinates → first mass matrix `M(q)`,
gravity-bias torque, forward kinematics. *Test:* passive energy conservation
within bound; small-angle period matches `2π√(l/g)`; cross-check against the
closed form. Then `Pendulum-v1` swing-up (continuous control, dense reward) with
a defined solved bar. Adds skills: `add-joint-type`, `spatial-algebra-conventions`.

## Milestone 2 — CartPole

2-DoF; the first multi-joint model. *Test:* dynamics match the reference
cart-pole equations; balance "solved" bar (mean return ≥ 475/500).

## Milestone 3 — 2-link Reacher + URDF subset + goal-conditioned obs

Hand-rolled 2-link arm; `{observation, achieved_goal, desired_goal}` dict; a
minimal URDF loader. *Test:* FK reach geometry; success = fingertip in target
radius; URDF round-trips to the same programmatic model. Adds skill:
`parse-urdf-subset`.

## Milestone 4 — Contacts

Penalty / sequential-impulse (Box2D-Lite-style), then ground contact → first
*true* `terminated`-on-fall locomotion task. *Test:* energy non-increase on
bounce, penetration bound, stacking stability.

## Milestone 5+ — Horizontal widening

Registry + vectorized envs; fixed-range domain randomization with a reproducible
difficulty level; richer metrics (`rliable` IQM + bootstrap CIs, performance
profiles); multi-task suite with train/test splits; optional vision obs. ABA as
an O(n) drop-in once CRBA+RNEA is validated; free-floating base (quaternions)
when locomotion needs it.
