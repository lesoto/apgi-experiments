"""
Experimental control and stimulus presentation module.

Provides multi-modal task management, adaptive staircases, and timing control
for IPI framework experimental paradigms.
"""

from .multi_modal_task_manager import (
    MultiModalTaskManager,
    TrialConfiguration,
    TrialResult,
    ModalityType,
    TaskParadigm
)

from .adaptive_staircase import (
    AdaptiveStaircase,
    SimpleStaircase,
    PESTStaircase,
    QUESTStaircase,
    StaircaseParameters,
    StaircaseType,
    ThresholdEstimate,
    CrossModalThresholdNormalizer,
    create_staircase
)

from .precision_timing import (
    PrecisionTimer,
    TrialSequencer,
    SynchronizationManager,
    TimingController,
    TimingMode,
    SyncMarkerType,
    SyncMarker,
    TrialTiming,
    TimingEvent
)

from .neuromodulatory_blockade import (
    NeuromodulatoryBlockadeSimulator,
    NeuromodulatorEffect,
    BlockadeSimulationResult
)

from .surprise_accumulation_dynamics import (
    SurpriseAccumulationAnalyzer,
    TrialSurpriseEstimate,
    SurpriseAccumulationResult
)

from .behavioral_tasks import (
    DetectionTask,
    HeartbeatDetectionTask,
    DualModalityOddballTask,
    BehavioralThresholdCalculator,
    P3bCorrelationValidator,
    DPrimeCalculator,
    ConfidenceAnalyzer,
    AdaptiveAsynchronyAdjuster,
    StimulusCalibrator,
    InteroceptiveDeviantGenerator,
    ExteroceptiveDeviantGenerator,
    P3bRatioCalculator
)

__all__ = [
    'MultiModalTaskManager',
    'TrialConfiguration',
    'TrialResult',
    'ModalityType',
    'TaskParadigm',
    'AdaptiveStaircase',
    'SimpleStaircase',
    'PESTStaircase',
    'QUESTStaircase',
    'StaircaseParameters',
    'StaircaseType',
    'ThresholdEstimate',
    'CrossModalThresholdNormalizer',
    'create_staircase',
    'PrecisionTimer',
    'TrialSequencer',
    'SynchronizationManager',
    'TimingController',
    'TimingMode',
    'SyncMarkerType',
    'SyncMarker',
    'TrialTiming',
    'TimingEvent',
    'NeuromodulatoryBlockadeSimulator',
    'NeuromodulatorEffect',
    'BlockadeSimulationResult',
    'SurpriseAccumulationAnalyzer',
    'TrialSurpriseEstimate',
    'SurpriseAccumulationResult',
    'DetectionTask',
    'HeartbeatDetectionTask',
    'DualModalityOddballTask',
    'BehavioralThresholdCalculator',
    'P3bCorrelationValidator',
    'DPrimeCalculator',
    'ConfidenceAnalyzer',
    'AdaptiveAsynchronyAdjuster',
    'StimulusCalibrator',
    'InteroceptiveDeviantGenerator',
    'ExteroceptiveDeviantGenerator',
    'P3bRatioCalculator'
]
