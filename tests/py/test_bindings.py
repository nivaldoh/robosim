"""Verify the pybind11 boundary: Python results equal the C++ closed form,
NumPy types round-trip correctly, and stepping is deterministic."""

import numpy as np
import robosim


def closed_form_pos(x0, v0, a, dt, k):
    # Semi-implicit Euler closed form for constant acceleration a.
    return x0 + k * dt * v0 + a * dt * dt * k * (k + 1) / 2.0


def test_imports_and_numpy_types():
    m = robosim.Model(mass=1.0, dt=0.01)
    sys = robosim.System(m)
    sys.reset(np.zeros(3), np.zeros(3))
    assert m.nq == 3 and m.nv == 3
    assert isinstance(sys.qpos, np.ndarray)
    assert sys.qpos.shape == (3,) and sys.qvel.shape == (3,)
    assert isinstance(sys.time, float)


def test_constant_force_matches_closed_form():
    dt, mass = 0.005, 2.0
    sys = robosim.System(robosim.Model(mass=mass, dt=dt))
    x0 = np.array([1.0, -2.0, 3.0])
    v0 = np.array([0.5, 0.0, -0.25])
    sys.reset(x0, v0)
    F = np.array([4.0, -6.0, 2.0])
    sys.set_control(F)
    sys.step(300)
    expected = closed_form_pos(x0, v0, F / mass, dt, 300)
    np.testing.assert_allclose(sys.qpos, expected, atol=1e-9, rtol=1e-12)


def test_gravity_free_fall_matches_closed_form():
    dt = 0.01
    sys = robosim.System(
        robosim.Model(mass=1.0, dt=dt, gravity=np.array([0.0, 0.0, -9.81]))
    )
    sys.reset(np.zeros(3), np.zeros(3))
    sys.step(100)
    expected_z = closed_form_pos(0.0, 0.0, -9.81, dt, 100)
    assert abs(sys.qpos[2] - expected_z) < 1e-9


def test_stepping_is_deterministic():
    def run():
        sys = robosim.System(
            robosim.Model(mass=1.3, dt=0.01, gravity=np.array([0.0, 0.0, -9.81]))
        )
        sys.reset(np.array([0.0, 0.0, 5.0]), np.array([1.0, 0.5, 0.0]))
        sys.set_control(np.array([0.2, -0.1, 0.4]))
        traj = []
        for _ in range(50):
            sys.step(2)
            traj.append(sys.qpos.copy())
        return np.array(traj)

    np.testing.assert_array_equal(run(), run())


def test_diverged_property_detects_nan():
    sys = robosim.System(robosim.Model())
    sys.reset(np.zeros(3), np.zeros(3))
    assert sys.diverged is False
    sys.reset(np.zeros(3), np.array([np.nan, 0.0, 0.0]))
    assert sys.diverged is True
