"""
APGI Framework Falsification Testing System

A comprehensive platform for implementing and validating the Interoceptive Predictive
Integration (APGI) Framework through systematic falsification testing.
"""

__version__ = "0.1.0"
__author__ = "APGI Research Team"

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
