---
name: spatial-algebra-conventions
description: The single pinned convention for robosim's 3D rigid-body / spatial algebra (frames, 6D motion/force vectors, quaternion integration on the manifold, world-frame inertia). Use before writing any articulated-dynamics or 3D-rotation code. STUB — to be filled at Milestone 1.
---

# spatial-algebra-conventions (stub — fill at Milestone 1)

The single biggest correctness risk in articulated dynamics is mixed
conventions. Will pin ONE convention and document: frame definitions; 6D
motion/force (spatial) vectors and the `v×`/`v×*` cross products; spatial
inertia; quaternion integration ON THE MANIFOLD (never `q ← q + v·dt`; mind
`nq != nv`) with per-step renormalization; world-frame inertia
`I_world = R·I_body·Rᵀ`. Sign/frame unit tests against a 1-link pendulum.

Not needed at M0 (point mass, no rotation).
