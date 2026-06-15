---
name: run-eval-protocol
description: Run robosim's evaluation protocol (held-out seeds × N episodes -> success rate + mean return + per-episode raw scores) and record the canonical results row. Use when benchmarking a policy. STUB — partially implemented in eval/harness.py.
---

# run-eval-protocol (stub — extend at Milestone 5)

Today: `robosim.eval.evaluate(env_id, policy_fn, method=...)` runs the held-out
`EVAL_SEEDS`, returns `success_rate`, `mean_return`, and `.row()` with
per-episode raw scores.

To fill later: normalized scores (pinned random/oracle anchors), multi-seed
training × eval matrices, and `rliable` IQM + 95% bootstrap CIs + performance
profiles (Milestone 5). Always publish per-task raw scores, not just aggregates.
