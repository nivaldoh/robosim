# robosim — Design Decisions & Hard Rules

The canonical reference for **why** robosim is built the way it is. `CLAUDE.md`
stays lean and points here. When a decision changes, update this file (and bump
the relevant task version — see rule #7).

## In one paragraph

robosim is a minimal robotics **benchmark** built from scratch for *learning*: a
C++ physics core (Model/Data split, generalized coordinates, semi-implicit
Euler) under a Python benchmark layer (Gymnasium-compatible envs, a
dm_control-style Task/Physics/Environment split, a seeded evaluation harness, and
rerun 3D viz). It is built **tracer-bullet style** — a thin vertical slice
through *every* layer first (Milestone 0 = `PointReach-3D`), then horizontal
expansion. The simulator exists only to serve the benchmark.

---

## Hard rules (non-negotiable)

1. **Tracer bullet first.** A new capability is proven through every layer on one
   task before it is widened. We do not build a layer "fully" in isolation.

2. **Every milestone ships a runnable test that proves correctness** — an
   analytic match, a conservation invariant, or a contract check. `ctest` and
   `pytest` must both be green before a milestone is "done." Verification is the
   spine of this project, not an afterthought.

3. **Boundary discipline.** The C++ core (`include/`, `src/`) builds and
   unit-tests with **zero** Python — see the standalone `cmake` build. Binding
   code (`bindings/bindings.cpp`) carries **zero** business logic; it only
   marshals types. This keeps the binding library swappable (e.g. to nanobind)
   and avoids ownership/lifetime segfaults.

4. **Determinism.** The only authoritative state is `(time, qpos, qvel)`
   (`include/robosim/data.hpp`); everything else is derived and recomputed each
   step, so a step is a pure function of `(Model, state, control)`. All
   randomness flows through Gymnasium's `self.np_random`, which also seeds the
   C++ RNG (`gym_env.py: reset`). Same seed ⇒ identical trajectory. The compiled
   `Model` is immutable during simulation; `Data` is the only scratchpad.

5. **`terminated` ≠ `truncated`.** `terminated` = MDP-terminal (success/failure,
   set by the Task); `truncated` = time limit, owned by Gymnasium's `TimeLimit`
   wrapper via `max_episode_steps`. The base env never truncates. Conflating
   these corrupts value bootstrapping.

6. **Report the sparse success predicate, never the shaped reward.** Each Task
   exposes a frozen `success(physics)` predicate, decoupled from `get_reward`.
   The eval harness reports `info["is_success"]`; reward hacking can't
   masquerade as success.

7. **Versioned task ids** (`name-vN`). Bump on ANY change to a task's reward,
   success predicate, horizon, or reset distribution; pin the physics-core commit
   in results. (`PointReach-v0` today.)

---

## The benchmark stack (layers & C++/Python split)

Rule of thumb: anything in the hot per-substep loop or numerically load-bearing
is **C++**; anything that is policy/eval orchestration, glue, or convention is
**Python**.

| Layer | Responsibility | Where |
|---|---|---|
| L0 Math/integrator | `Model`/`Data`, forward dynamics, semi-implicit Euler | **C++** `src/physics.cpp` |
| L1 Physics handle | own Model+Data, `reset/step/seed/diverged` | **C++** `include/robosim/system.hpp` |
| L2 Physics accessors | semantic named state (`position()`, `velocity()`) | **Py** `physics.py` |
| L3 Task | `initialize_episode/get_observation/get_reward/get_terminated/success`, specs | **Py** `tasks/` |
| L4 Environment | generic loop, control_timestep vs substeps | **Py** `env.py` |
| L5 Gym adapter | `gymnasium.Env`: spaces, seeding, (obs,info)/5-tuple | **Py** `gym_env.py` |
| L6 Suite/registry | versioned ids, eval seeds | **Py** `suite.py` |
| L7 Eval harness | seeded rollouts, success rate / return, results row | **Py** `eval/harness.py` |
| L8 Viz | 3D render of positions | **Py** `viz/rerun_viewer.py` |

The pybind boundary (`bindings/bindings.cpp`) is ~5 thin calls: `Model(...)`,
`System.reset/set_control/step/seed`, and read-only `qpos/qvel/time/...`.

---

## Settled decisions (decision → choice → rationale → tradeoff)

| Decision | Choice | Rationale / Tradeoff |
|---|---|---|
| Coordinates | **Generalized** over a kinematic tree | Joints enforced exactly, small state. M0's point mass (nq=nv=3, qpos=world pos) is the degenerate case. Tradeoff: `nq≠nv` quaternion bookkeeping arrives with free/ball joints. |
| Integrator | **Semi-implicit (symplectic) Euler** | One line different from explicit Euler, vastly more stable. First-order only (fine for now). |
| Timestep | **Fixed `dt` + control/substep decoupling** (`n_substeps = control_timestep/dt`, integer) | Determinism + frame-rate-independent tuning. `env.py` rejects non-integer ratios. |
| Dynamics algorithm | Direct now; **CRBA+RNEA at M1**, ABA later | Debuggable first (inspect M and bias); ABA's articulated-inertia recursion is subtle. |
| Contact model | **None yet** | Contacts are the hardest part → a later horizontal expansion (penalty / sequential-impulse). |
| Bindings | **pybind11** | Largest tutorial corpus (learning-friendly); swappable by rule #3. |
| Build | **CMake + scikit-build-core**; Eigen 3.4.0 + Catch2 v3.7.1 via FetchContent | pip-installable *and* a normal C++ project. |
| Math | **Eigen** (header-only) | Small fixed-size math; zero-copy ↔ NumPy via pybind11/eigen. |
| Env API | **Gymnasium-compatible** | Free TimeLimit / checker / vectorization / registry. Borrow dm_control's Task/Physics/Environment split + `rewards.tolerance`; skip dm_env TimeStep/Composer. |
| Model format | **Programmatic now**, URDF subset later | Keeps M0 parser-free; URDF is the first horizontal expansion. |
| Viz | **rerun.io** | Log positions, no render-loop code. Save `.rrd` (headless/WSL); `spawn=True` on a desktop. |
| Dimensionality | **3D from the start** | M0's fixed-base, translational/hinge design gives 3D without quaternions or a contact solver. |

---

## Known pitfalls (and how we avoid them)

- **Explicit Euler** injects energy / blows up → we use semi-implicit (rule in
  `physics.cpp`).
- **Quaternion `nq≠nv`** → not present at M0 (point mass); when free/ball joints
  arrive, integrate orientation on the manifold and renormalize (see the
  `spatial-algebra-conventions` skill).
- **Mutating `Model` mid-sim** breaks determinism → `Model` is value-owned and
  never mutated by the step.
- **Conflating terminated/truncated** → `TimeLimit` owns truncation; tested in
  `tests/py/test_env_contract.py`.
- **Reporting shaped reward as success** → frozen `success()` predicate, tested.
- **Unseeded C++ RNG / missing `super().reset(seed=)`** → both done in
  `gym_env.py`, determinism tested.
- **Doc-page physics constants** (CartPole/Reacher constants are source-only) →
  always cite the upstream source when adding a canonical task.
- **Over-engineering** (sparse linear algebra, SIMD, elliptic friction cones,
  ABA-before-CRBA) → deferred; they are scaling features, not prerequisites.

---

## Toolchain / environment notes

- **venv** at `.venv` (created from system `python3`); all commands use it.
- **CMake 4.x + Eigen 3.4.0:** pass `-DCMAKE_POLICY_VERSION_MINIMUM=3.5` (set for
  the pip build in `pyproject.toml`; pass on the CLI for the standalone build).
- **WSL2 / headless:** no display → rerun **saves `.rrd`** (open with
  `rerun file.rrd`); `--spawn` only works with a display.
- C++ tests are excluded from the wheel (built only in standalone `cmake`
  builds, `ROBOSIM_BUILD_TESTS`), keeping `pip install` lean.
