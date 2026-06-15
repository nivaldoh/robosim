"""Headless smoke test for the 3D viewer: logging a full episode writes a
non-empty rerun .rrd without error (no display required)."""

import gymnasium as gym
import pytest

ENV_ID = "PointReach-v0"


def test_viewer_writes_nonempty_rrd(tmp_path):
    pytest.importorskip("rerun")
    from robosim.baselines import PointReachPD
    from robosim.viz import PointReachViewer

    rrd = tmp_path / "episode.rrd"
    env = gym.make(ENV_ID)
    with PointReachViewer(save_path=rrd) as viewer:
        obs, _ = env.reset(seed=1000)
        environment = env.unwrapped.environment
        viewer.reset(environment)
        pd = PointReachPD()
        done = False
        while not done:
            obs, _, terminated, truncated, _ = env.step(pd(obs))
            viewer.step(environment)
            done = terminated or truncated
    env.close()

    assert rrd.exists() and rrd.stat().st_size > 0
