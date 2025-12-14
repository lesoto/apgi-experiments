"""
Core mathematical framework for the APGI Framework.

This module contains the fundamental mathematical implementations including
the APGI ignition threshold equation, precision calculations, and prediction
error processing.
"""

from .equation import APGIEquation
from .precision import PrecisionCalculator
from .prediction_error import PredictionErrorProcessor
from .somatic_marker import SomaticMarkerEngine, ContextType
from .threshold import ThresholdManager, ThresholdAdaptationType
from .data_models import (
    APGIParameters, NeuralSignatures, ConsciousnessAssessment,
    ExperimentalTrial, FalsificationResult, StatisticalSummary,
    PharmacologicalCondition
)

__all__ = [
    "APGIEquation",
    "PrecisionCalculator", 
    "PredictionErrorProcessor",
    "SomaticMarkerEngine",
    "ContextType",
    "ThresholdManager",
    "ThresholdAdaptationType",
    "APGIParameters",
    "NeuralSignatures", 
    "ConsciousnessAssessment",
    "ExperimentalTrial",
    "FalsificationResult",
    "StatisticalSummary",
    "PharmacologicalCondition"
]