"""
Data management and storage components for the APGI Framework.

This module provides comprehensive data storage, versioning, management,
reporting, visualization, and dashboard capabilities for experimental data,
results, and metadata.
"""

# Import example data loading functionality

from .dashboard import (
    DashboardServer,
    ExperimentComparator,
    ExperimentMonitor,
    create_dashboard,
)
from .data_exporter import DataExporter
from .data_manager import IntegratedDataManager, create_data_manager
from .data_models import (
    BackupInfo,
    DataVersion,
    ExperimentalDataset,
    ExperimentMetadata,
)
from .data_validator import DataValidator
from .experiment_tracker import ExperimentTracker
from .migration_manager import MigrationManager, create_migration_manager
from .parameter_estimation_dao import (
    ParameterEstimationDAO,
    create_parameter_estimation_dao,
)
from .parameter_estimation_models import (
    BehavioralResponse,
    DetectionTrialResult,
    HeartbeatTrialResult,
    ModelFitMetrics,
    OddballTrialResult,
    ParameterDistribution,
    ParameterEstimates,
    QualityMetrics,
    ReliabilityMetrics,
    SessionData,
    StimulusModality,
    TaskType,
    TrialData,
)
from .parameter_estimation_schema import (
    ParameterEstimationSchema,
    create_parameter_estimation_schema,
)
from .persistence_layer import PersistenceLayer

# New reporting and visualization components
from .report_generator import FalsificationReport, ReportGenerator, ReportSection
from .storage_manager import StorageManager
from .visualizer import APGIVisualizer, InteractiveVisualizer

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
]
