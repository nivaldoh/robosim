#pragma once
#include "robosim/data.hpp"
#include "robosim/model.hpp"

namespace robosim {

// Compute the generalized acceleration qacc from the current (qpos, qvel, ctrl).
//
// Milestone 0 is the point-mass specialization: M = mass * I, so
//   qacc = ctrl / mass + gravity.
// This is the seam that becomes articulated forward dynamics (CRBA/RNEA, then
// ABA) at Milestone 1.
void forward(const Model& model, Data& data);

// Advance one timestep with semi-implicit (symplectic) Euler:
//   qvel <- qvel + dt * qacc      (velocity first)
//   qpos <- qpos + dt * qvel      (position from the NEW velocity)
// Calls forward() internally. Symplectic Euler is one line different from
// explicit Euler and vastly more stable for the stiff forces a sim produces.
void integrate(const Model& model, Data& data);

// Advance n_substeps integration steps.
void step(const Model& model, Data& data, int n_substeps);

// True if any authoritative state component is non-finite (NaN/Inf).
bool diverged(const Data& data);

// Total mechanical energy of the point mass: kinetic + gravitational potential.
// (Used as a conservation invariant starting at Milestone 1.)
double energy(const Model& model, const Data& data);

}  // namespace robosim
