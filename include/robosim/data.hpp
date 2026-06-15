#pragma once
#include <Eigen/Core>
#include <cstdint>
#include <random>

#include "robosim/model.hpp"

namespace robosim {

// Data: the MUTABLE runtime scratchpad.
//
// The ONLY authoritative state is (time, qpos, qvel); every other field is a
// deterministic function of those and is recomputed each step. This is the
// other half of the Model/Data split: a step is a pure function of
// (Model, state, control), which is what makes resets trivial and rollouts
// reproducible.
struct Data {
  double time = 0.0;
  Eigen::VectorXd qpos;  // size nq  (authoritative)
  Eigen::VectorXd qvel;  // size nv  (authoritative)
  Eigen::VectorXd ctrl;  // size nv  (applied generalized/world force; input)
  Eigen::VectorXd qacc;  // size nv  (derived each step by forward())

  // Seedable RNG for any physics-level stochasticity (process noise, domain
  // randomization). Unused by Milestone 0 dynamics, but seeded from Python so
  // the whole pipeline is reproducible from a single seed.
  std::mt19937_64 rng{0};

  explicit Data(const Model& m)
      : qpos(Eigen::VectorXd::Zero(m.nq)),
        qvel(Eigen::VectorXd::Zero(m.nv)),
        ctrl(Eigen::VectorXd::Zero(m.nv)),
        qacc(Eigen::VectorXd::Zero(m.nv)) {}
};

}  // namespace robosim
