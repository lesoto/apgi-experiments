"""
Neural data acquisition and processing pipeline for IPI framework.

This module provides interfaces for EEG/MEG data acquisition, real-time processing,
neural signature extraction including ERPs, microstates, and gamma synchrony,
pupillometry, and multi-modal physiological monitoring.
"""

from .eeg_interface import EEGInterface, EEGConfig, ArtifactDetector, ChannelInfo, ChannelType
from .erp_analysis import ERPAnalysis, ERPComponents, P3bMetrics
from .microstate_analysis import MicrostateAnalysis, MicrostateSequence
from .gamma_synchrony import GammaSynchronyAnalysis, CoherenceMetrics, NetworkConnectivity
from .pupillometry_interface import (
    PupillometryInterface, 
    PupillometryConfig, 
    PupilSample, 
    EyeType,
    BlinkDetectionMethod
)
from .physiological_monitoring import (
    PhysiologicalMonitoring,
    PhysiologicalConfig,
    PhysiologicalSample,
    SignalType,
    RespirationPhase,
    HeartRateMonitor,
    SkinConductanceMonitor,
    RespirationMonitor
)

# Signal processing components
from .eeg_processor import (
    EEGProcessor,
    FASTERArtifactDetector,
    EpochExtractor,
    BaselineCorrector,
    ERPExtractor,
    ProcessedEEG,
    ERPFeatures,
    FilterType
)
from .pupillometry_processor import (
    PupillometryProcessor,
    PupilFeatureExtractor,
    PupilMetricsCalculator,
    PupilQualityScorer,
    PupilFeatures,
    PupilQualityMetrics
)
from .cardiac_processor import (
    CardiacProcessor,
    HRVAnalyzer,
    HEPExtractor,
    CardiacQualityAssessor,
    HRVMetrics,
    CardiacQualityMetrics,
    RPeakAlgorithm
)
from .quality_control import (
    SignalQualityMonitor,
    ArtifactDetector as UnifiedArtifactDetector,
    AdaptiveProtocolManager,
    OperatorNotificationSystem,
    MultiModalQualityMetrics,
    QualityAlert,
    QualityLevel,
    AlertSeverity
)

__all__ = [
    # Data acquisition interfaces
    'EEGInterface',
    'EEGConfig',
    'ArtifactDetector',
    'ChannelInfo',
    'ChannelType',
    'PupillometryInterface',
    'PupillometryConfig',
    'PupilSample',
    'EyeType',
    'BlinkDetectionMethod',
    'PhysiologicalMonitoring',
    'PhysiologicalConfig',
    'PhysiologicalSample',
    'SignalType',
    'RespirationPhase',
    'HeartRateMonitor',
    'SkinConductanceMonitor',
    'RespirationMonitor',
    
    # Neural analysis
    'ERPAnalysis',
    'ERPComponents',
    'P3bMetrics',
    'MicrostateAnalysis',
    'MicrostateSequence',
    'GammaSynchronyAnalysis',
    'CoherenceMetrics',
    'NetworkConnectivity',
    
    # Signal processing
    'EEGProcessor',
    'FASTERArtifactDetector',
    'EpochExtractor',
    'BaselineCorrector',
    'ERPExtractor',
    'ProcessedEEG',
    'ERPFeatures',
    'FilterType',
    'PupillometryProcessor',
    'PupilFeatureExtractor',
    'PupilMetricsCalculator',
    'PupilQualityScorer',
    'PupilFeatures',
    'PupilQualityMetrics',
    'CardiacProcessor',
    'HRVAnalyzer',
    'HEPExtractor',
    'CardiacQualityAssessor',
    'HRVMetrics',
    'CardiacQualityMetrics',
    'RPeakAlgorithm',
    
    # Quality control
    'SignalQualityMonitor',
    'UnifiedArtifactDetector',
    'AdaptiveProtocolManager',
    'OperatorNotificationSystem',
    'MultiModalQualityMetrics',
    'QualityAlert',
    'QualityLevel',
    'AlertSeverity',
]
