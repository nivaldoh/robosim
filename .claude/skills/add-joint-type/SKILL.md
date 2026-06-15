---
name: add-joint-type
description: Add a new joint type (revolute/prismatic/ball/free) to the robosim generalized-coordinate model — motion subspace, qpos/qvel addressing (mind nq != nv), Jacobian, and which pipeline stages to touch. STUB — to be filled at Milestone 1.
---

# add-joint-type (stub — fill at Milestone 1)

Will document: define a joint's motion subspace `S`, allocate `qpos`/`qvel`
addresses (mind `nq != nv` for ball/free joints with quaternions), its Jacobian
contribution, and the forward-kinematics / dynamics stages it touches. Include a
validation pendulum test (energy + period) via `physics-invariant-check`.

Today the model is a single point mass (no joints); this skill activates when the
kinematic tree arrives at M1.
