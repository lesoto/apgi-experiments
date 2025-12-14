"""
Data models for the APGI Framework data management system.

Defines the core data structures for experimental datasets, metadata,
versioning, and backup information.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import uuid


@dataclass
class DataVersion:
    """Represents a version of experimental data."""
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version_number: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    description: str = ""
    parent_version: Optional[str] = None
    checksum: str = ""
    size_bytes: int = 0


@dataclass
class ExperimentMetadata:
    """Metadata for experimental datasets."""
    experiment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    experiment_name: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    researcher: str = ""
    institution: str = ""
    
    # Experimental parameters
    n_participants: int = 0
    n_trials: int = 0
    conditions: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Data characteristics
    data_format: str = "hdf5"  # hdf5, sqlite, csv
    file_paths: List[str] = field(default_factory=list)
    total_size_mb: float = 0.0
    
    # Version information
    current_version: str = "1.0.0"
    version_history: List[DataVersion] = field(default_factory=list)
    
    # Tags and categories
    tags: List[str] = field(default_factory=list)
    category: str = "falsification_test"
    
    # Quality metrics
    data_quality_score: float = 1.0
    completeness_percentage: float = 100.0
    validation_status: str = "pending"  # pending, validated, failed


@dataclass
class BackupInfo:
    """Information about data backups."""
    backup_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    backup_path: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    backup_type: str = "full"  # full, incremental, differential
    size_bytes: int = 0
    checksum: str = ""
    compression_ratio: float = 1.0
    retention_days: int = 30
    status: str = "active"  # active, archived, deleted


@dataclass
class ExperimentalDataset:
    """Complete experimental dataset with data and metadata."""
    metadata: ExperimentMetadata
    data: Dict[str, Any] = field(default_factory=dict)
    raw_data: Optional[Dict[str, Any]] = None
    processed_data: Optional[Dict[str, Any]] = None
    analysis_results: Optional[Dict[str, Any]] = None
    
    # File system information
    storage_path: Optional[Path] = None
    backup_info: List[BackupInfo] = field(default_factory=list)
    
    # Access control
    access_permissions: Dict[str, List[str]] = field(default_factory=dict)
    is_locked: bool = False
    lock_reason: str = ""
    
    def __post_init__(self):
        """Initialize dataset after creation."""
        if not self.metadata.experiment_id:
            self.metadata.experiment_id = str(uuid.uuid4())
        
        if not self.metadata.created_at:
            self.metadata.created_at = datetime.now()
            
        self.metadata.updated_at = datetime.now()


@dataclass
class QueryFilter:
    """Filter criteria for querying experimental datasets."""
    experiment_ids: Optional[List[str]] = None
    researcher: Optional[str] = None
    institution: Optional[str] = None
    date_range: Optional[tuple[datetime, datetime]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    min_participants: Optional[int] = None
    max_participants: Optional[int] = None
    conditions: Optional[List[str]] = None
    validation_status: Optional[str] = None
    data_format: Optional[str] = None


@dataclass
class StorageStats:
    """Statistics about data storage usage."""
    total_datasets: int = 0
    total_size_mb: float = 0.0
    total_backups: int = 0
    backup_size_mb: float = 0.0
    oldest_dataset: Optional[datetime] = None
    newest_dataset: Optional[datetime] = None
    average_dataset_size_mb: float = 0.0
    storage_efficiency: float = 1.0  # compression ratio
    
    # By category
    datasets_by_category: Dict[str, int] = field(default_factory=dict)
    size_by_category: Dict[str, float] = field(default_factory=dict)
    
    # Health metrics
    corrupted_datasets: int = 0
    missing_backups: int = 0
    validation_failures: int = 0