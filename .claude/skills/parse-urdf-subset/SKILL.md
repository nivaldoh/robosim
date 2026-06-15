---
name: parse-urdf-subset
description: Load a minimal URDF subset (links, joints, visual geometry) into a robosim programmatic model — which elements to read vs defer, mesh-path resolution, and the link/joint -> kinematic-tree mapping. STUB — to be filled at Milestone 3.
---

# parse-urdf-subset (stub — fill at Milestone 3)

Will document the minimal URDF subset to parse (link name + visual geometry +
origin; joint type/axis/origin/parent/child) and what to defer
(collision/inertial/materials/transmissions, and all of MJCF/SDF); mesh-path
resolution (`package://`/relative — the classic "robot loads but is invisible"
bug); and the link/joint → kinematic-tree mapping that must round-trip to the
same programmatic model. Parse with stdlib `xml.etree.ElementTree`.

Today models are built programmatically (`Physics.point_mass`); URDF arrives at M3.
