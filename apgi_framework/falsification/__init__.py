"""
APGI Framework Falsification Testing Module

This module implements the primary falsification testing framework for the APGI
(Interoceptive Predictive Integration) Framework, including consciousness assessment,
neural signature validation, and experimental control mechanisms.
"""

from .primary_falsification_test import PrimaryFalsificationTest
from .consciousness_assessment import ConsciousnessAssessment, ConsciousnessAssessmentSimulator, ConsciousnessValidator
from .ai_acc_validation import AIACCValidator
from .experimental_control import ExperimentalControlValidator
from .result_interpretation import FalsificationInterpreter, ResultLogger
from .edge_case_interpreter import EdgeCaseInterpreter, EdgeCaseType, FrameworkBoundary

__all__ = [
    'PrimaryFalsificationTest',
    'ConsciousnessAssessment',
    'ConsciousnessAssessmentSimulator',
    'ConsciousnessValidator',
    'AIACCValidator',
    'ExperimentalControlValidator',
    'FalsificationInterpreter',
    'ResultLogger',
    'EdgeCaseInterpreter',
    'EdgeCaseType',
    'FrameworkBoundary'
]