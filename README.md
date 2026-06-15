# robosim

A **minimal robotics benchmark built from scratch** — a C++ physics core with a Python
benchmark layer (Gymnasium-compatible environments + a seeded evaluation harness + 3D
visualization). Built for *learning* how a robotics benchmark works, one verifiable layer
at a time.

> **Method:** tracer-bullet development — a thin vertical slice through *every* layer first
> (Milestone 0), then horizontal expansion. Every milestone ships a runnable test that
> proves it is correct.

- **Design decisions & hard rules:** [`docs/DESIGN.md`](docs/DESIGN.md)
- **Milestone roadmap:** [`docs/milestones.md`](docs/milestones.md)
- **Agent working notes / commands:** [`CLAUDE.md`](CLAUDE.md)

## Layout

```
include/robosim/   C++ core headers (no Python)
src/               C++ core implementation
bindings/          pybind11 bindings (logic-free)
python/robosim/    Python benchmark layer (env, tasks, eval, viz)
tests/cpp/         Catch2 tests        tests/py/  pytest tests
docs/              DESIGN.md, milestones.md
.claude/skills/    domain-specific skills
```

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install cmake ninja "pybind11>=2.12" numpy pytest "scikit-build-core>=0.10"

# C++ core + tests (no Python needed)
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build build
ctest --test-dir build --output-on-failure

# Python package (builds the pybind11 module)
pip install -e . --no-build-isolation
pytest tests/py -q
```

Milestone 0 is the `PointReach-3D` tracer bullet: a point mass reaching a target, threaded
end-to-end from the C++ integrator up to a Gymnasium env, a reproducible eval row, and a
`rerun` 3D view.
