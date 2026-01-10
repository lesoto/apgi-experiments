"""
Persistence layer for the APGI Framework data management system.

Provides unified interface for data storage using SQLite and HDF5 backends.
"""

import sqlite3
import h5py
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
import numpy as np

from ..exceptions import APGIFrameworkError
from .data_models import (
    ExperimentalDataset,
    ExperimentMetadata,
    DataVersion,
    BackupInfo,
)
from ..security.secure_pickle import (
    safe_pickle_load,
    safe_pickle_dump,
    SecurePickleError,
)


class PersistenceError(APGIFrameworkError):
    """Errors in data persistence operations."""

    pass


class PersistenceLayer:
    """
    Unified persistence layer supporting SQLite and HDF5 storage.

    Provides data storage, retrieval, versioning, and backup capabilities
    with automatic format detection and conversion.
    """

    def __init__(self, storage_path: Union[str, Path], backend: str = "hdf5"):
        """
        Initialize persistence layer.

        Args:
            storage_path: Base path for data storage
            backend: Storage backend ('sqlite', 'hdf5', or 'hybrid')
        """
        self.storage_path = Path(storage_path)
        self.backend = backend.lower()

        if self.backend not in ["sqlite", "hdf5", "hybrid"]:
            raise PersistenceError(f"Unsupported backend: {backend}")

        # Create storage directories
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path = self.storage_path / "metadata"
        self.data_path = self.storage_path / "data"
        self.backup_path = self.storage_path / "backups"

        for path in [self.metadata_path, self.data_path, self.backup_path]:
            path.mkdir(exist_ok=True)

        # Initialize backends
        self._init_sqlite()
        if self.backend in ["hdf5", "hybrid"]:
            self._init_hdf5()

    def _init_sqlite(self):
        """Initialize SQLite database for metadata storage."""
        self.db_path = self.metadata_path / "experiments.db"

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    experiment_name TEXT,
                    description TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    researcher TEXT,
                    institution TEXT,
                    n_participants INTEGER,
                    n_trials INTEGER,
                    conditions TEXT,
                    parameters TEXT,
                    data_format TEXT,
                    file_paths TEXT,
                    total_size_mb REAL,
                    current_version TEXT,
                    tags TEXT,
                    category TEXT,
                    data_quality_score REAL,
                    completeness_percentage REAL,
                    validation_status TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    version_id TEXT PRIMARY KEY,
                    experiment_id TEXT,
                    version_number TEXT,
                    created_at TEXT,
                    created_by TEXT,
                    description TEXT,
                    parent_version TEXT,
                    checksum TEXT,
                    size_bytes INTEGER,
                    FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS backups (
                    backup_id TEXT PRIMARY KEY,
                    experiment_id TEXT,
                    backup_path TEXT,
                    created_at TEXT,
                    backup_type TEXT,
                    size_bytes INTEGER,
                    checksum TEXT,
                    compression_ratio REAL,
                    retention_days INTEGER,
                    status TEXT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id)
                )
            """)

            conn.commit()

    def _init_hdf5(self):
        """Initialize HDF5 storage structure."""
        self.hdf5_path = self.data_path / "experiments.h5"

        # Create initial HDF5 structure if it doesn't exist
        if not self.hdf5_path.exists():
            with h5py.File(self.hdf5_path, "w") as f:
                f.attrs["created_at"] = datetime.now().isoformat()
                f.attrs["version"] = "1.0.0"
                f.attrs["description"] = "APGI Framework Experimental Data Storage"

    def store_dataset(self, dataset: ExperimentalDataset) -> str:
        """
        Store experimental dataset with metadata.

        Args:
            dataset: ExperimentalDataset to store

        Returns:
            str: Experiment ID of stored dataset
        """
        try:
            # Store metadata in SQLite
            self._store_metadata(dataset.metadata)

            # Store data based on backend
            if self.backend == "sqlite":
                self._store_data_sqlite(dataset)
            elif self.backend == "hdf5":
                self._store_data_hdf5(dataset)
            elif self.backend == "hybrid":
                # Store large numerical data in HDF5, metadata in SQLite
                self._store_data_hdf5(dataset)

            # Create initial version
            version = DataVersion(
                version_number="1.0.0",
                description="Initial dataset version",
                checksum=self._calculate_checksum(dataset),
            )
            self._store_version(dataset.metadata.experiment_id, version)

            return dataset.metadata.experiment_id

        except Exception as e:
            raise PersistenceError(f"Failed to store dataset: {str(e)}")

    def load_dataset(
        self, experiment_id: str, version: Optional[str] = None
    ) -> ExperimentalDataset:
        """
        Load experimental dataset by ID.

        Args:
            experiment_id: Experiment identifier
            version: Specific version to load (latest if None)

        Returns:
            ExperimentalDataset: Loaded dataset
        """
        try:
            # Load metadata
            metadata = self._load_metadata(experiment_id)
            if not metadata:
                raise PersistenceError(f"Experiment {experiment_id} not found")

            # Load data based on backend
            if self.backend == "sqlite":
                data = self._load_data_sqlite(experiment_id, version)
            elif self.backend in ["hdf5", "hybrid"]:
                data = self._load_data_hdf5(experiment_id, version)

            # Load backup information
            backup_info = self._load_backup_info(experiment_id)

            dataset = ExperimentalDataset(
                metadata=metadata,
                data=data.get("data", {}),
                raw_data=data.get("raw_data"),
                processed_data=data.get("processed_data"),
                analysis_results=data.get("analysis_results"),
                backup_info=backup_info,
            )

            return dataset

        except Exception as e:
            raise PersistenceError(f"Failed to load dataset {experiment_id}: {str(e)}")

    def _store_metadata(self, metadata: ExperimentMetadata):
        """Store experiment metadata in SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO experiments VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """,
                (
                    metadata.experiment_id,
                    metadata.experiment_name,
                    metadata.description,
                    metadata.created_at.isoformat(),
                    metadata.updated_at.isoformat(),
                    metadata.researcher,
                    metadata.institution,
                    metadata.n_participants,
                    metadata.n_trials,
                    json.dumps(metadata.conditions),
                    json.dumps(metadata.parameters),
                    metadata.data_format,
                    json.dumps(metadata.file_paths),
                    metadata.total_size_mb,
                    metadata.current_version,
                    json.dumps(metadata.tags),
                    metadata.category,
                    metadata.data_quality_score,
                    metadata.completeness_percentage,
                    metadata.validation_status,
                ),
            )
            conn.commit()

    def _load_metadata(self, experiment_id: str) -> Optional[ExperimentMetadata]:
        """Load experiment metadata from SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM experiments WHERE experiment_id = ?", (experiment_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            return ExperimentMetadata(
                experiment_id=row["experiment_id"],
                experiment_name=row["experiment_name"],
                description=row["description"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                researcher=row["researcher"],
                institution=row["institution"],
                n_participants=row["n_participants"],
                n_trials=row["n_trials"],
                conditions=json.loads(row["conditions"]),
                parameters=json.loads(row["parameters"]),
                data_format=row["data_format"],
                file_paths=json.loads(row["file_paths"]),
                total_size_mb=row["total_size_mb"],
                current_version=row["current_version"],
                tags=json.loads(row["tags"]),
                category=row["category"],
                data_quality_score=row["data_quality_score"],
                completeness_percentage=row["completeness_percentage"],
                validation_status=row["validation_status"],
            )

    def _store_data_hdf5(self, dataset: ExperimentalDataset):
        """Store dataset in HDF5 format."""
        experiment_id = dataset.metadata.experiment_id

        with h5py.File(self.hdf5_path, "a") as f:
            # Create experiment group
            if experiment_id in f:
                del f[experiment_id]

            exp_group = f.create_group(experiment_id)
            exp_group.attrs["created_at"] = datetime.now().isoformat()

            # Store different data types
            for data_type, data_dict in [
                ("data", dataset.data),
                ("raw_data", dataset.raw_data),
                ("processed_data", dataset.processed_data),
                ("analysis_results", dataset.analysis_results),
            ]:
                if data_dict:
                    type_group = exp_group.create_group(data_type)
                    self._store_dict_hdf5(type_group, data_dict)

    def _store_dict_hdf5(self, group: h5py.Group, data_dict: Dict[str, Any]):
        """Recursively store dictionary data in HDF5."""
        for key, value in data_dict.items():
            if isinstance(value, np.ndarray):
                # Store numpy arrays directly
                try:
                    group.create_dataset(key, data=value)
                except (TypeError, ValueError):
                    # Fallback to JSON for complex arrays
                    group.attrs[key] = json.dumps(value.tolist(), default=str)
            elif isinstance(value, list):
                # Handle lists carefully - check if they can be converted to homogeneous array
                try:
                    # Try to create a homogeneous numpy array
                    arr = np.array(value)
                    if arr.dtype == "O":  # Object dtype means mixed types
                        # Store as JSON string instead
                        group.attrs[key] = json.dumps(value, default=str)
                    else:
                        # Homogeneous array, store directly
                        group.create_dataset(key, data=arr)
                except (TypeError, ValueError):
                    # Fallback to JSON serialization
                    group.attrs[key] = json.dumps(value, default=str)
            elif isinstance(value, dict):
                # Create subgroup for nested dictionaries
                subgroup = group.create_group(key)
                self._store_dict_hdf5(subgroup, value)
            elif isinstance(value, pd.DataFrame):
                # Store DataFrame as dataset with metadata
                df_group = group.create_group(key)
                df_group.create_dataset("values", data=value.values)
                df_group.create_dataset("columns", data=[str(c) for c in value.columns])
                df_group.create_dataset("index", data=[str(i) for i in value.index])
            else:
                # Store scalar values as attributes or datasets
                try:
                    group.attrs[key] = value
                except (TypeError, ValueError):
                    # Fallback to JSON serialization for complex objects
                    group.attrs[key] = json.dumps(value, default=str)

    def _load_data_hdf5(
        self, experiment_id: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load dataset from HDF5 format."""
        with h5py.File(self.hdf5_path, "r") as f:
            if experiment_id not in f:
                return {}

            exp_group = f[experiment_id]
            result = {}

            for data_type in ["data", "raw_data", "processed_data", "analysis_results"]:
                if data_type in exp_group:
                    result[data_type] = self._load_dict_hdf5(exp_group[data_type])

            return result

    def _load_dict_hdf5(self, group: h5py.Group) -> Dict[str, Any]:
        """Recursively load dictionary data from HDF5."""
        result = {}

        # Load attributes
        for key, value in group.attrs.items():
            try:
                # Try to parse as JSON if it's a string
                if isinstance(value, str) and (
                    value.startswith("{") or value.startswith("[")
                ):
                    result[key] = json.loads(value)
                else:
                    result[key] = value
            except (json.JSONDecodeError, TypeError):
                result[key] = value

        # Load datasets and subgroups
        for key in group.keys():
            item = group[key]
            if isinstance(item, h5py.Dataset):
                result[key] = item[()]
            elif isinstance(item, h5py.Group):
                # Check if it's a DataFrame
                if "values" in item and "columns" in item and "index" in item:
                    result[key] = pd.DataFrame(
                        data=item["values"][()],
                        columns=item["columns"][()],
                        index=item["index"][()],
                    )
                else:
                    result[key] = self._load_dict_hdf5(item)

        return result

    def _store_data_sqlite(self, dataset: ExperimentalDataset):
        """Store dataset in SQLite format (for smaller datasets)."""
        experiment_id = dataset.metadata.experiment_id

        # Serialize data to JSON/pickle for SQLite storage
        data_file = self.data_path / f"{experiment_id}.pkl"

        data_to_store = {
            "data": dataset.data,
            "raw_data": dataset.raw_data,
            "processed_data": dataset.processed_data,
            "analysis_results": dataset.analysis_results,
        }

        with open(data_file, "wb") as f:
            safe_pickle_dump(data_to_store, f)

    def _load_data_sqlite(
        self, experiment_id: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load dataset from SQLite format."""
        data_file = self.data_path / f"{experiment_id}.pkl"

        if not data_file.exists():
            return {}

        with open(data_file, "rb") as f:
            return safe_pickle_load(f)

    def _store_version(self, experiment_id: str, version: DataVersion):
        """Store version information."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO versions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    version.version_id,
                    experiment_id,
                    version.version_number,
                    version.created_at.isoformat(),
                    version.created_by,
                    version.description,
                    version.parent_version,
                    version.checksum,
                    version.size_bytes,
                ),
            )
            conn.commit()

    def _load_backup_info(self, experiment_id: str) -> List[BackupInfo]:
        """Load backup information for experiment."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM backups WHERE experiment_id = ?", (experiment_id,)
            )

            backups = []
            for row in cursor.fetchall():
                backup = BackupInfo(
                    backup_id=row["backup_id"],
                    backup_path=row["backup_path"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    backup_type=row["backup_type"],
                    size_bytes=row["size_bytes"],
                    checksum=row["checksum"],
                    compression_ratio=row["compression_ratio"],
                    retention_days=row["retention_days"],
                    status=row["status"],
                )
                backups.append(backup)

            return backups

    def _calculate_checksum(self, dataset: ExperimentalDataset) -> str:
        """Calculate checksum for dataset integrity verification."""
        # Create a string representation of the dataset for hashing
        data_str = json.dumps(
            {
                "metadata": dataset.metadata.experiment_id,
                "data_keys": list(dataset.data.keys()) if dataset.data else [],
                "timestamp": datetime.now().isoformat(),
            },
            sort_keys=True,
        )

        return hashlib.sha256(data_str.encode()).hexdigest()

    def create_backup(
        self, experiment_id: str, backup_type: str = "full"
    ) -> BackupInfo:
        """Create backup of experimental dataset."""
        try:
            # Load dataset
            dataset = self.load_dataset(experiment_id)

            # Create backup directory
            backup_dir = (
                self.backup_path
                / f"{experiment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            backup_dir.mkdir(exist_ok=True)

            # Copy data files
            if self.backend in ["hdf5", "hybrid"]:
                shutil.copy2(self.hdf5_path, backup_dir / "experiments.h5")

            if self.backend in ["sqlite", "hybrid"]:
                shutil.copy2(self.db_path, backup_dir / "experiments.db")

                # Copy pickle files if they exist
                data_file = self.data_path / f"{experiment_id}.pkl"
                if data_file.exists():
                    shutil.copy2(data_file, backup_dir / f"{experiment_id}.pkl")

            # Calculate backup size and checksum
            backup_size = sum(
                f.stat().st_size for f in backup_dir.rglob("*") if f.is_file()
            )
            backup_checksum = self._calculate_backup_checksum(backup_dir)

            # Create backup info
            backup_info = BackupInfo(
                backup_path=str(backup_dir),
                backup_type=backup_type,
                size_bytes=backup_size,
                checksum=backup_checksum,
            )

            # Store backup info in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO backups VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        backup_info.backup_id,
                        experiment_id,
                        backup_info.backup_path,
                        backup_info.created_at.isoformat(),
                        backup_info.backup_type,
                        backup_info.size_bytes,
                        backup_info.checksum,
                        backup_info.compression_ratio,
                        backup_info.retention_days,
                        backup_info.status,
                    ),
                )
                conn.commit()

            return backup_info

        except Exception as e:
            raise PersistenceError(
                f"Failed to create backup for {experiment_id}: {str(e)}"
            )

    def _calculate_backup_checksum(self, backup_dir: Path) -> str:
        """Calculate checksum for backup directory."""
        checksums = []
        for file_path in sorted(backup_dir.rglob("*")):
            if file_path.is_file():
                with open(file_path, "rb") as f:
                    file_checksum = hashlib.sha256(f.read()).hexdigest()
                    checksums.append(f"{file_path.name}:{file_checksum}")

        combined = "|".join(checksums)
        return hashlib.sha256(combined.encode()).hexdigest()

    def list_experiments(self, limit: Optional[int] = None) -> List[str]:
        """List all experiment IDs."""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT experiment_id FROM experiments ORDER BY created_at DESC"
            if limit:
                query += f" LIMIT {limit}"

            cursor = conn.execute(query)
            return [row[0] for row in cursor.fetchall()]

    def delete_experiment(self, experiment_id: str, include_backups: bool = False):
        """Delete experiment and optionally its backups."""
        try:
            # Delete from SQLite
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "DELETE FROM experiments WHERE experiment_id = ?", (experiment_id,)
                )
                conn.execute(
                    "DELETE FROM versions WHERE experiment_id = ?", (experiment_id,)
                )

                if include_backups:
                    # Get backup paths before deletion
                    cursor = conn.execute(
                        "SELECT backup_path FROM backups WHERE experiment_id = ?",
                        (experiment_id,),
                    )
                    backup_paths = [row[0] for row in cursor.fetchall()]

                    # Delete backup records
                    conn.execute(
                        "DELETE FROM backups WHERE experiment_id = ?", (experiment_id,)
                    )

                    # Delete backup directories
                    for backup_path in backup_paths:
                        backup_dir = Path(backup_path)
                        if backup_dir.exists():
                            shutil.rmtree(backup_dir)

                conn.commit()

            # Delete from HDF5
            if self.backend in ["hdf5", "hybrid"]:
                with h5py.File(self.hdf5_path, "a") as f:
                    if experiment_id in f:
                        del f[experiment_id]

        except Exception as e:
            raise PersistenceError(
                f"Failed to delete experiment {experiment_id}: {str(e)}"
            )

    def flush_all(self) -> None:
        """
        Flush all pending operations and ensure data persistence.

        Forces all cached data to be written to disk and commits
        any pending database transactions.
        """
        try:
            # Flush SQLite connections
            if self.backend in ["sqlite", "hybrid"]:
                with sqlite3.connect(self.db_path) as conn:
                    conn.commit()

            # Flush HDF5 files
            if self.backend in ["hdf5", "hybrid"]:
                # HDF5 files are automatically flushed when closed
                # Force flush by opening and closing
                with h5py.File(self.hdf5_path, "a") as f:
                    f.flush()

        except Exception as e:
            raise PersistenceError(f"Failed to flush persistence layer: {str(e)}")

            # Delete pickle file
            data_file = self.data_path / f"{experiment_id}.pkl"
            if data_file.exists():
                data_file.unlink()

        except Exception as e:
            raise PersistenceError(
                f"Failed to delete experiment {experiment_id}: {str(e)}"
            )
