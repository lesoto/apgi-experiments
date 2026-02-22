"""
GUI components for parameter estimation experiment control.

This module provides graphical user interfaces for running parameter estimation
experiments, monitoring data quality, and managing sessions.
"""

from .parameter_estimation_gui import launch_gui

from .session_management import SessionSetupManager, ParticipantManager
from .progress_monitoring import RealTimeProgressMonitor
from .task_configuration import (
    TaskParameterConfigurator,
    DetectionTaskConfig,
    HeartbeatTaskConfig,
    OddballTaskConfig,
)
from .monitoring_dashboard import (
    LiveEEGMonitor,
    PupillometryMonitor,
    CardiacMonitor,
    RealTimeParameterEstimateUpdater,
    QualityAlertSystem,
)
from .reporting_visualization import (
    SessionReportGenerator,
    ParameterVisualizationEngine,
    DataQualitySummarizer,
    DataExporter,
)
from .error_handling import (
    HardwareFailureHandler,
    SessionStateManager,
    AutomaticBackupSystem,
    UserGuidanceSystem,
)

__all__ = [
    "launch_gui",
    "SessionSetupManager",
    "ParticipantManager",
    "RealTimeProgressMonitor",
    "TaskParameterConfigurator",
    "DetectionTaskConfig",
    "HeartbeatTaskConfig",
    "OddballTaskConfig",
    "LiveEEGMonitor",
    "PupillometryMonitor",
    "CardiacMonitor",
    "RealTimeParameterEstimateUpdater",
    "QualityAlertSystem",
    "SessionReportGenerator",
    "ParameterVisualizationEngine",
    "DataQualitySummarizer",
    "DataExporter",
    "HardwareFailureHandler",
    "SessionStateManager",
    "AutomaticBackupSystem",
    "UserGuidanceSystem",
]
