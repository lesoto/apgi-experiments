"""
Engine components for the IPI Framework.

This module contains the engine implementations for somatic marker processing
and threshold management.
"""

from ..core.somatic_marker import SomaticMarkerEngine
from ..core.threshold import ThresholdManager

__all__ = [
    "SomaticMarkerEngine",
    "ThresholdManager"
]