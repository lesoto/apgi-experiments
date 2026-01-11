"""
Tests for data management modules.
"""

import pytest
import tempfile
import json
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from apgi_framework.data.data_manager import IntegratedDataManager
from apgi_framework.data.storage_manager import StorageManager, StorageError
from apgi_framework.data.data_exporter import DataExporter
from apgi_framework.data.report_generator import ReportGenerator
from apgi_framework.data.visualizer import APGIVisualizer
from apgi_framework.exceptions import DataManagementError


class TestIntegratedDataManager:
    """Test integrated data manager implementation."""

    def test_initialization(self):
        """Test data manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = IntegratedDataManager(
                base_output_dir=temp_dir, enable_dashboard=False
            )

            assert manager.base_output_dir == Path(temp_dir)
            assert manager.report_generator is not None
            assert manager.data_exporter is not None
            assert manager.visualizer is not None
            assert manager.dashboard is None  # Disabled

    def test_directory_creation(self):
        """Test automatic directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "test_outputs"

            manager = IntegratedDataManager(
                base_output_dir=str(output_dir), enable_dashboard=False
            )

            assert output_dir.exists()
            assert (output_dir / "reports").exists()
            assert (output_dir / "exports").exists()
            assert (output_dir / "figures").exists()

    def test_store_experiment_data(self):
        """Test registering experiment data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = IntegratedDataManager(
                storage_path=temp_dir, backend="sqlite"
            )

            # Mock experiment data
            experiment_data = {
                "experiment_id": "test_exp_001",
                "timestamp": datetime.now().isoformat(),
                "parameters": {"theta_t": 3.5, "pi_e": 2.0},
            }

            # Register experiment (this is the actual method)
            result = manager.register_experiment("test_exp_001", experiment_data)

            assert result == "test_exp_001"
            assert "test_exp_001" in manager.active_experiments

    def test_generate_report(self):
        """Test report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = IntegratedDataManager(
                base_output_dir=temp_dir, enable_dashboard=False
            )

            # Register experiment first
            experiment_data = {
                "experiment_id": "test_exp_001",
                "timestamp": datetime.now().isoformat(),
                "parameters": {"theta_t": 3.5, "pi_e": 2.0},
                "results": {"p3b_violations": 0.15, "falsified": False},
            }
            manager.register_experiment("test_exp_001", experiment_data)

            # Mock statistical summary using correct data model
            from apgi_framework.core.data_models import StatisticalSummary

            summary = StatisticalSummary(
                total_trials=1000, statistical_power=0.85, mean_effect_size=0.8
            )

            # Generate report (this is the actual method)
            report_paths = manager.generate_comprehensive_report(
                "test_exp_001", summary, formats=["html"]
            )

            assert isinstance(report_paths, dict)
            assert "html" in report_paths

    def test_export_data(self):
        """Test data export functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = IntegratedDataManager(
                base_output_dir=temp_dir, enable_dashboard=False
            )

            # Register experiment first
            experiment_data = {
                "experiment_id": "test_exp_001",
                "timestamp": datetime.now().isoformat(),
                "parameters": {"theta_t": 3.5, "pi_e": 2.0},
            }
            manager.register_experiment("test_exp_001", experiment_data)

            # Export data (this is the actual method)
            export_paths = manager.export_experiment_data(
                "test_exp_001", formats=["json"]
            )

            assert isinstance(export_paths, dict)

    def test_create_visualization(self):
        """Test visualization creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = IntegratedDataManager(
                base_output_dir=temp_dir, enable_dashboard=False
            )

            # Register experiment first
            experiment_data = {
                "experiment_id": "test_exp_001",
                "timestamp": datetime.now().isoformat(),
                "parameters": {"theta_t": 3.5, "pi_e": 2.0},
            }
            manager.register_experiment("test_exp_001", experiment_data)

            # Mock statistical summary
            from apgi_framework.core.data_models import StatisticalSummary

            summary = StatisticalSummary(
                total_trials=1000, mean_effect_size=0.15
            )

            # Generate visualizations (this is the actual method)
            figure_paths = manager.generate_visualizations(
                "test_exp_001", summary, create_publication_set=False
            )

            assert isinstance(figure_paths, list)

    def test_query_experiments(self):
        """Test experiment querying."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = IntegratedDataManager(
                base_output_dir=temp_dir, enable_dashboard=False
            )

            # Store some test data first
            experiments = [
                {"experiment_id": "exp_001", "date": "2024-01-01", "falsified": False},
                {"experiment_id": "exp_002", "date": "2024-01-02", "falsified": True},
                {"experiment_id": "exp_003", "date": "2024-01-03", "falsified": False},
            ]

            for exp in experiments:
                manager.register_experiment(exp["experiment_id"], exp)

            # Query experiments
            all_experiments = manager.query_experiments()
            falsified_experiments = manager.query_experiments(
                filters={"falsified": True}
            )

            assert len(all_experiments) == 3
            assert len(falsified_experiments) == 1
            assert falsified_experiments[0]["experiment_id"] == "exp_002"

    def test_dashboard_integration(self):
        """Test dashboard integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = IntegratedDataManager(
                base_output_dir=temp_dir, enable_dashboard=False
            )

            # Test dashboard URL (this is the actual method)
            dashboard_url = manager.get_dashboard_url()

            assert dashboard_url is None  # Disabled in test


class TestStorageManager:
    """Test storage manager implementation."""

    def test_initialization(self):
        """Test storage manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(
                storage_path=temp_dir,
                backend="sqlite",
                auto_validate=True,
                auto_backup=False,
            )

            assert storage.storage_path == Path(temp_dir)
            assert storage.backend == "sqlite"
            assert storage.auto_validate is True
            assert storage.auto_backup is False

    @staticmethod
    def create_test_dataset(dataset_id="test_dataset_001", participant_id="P001", data=None):
        """Helper to create a test ExperimentalDataset."""
        from apgi_framework.data.data_models import ExperimentalDataset, ExperimentMetadata
        
        if data is None:
            data = {
                "p3b_amplitudes": [5.2, 4.8],
                "apgi_parameters": {"theta_t": 3.5, "pi_e": 2.0},
                "neural_signatures": {"p3b_amplitude": 5.2},
                "consciousness_assessments": {"subjective_report": True},
            }
            
        metadata = ExperimentMetadata(
            experiment_id=dataset_id,
            experiment_name=f"Test Experiment {dataset_id}",
            researcher=participant_id,
            n_participants=1,
            n_trials=10,
            created_at=datetime.now(),
        )
        
        return ExperimentalDataset(metadata=metadata, data=data)

    def test_store_dataset(self):
        """Test dataset storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(
                storage_path=temp_dir, backend="sqlite", auto_backup=False
            )

            # Mock dataset
            dataset = self.create_test_dataset()

            # Store dataset (disable validation for testing)
            result = storage.store_dataset(dataset, validate=False)

            assert result is True
            assert storage.dataset_count > 0

    def test_retrieve_dataset(self):
        """Test dataset retrieval."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(
                storage_path=temp_dir, backend="sqlite", auto_backup=False
            )

            # Store dataset first
            dataset = self.create_test_dataset()
            storage.store_dataset(dataset)

            # Retrieve dataset
            retrieved = storage.retrieve_dataset("test_dataset_001")

            assert retrieved is not None
            assert retrieved.metadata.experiment_id == "test_dataset_001"
            assert retrieved.metadata.researcher == "P001"

    def test_query_datasets(self):
        """Test dataset querying."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(
                storage_path=temp_dir, backend="sqlite", auto_backup=False
            )

            # Store multiple datasets
            datasets = [
                self.create_test_dataset("dataset_001", "P001"),
                self.create_test_dataset("dataset_002", "P002"),
                self.create_test_dataset("dataset_003", "P001"),
            ]
            
            for dataset in datasets:
                storage.store_dataset(dataset)

            # Query by researcher
            p001_datasets = storage.query_datasets({"researcher": "P001"})
            assert len(p001_datasets) == 2

    def test_update_dataset(self):
        """Test dataset updating."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(
                storage_path=temp_dir, backend="sqlite", auto_backup=False
            )

            # Store original dataset
            dataset = self.create_test_dataset(data={"p3b_amplitudes": [5.2]})
            storage.store_dataset(dataset)

            # Update dataset
            updates = {
                "metadata": {"participant_id": "P001", "updated": True},
                "data": {"p3b_amplitudes": [5.2, 4.8, 5.5]},
            }

            result = storage.update_dataset("test_dataset_001", updates)
            assert result is True

            # Verify update
            updated = storage.retrieve_dataset("test_dataset_001")
            assert updated["metadata"]["updated"] is True
            assert len(updated["data"]["p3b_amplitudes"]) == 3

    def test_delete_dataset(self):
        """Test dataset deletion."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(
                storage_path=temp_dir, backend="sqlite", auto_backup=False
            )

            # Store dataset
            dataset = self.create_test_dataset(data={})
            storage.store_dataset(dataset)

            # Verify it exists
            assert storage.retrieve_dataset("test_dataset_001") is not None

            # Delete dataset
            result = storage.delete_dataset("test_dataset_001")
            assert result is True

            # Verify it's gone
            assert storage.retrieve_dataset("test_dataset_001") is None

    def test_backup_creation(self):
        """Test backup creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(
                storage_path=temp_dir, backend="sqlite", auto_backup=True
            )

            # Store some data
            dataset = self.create_test_dataset(data={})
            storage.store_dataset(dataset)

            # Create backup
            backup_path = storage.create_backup("test_backup")

            assert backup_path is not None
            assert Path(backup_path).exists()
            assert "test_backup" in backup_path

    def test_storage_statistics(self):
        """Test storage statistics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(
                storage_path=temp_dir, backend="sqlite", auto_backup=False
            )

            # Store some datasets
            for i in range(5):
                dataset = self.create_test_dataset(
                    dataset_id=f"dataset_{i:03d}",
                    data={"values": list(range(10))}
                )
                storage.store_dataset(dataset)

            # Get statistics
            stats = storage.get_storage_statistics()

            assert "total_datasets" in stats
            assert "total_size" in stats
            assert "created_at" in stats
            assert stats["total_datasets"] == 5

    def test_validation_errors(self):
        """Test validation error handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(
                storage_path=temp_dir,
                backend="sqlite",
                auto_validate=True,
                auto_backup=False,
            )

            # Invalid dataset (using wrong type)
            invalid_dataset = "not a dataset object"

            # Should raise validation error
            with pytest.raises(Exception):  # Could be ValidationError or StorageError
                storage.store_dataset(invalid_dataset)

    def test_concurrent_access(self):
        """Test concurrent access handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(
                storage_path=temp_dir, backend="sqlite", auto_backup=False
            )

            # Simulate concurrent operations
            import threading
            import time

            results = []

            def store_dataset(index):
                try:
                    dataset = self.create_test_dataset(
                        dataset_id=f"concurrent_{index}",
                        data={}
                    )
                    result = storage.store_dataset(dataset)
                    results.append(result)
                except Exception as e:
                    results.append(e)

            # Create multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=store_dataset, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Check results
            successful_results = [r for r in results if r is True]
            assert len(successful_results) >= 4  # At least most should succeed


class TestDataExporter:
    """Test data exporter implementation."""

    def test_initialization(self):
        """Test data exporter initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = DataExporter(temp_dir)

            assert exporter.output_dir == Path(temp_dir)
            assert exporter.output_dir.exists()

    def test_export_falsification_results(self):
        """Test exporting falsification results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = DataExporter(temp_dir)

            # Mock falsification results
            from apgi_framework.core.data_models import FalsificationResult

            results = [
                FalsificationResult(
                    test_type="primary",
                    is_falsified=False,
                    confidence_level=0.95,
                    effect_size=0.8,
                    p_value=0.03,
                    statistical_power=0.85,
                )
            ]

            # Export to JSON
            export_path = exporter.export_falsification_results(results, format="json")

            assert export_path is not None
            assert Path(export_path).exists()
            assert export_path.endswith(".json")

    def test_export_experimental_trials(self):
        """Test exporting experimental trials."""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = DataExporter(temp_dir)

            # Mock experimental trials using correct data model
            from apgi_framework.core.data_models import (
                ExperimentalTrial,
                APGIParameters,
                NeuralSignatures,
                ConsciousnessAssessment,
            )

            trials = [
                ExperimentalTrial(
                    trial_id="trial_001",
                    participant_id="P001",
                    condition="exteroceptive",
                    trial_number=1,
                    neural_signatures=NeuralSignatures(p3b_amplitude=5.2),
                    consciousness_assessment=ConsciousnessAssessment(
                        subjective_report=True
                    ),
                )
            ]

            # Export to CSV
            export_path = exporter.export_experimental_trials(trials, format="csv")

            assert export_path is not None
            assert Path(export_path).exists()
            assert export_path.endswith(".csv")


class TestReportGenerator:
    """Test report generator implementation."""

    def test_initialization(self):
        """Test report generator initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(temp_dir)

            assert generator.output_dir == Path(temp_dir)
            assert generator.output_dir.exists()

    def test_generate_falsification_report(self):
        """Test generating falsification report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(temp_dir)

            # Mock data
            from apgi_framework.core.data_models import (
                FalsificationResult,
                ExperimentalTrial,
                StatisticalSummary,
            )

            results = [
                FalsificationResult(
                    test_type="primary",
                    is_falsified=False,
                    confidence_level=0.95,
                    effect_size=0.8,
                    p_value=0.03,
                    statistical_power=0.85,
                )
            ]

            # Mock experimental trials using correct data model
            from apgi_framework.core.data_models import (
                ExperimentalTrial,
                APGIParameters,
                NeuralSignatures,
                ConsciousnessAssessment,
            )

            trials = [
                ExperimentalTrial(
                    trial_id="trial_001",
                    participant_id="P001",
                    condition="exteroceptive",
                    trial_number=1,
                    neural_signatures=NeuralSignatures(p3b_amplitude=5.2),
                    consciousness_assessment=ConsciousnessAssessment(
                        subjective_report=True
                    ),
                )
            ]

            stats = StatisticalSummary(
                total_trials=1000,
                statistical_power=0.85,
                mean_effect_size=0.8,
            )

            # Generate report (this is the actual method)
            report = generator.generate_falsification_report(
                "test_exp_001", results, trials, stats
            )

            assert report is not None
            assert report.experiment_id == "test_exp_001"

    def test_save_report(self):
        """Test saving report to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ReportGenerator(temp_dir)

            # Mock report using correct data model
            from apgi_framework.data.report_generator import (
                FalsificationReport,
                ReportSection,
            )
            from apgi_framework.core.data_models import StatisticalSummary

            report = FalsificationReport(
                experiment_id="test_exp_001",
                timestamp=datetime.now(),
                test_type="primary",
                summary="Test summary",
                conclusions="Test conclusions",
                statistical_summary=StatisticalSummary(total_trials=1000),
                sections=[ReportSection(title="Test Section", content="Test content")],
                metadata={"test": True},
            )

            # Save report (this is the actual method)
            report_path = generator.save_report(report, format="json")

            assert report_path is not None
            assert Path(report_path).exists()
            assert report_path.endswith(".json")


if __name__ == "__main__":
    pytest.main([__file__])
