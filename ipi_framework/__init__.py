"""
IPI Framework Falsification Testing System

A comprehensive platform for implementing and validating the Interoceptive Predictive 
Integration (IPI) Framework through systematic falsification testing.
"""

__version__ = "0.1.0"
__author__ = "IPI Research Team"

from .core import IPIEquation, PrecisionCalculator, PredictionErrorProcessor
from .engines import SomaticMarkerEngine, ThresholdManager
from .exceptions import IPIFrameworkError, MathematicalError, SimulationError

__all__ = [
    "IPIEquation",
    "PrecisionCalculator", 
    "PredictionErrorProcessor",
    "SomaticMarkerEngine",
    "ThresholdManager",
    "IPIFrameworkError",
    "MathematicalError",
    "SimulationError"
]