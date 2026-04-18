"""
GUI components for parameter estimation experiment control.

This module provides graphical user interfaces for running parameter estimation
experiments, monitoring data quality, and managing sessions.
"""

from typing import Any, Dict, Optional

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


# Mock classes for testing
class InteractiveDesigner:
    """Mock interactive designer for testing purposes."""

    def __init__(self) -> None:
        self.design_components: Dict[str, Any] = {}
        self.current_design: Optional[Dict[str, Any]] = None

    def create_design(self, design_spec: Any) -> Any:
        """Create an interactive design."""
        design_id = f"design_{hash(str(design_spec)) % 10000:04d}"
        self.current_design = {
            "design_id": design_id,
            "specification": design_spec,
            "components": [],
            "interactive": True,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        self.design_components[design_id] = self.current_design
        return self.current_design

    def add_component(self, component_type: Any, properties: Any) -> Any:
        """Add a component to the current design."""
        if self.current_design:
            component = {
                "type": component_type,
                "properties": properties,
                "id": f"component_{len(self.current_design['components'])}",
            }
            self.current_design["components"].append(component)
            return component
        return None

    def get_design(self, design_id: Any) -> Any:
        """Get design by ID."""

        return self.design_components.get(design_id)


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
    # Mock classes for testing
    "InteractiveDesigner",
]
