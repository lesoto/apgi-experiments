"""
APGI Framework Testing System

A comprehensive platform for implementing and validating the Interoceptive Predictive
Integration (APGI) Framework through systematic testing.
"""

__version__ = "1.0.0"
__author__ = "APGI"

# Import all submodules for testing
from . import (
    analysis,
    clinical,
    data,
    falsification,
    gui,
    monitoring,
    processing,
    reporting,
    research,
    security,
    validation,
    visualization,
)
from .collaboration import CollaborationManager
from .computation import IntensiveComputation
from .core import APGIEquation, PrecisionCalculator, PredictionErrorProcessor
from .engines import SomaticMarkerEngine, ThresholdManager
from .exceptions import APGIFrameworkError, MathematicalError, SimulationError
from .fusion import DataFusion
from .notification import NotificationManager

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
