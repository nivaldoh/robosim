#pragma once
#include <Eigen/Core>

namespace robosim {

// Model: the COMPILED, IMMUTABLE description of a system.
//
// It is never mutated during simulation. Everything here is a constant of the
// problem (dimensions, masses, options). This mirrors MuJoCo's mjModel and is
// the half of the Model/Data split that makes reset trivial and rollouts
// deterministic and parallelizable.
//
// Milestone 0 models a single point mass in 3D (nq == nv == 3, qpos is the
// world position). Later milestones generalize this to a kinematic tree of
// joints in generalized coordinates.
struct Model {
  int nq = 3;                                       // generalized position dim
  int nv = 3;                                       // generalized velocity dim
  double dt = 0.01;                                 // integration timestep (s)
  double mass = 1.0;                                // point mass (kg)
  Eigen::Vector3d gravity = Eigen::Vector3d::Zero();  // world gravity (m/s^2)
};

}  // namespace robosim
