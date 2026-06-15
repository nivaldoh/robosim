---
name: physics-invariant-check
description: Verify a robosim physics change is correct using analytic/invariant checks (closed-form trajectory match, energy/momentum conservation, determinism, divergence guard). Use whenever you add or modify dynamics, an integrator, a joint, or anything in the C++ core, before calling a milestone done.
---

# physics-invariant-check

robosim's spine: every physics change is *proven* by a runnable test, never
eyeballed. Pick the strongest invariant that applies and add it before/with the
change.

## The four invariants

1. **Closed-form trajectory match** (strongest) — when the dynamics have an
   analytic solution (constant force/accel, free fall, small-angle pendulum),
   assert the sim matches it to ~1e-9..1e-12. See
   `tests/cpp/test_physics.cpp` (`closed_form_pos`/`closed_form_vel`): the
   semi-implicit-Euler recurrence is `x_k = x0 + k·dt·v0 + a·dt²·k(k+1)/2`.
2. **Conservation invariants** — passive (unactuated) system: impulse–momentum
   is *exact* under constant force (`Δ(m·v) = F·t`); mechanical energy
   (`System::energy()`) is *bounded* under symplectic Euler (NOT exact — it
   conserves a shadow Hamiltonian). At M1+: pendulum energy drift over N steps
   within a bound; small-angle period ≈ `2π√(l/g)`.
3. **Determinism** — same initial state + same control sequence ⇒ identical
   trajectory (bitwise / 1e-15). See
   `tests/py/test_bindings.py::test_stepping_is_deterministic`.
4. **Divergence guard** — `diverged()` detects NaN/Inf; a blow-up must surface as
   `diverged`, not as a silent wrong number.

## How to run

```bash
cmake --build build && ctest --test-dir build --output-on-failure   # C++
pytest tests/py                                                      # Python
```

A milestone is not done until both are green.

## Where to add tests

- Pure C++ dynamics → `tests/cpp/test_*.cpp` (Catch2). Use a robust matcher:
  `REQUIRE_THAT(x, WithinAbs(ref, 1e-9) || WithinRel(ref, 1e-12))`.
- Cross-boundary / behavior → `tests/py/test_*.py`.

## Pitfalls

- Don't assert *exact* energy conservation for semi-implicit Euler on
  non-oscillatory motion — use closed-form trajectory or impulse–momentum.
- Choose tolerances that reflect accumulation (magnitude × ULP × steps); the
  OR-of-abs-and-rel matcher is robust across scales.
- When no closed form exists (articulated dynamics, M1+), cross-check `M`, `C`,
  `g`, `v̇` against an independent reference (Pinocchio/RBDL) on the same model.
