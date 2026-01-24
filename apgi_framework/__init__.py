"""
APGI Framework Testing System

A comprehensive platform for implementing and validating the Interoceptive Predictive
Integration (APGI) Framework through systematic testing.
"""

__version__ = "1.0.0"
__author__ = "APGI"

from .core import APGIEquation, PrecisionCalculator, PredictionErrorProcessor
from .engines import SomaticMarkerEngine, ThresholdManager
from .exceptions import APGIFrameworkError, MathematicalError, SimulationError

__all__ = [
    "APGIEquation",
    "PrecisionCalculator",
    "PredictionErrorProcessor",
    "SomaticMarkerEngine",
    "ThresholdManager",
    "APGIFrameworkError",
    "MathematicalError",
    "SimulationError",
]
