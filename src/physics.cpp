#include "robosim/physics.hpp"

#include <cassert>

namespace robosim {

void forward(const Model& model, Data& data) {
  // Milestone 0 point-mass dynamics: M = mass * I (diagonal), and qpos is the
  // world position, so generalized gravity maps straight onto the 3 DOFs.
  //   qacc = ctrl / mass + gravity
  // Replaced by articulated forward dynamics (CRBA/RNEA -> ABA) at Milestone 1.
  assert(model.nv == 3 && "Milestone 0 forward() assumes a 3-DOF point mass");
  data.qacc = data.ctrl / model.mass;
  data.qacc += model.gravity;  // sizes match (nv == 3)
}

void integrate(const Model& model, Data& data) {
  forward(model, data);
  // Semi-implicit (symplectic) Euler: velocity first, position from new velocity.
  data.qvel += model.dt * data.qacc;
  data.qpos += model.dt * data.qvel;
  data.time += model.dt;
}

void step(const Model& model, Data& data, int n_substeps) {
  for (int i = 0; i < n_substeps; ++i) integrate(model, data);
}

bool diverged(const Data& data) {
  return !data.qpos.allFinite() || !data.qvel.allFinite();
}

double energy(const Model& model, const Data& data) {
  const double kinetic = 0.5 * model.mass * data.qvel.squaredNorm();
  // Potential U = -m * g . x  (gravity is an acceleration vector; force = m*g).
  const double potential = -model.mass * model.gravity.dot(data.qpos);
  return kinetic + potential;
}

}  // namespace robosim
