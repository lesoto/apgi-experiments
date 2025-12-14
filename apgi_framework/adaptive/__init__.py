"""
Adaptive staircase algorithms and stimulus control for parameter estimation tasks.

This module provides adaptive algorithms for optimal stimulus selection and
stimulus control systems for the three core parameter estimation tasks.
"""

from .quest_plus_staircase import QuestPlusStaircase
from .stimulus_generators import (
    GaborPatchGenerator,
    ToneGenerator, 
    CO2PuffController,
    HeartbeatSynchronizer
)
from .task_control import (
    PrecisionTimer,
    TaskStateMachine,
    ResponseCollector,
    SessionManager
)

__all__ = [
    'QuestPlusStaircase',
    'GaborPatchGenerator',
    'ToneGenerator',
    'CO2PuffController', 
    'HeartbeatSynchronizer',
    'PrecisionTimer',
    'TaskStateMachine',
    'ResponseCollector',
    'SessionManager'
]