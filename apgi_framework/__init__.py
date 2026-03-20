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

# Import all submodules for testing
from . import research
from . import clinical
from . import falsification
from . import data
from . import analysis
from . import gui
from . import monitoring
from . import visualization
from . import reporting
from . import validation
from . import security
from . import processing
from .cache import CacheManager
from .computation import IntensiveComputation
from .network import NetworkManager
from .collaboration import CollaborationManager
from .notification import NotificationManager
from .fusion import DataFusion
from .optimization import ResourceOptimizer

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
