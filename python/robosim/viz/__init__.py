"""3D visualization. Importing this module does not require rerun until a viewer
is actually instantiated (rerun is the optional ``viz`` extra)."""

from .rerun_viewer import PointReachViewer

__all__ = ["PointReachViewer"]
