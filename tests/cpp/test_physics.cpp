// Catch2 tests for the Milestone 0 point-mass physics.
//
// The strongest possible check: the simulator's trajectory under constant
// acceleration must equal the CLOSED-FORM semi-implicit-Euler recurrence to
// ~machine precision. Plus impulse-momentum exactness, a divergence guard, and
// step-composition consistency.

#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>
#include <cmath>

#include "robosim/model.hpp"
#include "robosim/physics.hpp"
#include "robosim/system.hpp"

using namespace robosim;
using Catch::Matchers::WithinAbs;
using Catch::Matchers::WithinRel;

// Closed-form semi-implicit (symplectic) Euler for CONSTANT acceleration a:
//   v_k = v0 + k*a*dt
//   x_k = x0 + dt * sum_{j=1..k} v_j = x0 + k*dt*v0 + a*dt^2 * k*(k+1)/2
static double closed_form_pos(double x0, double v0, double a, double dt, int k) {
  return x0 + k * dt * v0 + a * dt * dt * static_cast<double>(k) * (k + 1) / 2.0;
}
static double closed_form_vel(double v0, double a, double dt, int k) {
  return v0 + k * a * dt;
}

TEST_CASE("free fall matches closed-form semi-implicit Euler", "[physics]") {
  Model m;
  m.dt = 0.01;
  m.mass = 1.0;
  m.gravity = Eigen::Vector3d(0, 0, -9.81);
  System sys(m);
  sys.reset(Eigen::Vector3d::Zero(), Eigen::Vector3d::Zero());

  const int N = 500;
  for (int k = 1; k <= N; ++k) {
    sys.step(1);
    const double z_ref = closed_form_pos(0.0, 0.0, -9.81, m.dt, k);
    REQUIRE_THAT(sys.qpos()(2),
                 WithinAbs(z_ref, 1e-9) || WithinRel(z_ref, 1e-12));
  }
  REQUIRE_THAT(sys.time(), WithinAbs(N * m.dt, 1e-9));
}

TEST_CASE("constant force matches closed form in position and velocity",
          "[physics]") {
  Model m;
  m.dt = 0.005;
  m.mass = 2.0;
  m.gravity.setZero();
  System sys(m);
  const Eigen::Vector3d x0(1, -2, 3), v0(0.5, 0, -0.25);
  sys.reset(x0, v0);
  const Eigen::Vector3d F(4, -6, 2);
  sys.set_control(F);

  const int N = 300;
  sys.step(N);

  for (int axis = 0; axis < 3; ++axis) {
    const double a = F(axis) / m.mass;
    const double x_ref = closed_form_pos(x0(axis), v0(axis), a, m.dt, N);
    const double v_ref = closed_form_vel(v0(axis), a, m.dt, N);
    REQUIRE_THAT(sys.qpos()(axis),
                 WithinAbs(x_ref, 1e-9) || WithinRel(x_ref, 1e-12));
    REQUIRE_THAT(sys.qvel()(axis),
                 WithinAbs(v_ref, 1e-10) || WithinRel(v_ref, 1e-12));
  }
}

TEST_CASE("impulse-momentum is exact under constant force", "[physics]") {
  Model m;
  m.dt = 0.01;
  m.mass = 1.5;
  m.gravity.setZero();
  System sys(m);
  sys.reset(Eigen::Vector3d::Zero(), Eigen::Vector3d(1, 2, 3));
  const Eigen::Vector3d F(0.3, -0.7, 1.1);
  sys.set_control(F);

  const int N = 200;
  const Eigen::Vector3d p0 = m.mass * sys.qvel();
  sys.step(N);
  const Eigen::Vector3d p1 = m.mass * sys.qvel();
  const Eigen::Vector3d impulse = F * (N * m.dt);
  REQUIRE_THAT((p1 - p0 - impulse).norm(), WithinAbs(0.0, 1e-12));
}

TEST_CASE("diverged() detects non-finite state", "[physics]") {
  Model m;
  System sys(m);
  sys.reset(Eigen::Vector3d::Zero(), Eigen::Vector3d::Zero());
  REQUIRE_FALSE(sys.diverged());
  sys.reset(Eigen::Vector3d::Zero(),
            Eigen::Vector3d(std::nan(""), 0.0, 0.0));
  REQUIRE(sys.diverged());
}

TEST_CASE("step(n) equals n single steps", "[physics]") {
  Model m;
  m.dt = 0.01;
  m.gravity = Eigen::Vector3d(0, 0, -9.81);
  System a(m), b(m);
  a.reset(Eigen::Vector3d(0, 0, 5), Eigen::Vector3d(1, 0, 0));
  b.reset(Eigen::Vector3d(0, 0, 5), Eigen::Vector3d(1, 0, 0));
  const Eigen::Vector3d F(0.1, 0.2, 0.3);
  a.set_control(F);
  b.set_control(F);

  a.step(10);
  for (int i = 0; i < 10; ++i) b.step(1);

  REQUIRE_THAT((a.qpos() - b.qpos()).norm(), WithinAbs(0.0, 1e-15));
  REQUIRE_THAT((a.qvel() - b.qvel()).norm(), WithinAbs(0.0, 1e-15));
}
