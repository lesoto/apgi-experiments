"""
Core mathematical framework for the IPI Framework.

This module contains the fundamental mathematical implementations including
the IPI ignition threshold equation, precision calculations, and prediction
error processing.
"""

from .equation import IPIEquation
from .precision import PrecisionCalculator
from .prediction_error import PredictionErrorProcessor
from .somatic_marker import SomaticMarkerEngine, ContextType
from .threshold import ThresholdManager, ThresholdAdaptationType

__all__ = [
    "IPIEquation",
    "PrecisionCalculator", 
    "PredictionErrorProcessor",
    "SomaticMarkerEngine",
    "ContextType",
    "ThresholdManager",
    "ThresholdAdaptationType"
]