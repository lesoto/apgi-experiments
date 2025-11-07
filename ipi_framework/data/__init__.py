"""
Data management and storage components for the IPI Framework.

This module provides comprehensive data storage, versioning, management,
reporting, visualization, and dashboard capabilities for experimental data,
results, and metadata.
"""

from .storage_manager import StorageManager
from .data_models import (
    ExperimentalDataset,
    ExperimentMetadata,
    DataVersion,
    BackupInfo
)
from .persistence_layer import PersistenceLayer
from .data_validator import DataValidator
from .experiment_tracker import ExperimentTracker

# New reporting and visualization components
from .report_generator import ReportGenerator, FalsificationReport, ReportSection
from .data_exporter import DataExporter
from .visualizer import IPIVisualizer, InteractiveVisualizer
from .dashboard import DashboardServer, ExperimentMonitor, ExperimentComparator, create_dashboard
from .data_manager import IntegratedDataManager, create_data_manager

__all__ = [
    # Core data management
    'StorageManager',
    'ExperimentalDataset',
    'ExperimentMetadata', 
    'DataVersion',
    'BackupInfo',
    'PersistenceLayer',
    'DataValidator',
    'ExperimentTracker',
    
    # Reporting and visualization
    'ReportGenerator',
    'FalsificationReport',
    'ReportSection',
    'DataExporter',
    'IPIVisualizer',
    'InteractiveVisualizer',
    
    # Dashboard and monitoring
    'DashboardServer',
    'ExperimentMonitor',
    'ExperimentComparator',
    'create_dashboard',
    
    # Integrated management
    'IntegratedDataManager',
    'create_data_manager'
]