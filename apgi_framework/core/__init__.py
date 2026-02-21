"""
Core mathematical framework for the APGI Framework.

This module contains the fundamental mathematical implementations including
the APGI ignition threshold equation, precision calculations, and prediction
error processing.
"""

from .data_models import (
    APGIParameters,
    ConsciousnessAssessment,
    ExperimentalTrial,
    FalsificationResult,
    NeuralSignatures,
    PharmacologicalCondition,
    StatisticalSummary,
)
from .equation import APGIEquation
from .models import PredictiveIgnitionNetwork, SomaticAgent
from .precision import PrecisionCalculator
from .prediction_error import PredictionErrorProcessor
from .somatic_marker import ContextType, SomaticMarkerEngine
from .threshold import ThresholdAdaptationType, ThresholdManager

__all__ = [
    "APGIEquation",
    "PrecisionCalculator",
    "PredictionErrorProcessor",
    "SomaticMarkerEngine",
    "ContextType",
    "ThresholdManager",
    "ThresholdAdaptationType",
    "SomaticAgent",
    "PredictiveIgnitionNetwork",
    "APGIParameters",
    "NeuralSignatures",
    "ConsciousnessAssessment",
    "ExperimentalTrial",
    "FalsificationResult",
    "StatisticalSummary",
    "PharmacologicalCondition",
]
