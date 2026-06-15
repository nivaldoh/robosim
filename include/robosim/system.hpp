#pragma once
#include <cstdint>
#include <utility>

#include "robosim/data.hpp"
#include "robosim/model.hpp"
#include "robosim/physics.hpp"

namespace robosim {

// System: the C++-side "Physics" handle. Owns an immutable Model plus its
// mutable Data, and exposes the small stateful surface the Python layer binds
// to. It carries NO task logic (no rewards/observations/termination) — those
// live in Python so they can be iterated without recompiling C++.
class System {
 public:
  explicit System(Model model) : model_(std::move(model)), data_(model_) {}

  const Model& model() const { return model_; }
  Data& data() { return data_; }
  const Data& data() const { return data_; }

  // Set the authoritative state and clear derived/input buffers.
  void reset(const Eigen::VectorXd& qpos, const Eigen::VectorXd& qvel) {
    data_.qpos = qpos;
    data_.qvel = qvel;
    data_.ctrl.setZero();
    data_.qacc.setZero();
    data_.time = 0.0;
  }

  void set_control(const Eigen::VectorXd& u) { data_.ctrl = u; }
  void step(int n_substeps) { robosim::step(model_, data_, n_substeps); }
  void seed(std::uint64_t s) { data_.rng.seed(s); }

  const Eigen::VectorXd& qpos() const { return data_.qpos; }
  const Eigen::VectorXd& qvel() const { return data_.qvel; }
  double time() const { return data_.time; }
  bool diverged() const { return robosim::diverged(data_); }
  double energy() const { return robosim::energy(model_, data_); }

 private:
  Model model_;
  Data data_;
};

}  // namespace robosim
