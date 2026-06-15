"""The Gymnasium-contract checks — operationalizes the `check-env-contract`
skill: API shape, terminated != truncated semantics, and seed determinism."""

import warnings

import gymnasium as gym
import numpy as np

import robosim
from robosim.baselines import PointReachPD, RandomPolicy

ENV_ID = "PointReach-v0"


def test_passive_env_checker():
    from gymnasium.utils.env_checker import check_env

    env = gym.make(ENV_ID)
    with warnings.catch_warnings():
        # The only warnings are the expected +/-inf obs bounds (velocity is
        # genuinely unbounded; finite bounds would let rollouts exit the space).
        warnings.simplefilter("ignore")
        check_env(env.unwrapped, skip_render_check=True)
    env.close()


def test_reset_and_step_api():
    env = gym.make(ENV_ID)
    obs, info = env.reset(seed=0)
    assert env.observation_space.contains(obs)
    assert isinstance(info, dict)

    out = env.step(env.action_space.sample())
    assert len(out) == 5
    obs, reward, terminated, truncated, info = out
    assert env.observation_space.contains(obs)
    assert np.isscalar(reward)
    assert isinstance(terminated, (bool, np.bool_))
    assert isinstance(truncated, (bool, np.bool_))
    env.close()


def test_terminated_vs_truncated():
    # Zero action, no gravity -> never reaches -> must TRUNCATE at the limit.
    env = gym.make(ENV_ID)
    obs, _ = env.reset(seed=3)
    assert np.linalg.norm(obs[0:3] - obs[6:9]) > 0.05  # not already at goal
    terminated = truncated = False
    steps = 0
    while not (terminated or truncated):
        obs, _, terminated, truncated, _ = env.step(np.zeros(3, dtype=np.float32))
        steps += 1
    assert truncated and not terminated
    assert steps == robosim.suite.POINT_REACH_MAX_STEPS
    env.close()

    # PD reaches the goal -> must TERMINATE before the limit.
    env = gym.make(ENV_ID)
    obs, _ = env.reset(seed=1000)
    pd = PointReachPD()
    terminated = truncated = False
    info = {}
    while not (terminated or truncated):
        obs, _, terminated, truncated, info = env.step(pd(obs))
    assert terminated and not truncated and info["is_success"]
    env.close()


def test_seed_determinism():
    env = gym.make(ENV_ID)
    o1, _ = env.reset(seed=42)
    o2, _ = env.reset(seed=42)
    np.testing.assert_array_equal(o1, o2)
    env.close()

    # Same seed + same action sequence -> identical trajectory (incl. C++ RNG).
    def trajectory(seed):
        e = gym.make(ENV_ID)
        obs, _ = e.reset(seed=seed)
        actions = np.random.default_rng(0).uniform(-1, 1, size=(20, 3)).astype(np.float32)
        out = []
        for a in actions:
            obs, _, terminated, truncated, _ = e.step(a)
            out.append(obs.copy())
            if terminated or truncated:
                break
        e.close()
        return np.array(out)

    np.testing.assert_array_equal(trajectory(7), trajectory(7))


def test_pd_beats_random():
    from robosim.eval import evaluate

    pd = evaluate(ENV_ID, lambda e: PointReachPD(), method="pd")
    rand = evaluate(ENV_ID, lambda e: RandomPolicy(e.action_space), method="random")
    assert pd.success_rate == 1.0
    assert rand.success_rate < pd.success_rate
