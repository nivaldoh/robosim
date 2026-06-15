"""Eval-harness checks: fixed seeds -> identical metrics, per-episode raw scores
are recorded, and the PD baseline solves PointReach while random does not."""

import robosim
from robosim.baselines import PointReachPD, RandomPolicy
from robosim.eval import evaluate

ENV_ID = "PointReach-v0"


def _pd(env):
    return PointReachPD()


def test_eval_is_reproducible():
    a = evaluate(ENV_ID, _pd, method="pd")
    b = evaluate(ENV_ID, _pd, method="pd")
    assert a.success_rate == b.success_rate
    assert a.mean_return == b.mean_return
    assert [e.episode_return for e in a.episodes] == [e.episode_return for e in b.episodes]


def test_eval_row_records_per_episode_scores():
    res = evaluate(ENV_ID, _pd, method="pd")
    row = res.row()
    n = len(robosim.suite.EVAL_SEEDS[ENV_ID])
    assert row["num_eval_episodes"] == n
    assert len(row["raw_returns"]) == n
    assert len(row["raw_success"]) == n
    assert row["success_rate"] == 1.0


def test_pd_solves_random_does_not():
    pd = evaluate(ENV_ID, _pd, method="pd")
    rand = evaluate(ENV_ID, lambda e: RandomPolicy(e.action_space), method="random")
    assert pd.success_rate == 1.0
    assert rand.success_rate <= 0.1
