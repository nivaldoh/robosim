# CLAUDE.md

Working notes for agents. Kept **lean** — rationale lives in
[`docs/DESIGN.md`](docs/DESIGN.md); the roadmap in
[`docs/milestones.md`](docs/milestones.md); domain knowledge in
[`.claude/skills/`](.claude/skills/).

## What this is

A minimal robotics **benchmark** built from scratch for learning: a C++ physics
core + a Python benchmark layer (Gymnasium envs, seeded eval, rerun 3D viz).
Built **tracer-bullet style** — thin slice through every layer first, then widen.
Current state: **Milestone 0 (`PointReach-3D`) complete and verified.**

## Rules an agent must never break (full list in DESIGN.md)

1. **Tracer bullet first** — prove a capability through every layer before widening it.
2. **Every milestone ships a runnable test that proves correctness** — `ctest` + `pytest` green, always.
3. **Boundary discipline** — C++ core builds/tests with no Python; `bindings/` carries zero logic.
4. **Determinism** — state is `(time, qpos, qvel)`; all randomness via `np_random` (also seeds the C++ RNG).
5. **`terminated` ≠ `truncated`** — TimeLimit owns truncation.
6. **Report the frozen success predicate, never the shaped reward.**
7. **Versioned task ids** (`name-vN`); bump on reward/horizon/reset changes.

## Commands

All commands use the project venv at `.venv`.

```bash
# activate (or prefix commands with .venv/bin/)
source .venv/bin/activate

# C++ core + Catch2 tests (NO Python)
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build build
ctest --test-dir build --output-on-failure

# (re)build + install the Python package (after C++ changes)
pip install -e . --no-build-isolation

# Python tests
pytest tests/py

# end-to-end demo (writes a rerun .rrd; PD vs random eval row)
python scripts/demo_pointreach.py --rrd /tmp/pointreach.rrd
rerun /tmp/pointreach.rrd        # view (needs a display; headless -> open the file elsewhere)
```

First-time setup: `python3 -m venv .venv && .venv/bin/pip install cmake ninja
"pybind11>=2.12" numpy pytest "scikit-build-core>=0.10" "gymnasium>=0.29"
"rerun-sdk>=0.16"`.

## Map

```
include/robosim/  C++ headers (model/data/physics/system) — no Python
src/physics.cpp   forward dynamics + semi-implicit Euler
bindings/         pybind11 module (_core), logic-free
python/robosim/   physics.py env.py gym_env.py suite.py baselines.py rewards.py specs.py
                  tasks/ (Task base + point_reach)  eval/ (harness)  viz/ (rerun viewer)
tests/cpp/        Catch2 (physics closed-form / invariants)
tests/py/         pytest (bindings, env contract, eval, viz)
scripts/          demo_pointreach.py
```

## Gotchas

- CMake 4.x + Eigen 3.4.0 needs `-DCMAKE_POLICY_VERSION_MINIMUM=3.5` (already set
  for the pip build in `pyproject.toml`).
- Viz: rerun **saves `.rrd`** (open with `rerun file.rrd`); `--spawn` opens a live
  window. On Windows 11 WSLg, `--spawn` works — the viewer auto-points
  `XDG_RUNTIME_DIR` at `/mnt/wslg/runtime-dir` to find the Wayland socket.
  Truly headless (no display): use save mode.
- After editing C++, re-run `pip install -e . --no-build-isolation` to rebuild
  the extension.
