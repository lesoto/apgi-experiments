"""
Data management and storage components for the APGI Framework.

This module provides comprehensive data storage, versioning, management,
reporting, visualization, and dashboard capabilities for experimental data,
results, and metadata.
"""

from .storage_manager import StorageManager
from .data_models import (
    ExperimentalDataset,
    ExperimentMetadata,
    DataVersion,
    BackupInfo,
)
from .parameter_estimation_models import (
    TaskType,
    StimulusModality,
    BehavioralResponse,
    QualityMetrics,
    TrialData,
    DetectionTrialResult,
    HeartbeatTrialResult,
    OddballTrialResult,
    ParameterDistribution,
    ModelFitMetrics,
    ReliabilityMetrics,
    ParameterEstimates,
    SessionData,
)
from .parameter_estimation_schema import (
    ParameterEstimationSchema,
    create_parameter_estimation_schema,
)
from .parameter_estimation_dao import (
    ParameterEstimationDAO,
    create_parameter_estimation_dao,
)
from .migration_manager import MigrationManager, create_migration_manager
from .persistence_layer import PersistenceLayer
from .data_validator import DataValidator
from .experiment_tracker import ExperimentTracker

# New reporting and visualization components
from .report_generator import ReportGenerator, FalsificationReport, ReportSection
from .data_exporter import DataExporter
from .visualizer import APGIVisualizer, InteractiveVisualizer
from .dashboard import (
    DashboardServer,
    ExperimentMonitor,
    ExperimentComparator,
    create_dashboard,
)
from .data_manager import IntegratedDataManager, create_data_manager

# Import example data loading functionality
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "examples"))
from data_loader import load_example_data, list_example_data

__all__ = [
    # Core data management
    "StorageManager",
    "ExperimentalDataset",
    "ExperimentMetadata",
    "DataVersion",
    "BackupInfo",
    "PersistenceLayer",
    "DataValidator",
    "ExperimentTracker",
    # Parameter estimation models
    "TaskType",
    "StimulusModality",
    "BehavioralResponse",
    "QualityMetrics",
    "TrialData",
    "DetectionTrialResult",
    "HeartbeatTrialResult",
    "OddballTrialResult",
    "ParameterDistribution",
    "ModelFitMetrics",
    "ReliabilityMetrics",
    "ParameterEstimates",
    "SessionData",
    # Parameter estimation database
    "ParameterEstimationSchema",
    "create_parameter_estimation_schema",
    "ParameterEstimationDAO",
    "create_parameter_estimation_dao",
    "MigrationManager",
    "create_migration_manager",
    # Reporting and visualization
    "ReportGenerator",
    "FalsificationReport",
    "ReportSection",
    "DataExporter",
    "APGIVisualizer",
    "InteractiveVisualizer",
    # Dashboard and monitoring
    "DashboardServer",
    "ExperimentMonitor",
    "ExperimentComparator",
    "create_dashboard",
    # Integrated management
    "IntegratedDataManager",
    "create_data_manager",
    # Example data loading
    "load_example_data",
    "list_example_data",
]
