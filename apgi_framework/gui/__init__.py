"""
GUI components for parameter estimation experiment control.

This module provides graphical user interfaces for running parameter estimation
experiments, monitoring data quality, and managing sessions.
"""

from .parameter_estimation_gui import ParameterEstimationGUI, launch_gui
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
    # Main GUI
    "ParameterEstimationGUI",
    "launch_gui",
    # Session management
    "SessionSetupManager",
    "ParticipantManager",
    # Progress monitoring
    "RealTimeProgressMonitor",
    # Task configuration
    "TaskParameterConfigurator",
    "DetectionTaskConfig",
    "HeartbeatTaskConfig",
    "OddballTaskConfig",
    # Monitoring dashboard
    "LiveEEGMonitor",
    "PupillometryMonitor",
    "CardiacMonitor",
    "RealTimeParameterEstimateUpdater",
    "QualityAlertSystem",
    # Reporting and visualization
    "SessionReportGenerator",
    "ParameterVisualizationEngine",
    "DataQualitySummarizer",
    "DataExporter",
    # Error handling
    "HardwareFailureHandler",
    "SessionStateManager",
    "AutomaticBackupSystem",
    "UserGuidanceSystem",
]
