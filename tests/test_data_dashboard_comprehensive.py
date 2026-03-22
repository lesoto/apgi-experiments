"""
Comprehensive tests for data/dashboard.py module.

Tests for DataDashboard class to improve coverage from 15% to target 80%+.
"""

import pytest
import pandas as pd
from unittest.mock import Mock
from datetime import datetime


class TestDataDashboardImports:
    """Test module imports."""

    def test_module_imports(self):
        """Test that dashboard module can be imported."""
        from apgi_framework.data import dashboard

        assert hasattr(dashboard, "DataDashboard")


class TestDataDashboardInitialization:
    """Test DataDashboard initialization."""

    def test_basic_initialization(self):
        """Test basic dashboard initialization."""
        from apgi_framework.data.dashboard import DataDashboard

        dashboard = DataDashboard()
        assert dashboard.experiments == {}
        assert dashboard.summary_stats == {}

    def test_initialization_with_storage(self):
        """Test initialization with storage manager."""
        from apgi_framework.data.dashboard import DataDashboard

        mock_storage = Mock()
        dashboard = DataDashboard(storage_manager=mock_storage)
        assert dashboard.storage_manager == mock_storage


class TestDataDashboardExperimentManagement:
    """Test experiment management functionality."""

    @pytest.fixture
    def dashboard(self):
        """Create a dashboard instance for testing."""
        from apgi_framework.data.dashboard import DataDashboard

        return DataDashboard()

    def test_add_experiment(self, dashboard):
        """Test adding an experiment to dashboard."""
        experiment_data = {
            "experiment_id": "exp_001",
            "name": "Test Experiment",
            "participants": 20,
            "trials": 100,
            "conditions": ["control", "treatment"],
            "created_at": datetime.now(),
        }

        dashboard.add_experiment(experiment_data)
        assert "exp_001" in dashboard.experiments
        assert dashboard.experiments["exp_001"]["name"] == "Test Experiment"

    def test_remove_experiment(self, dashboard):
        """Test removing an experiment."""
        dashboard.experiments["exp_001"] = {"name": "Test"}

        result = dashboard.remove_experiment("exp_001")
        assert result is True
        assert "exp_001" not in dashboard.experiments

    def test_remove_nonexistent_experiment(self, dashboard):
        """Test removing experiment that doesn't exist."""
        result = dashboard.remove_experiment("nonexistent")
        assert result is False

    def test_get_experiment(self, dashboard):
        """Test getting experiment data."""
        dashboard.experiments["exp_001"] = {"name": "Test Experiment"}

        exp = dashboard.get_experiment("exp_001")
        assert exp["name"] == "Test Experiment"

    def test_get_nonexistent_experiment(self, dashboard):
        """Test getting experiment that doesn't exist."""
        exp = dashboard.get_experiment("nonexistent")
        assert exp is None

    def test_list_experiments(self, dashboard):
        """Test listing all experiments."""
        dashboard.experiments = {
            "exp_001": {"name": "Exp 1"},
            "exp_002": {"name": "Exp 2"},
        }

        exps = dashboard.list_experiments()
        assert len(exps) == 2
        assert "exp_001" in exps
        assert "exp_002" in exps


class TestDataDashboardDataOperations:
    """Test data operations on dashboard."""

    @pytest.fixture
    def dashboard(self):
        """Create a dashboard instance for testing."""
        from apgi_framework.data.dashboard import DataDashboard

        return DataDashboard()

    def test_add_data_to_experiment(self, dashboard):
        """Test adding data to an experiment."""
        dashboard.experiments["exp_001"] = {"data": []}

        data = {"trial": 1, "response_time": 0.5, "correct": True}
        dashboard.add_data_to_experiment("exp_001", data)

        assert len(dashboard.experiments["exp_001"]["data"]) == 1

    def test_add_data_to_nonexistent_experiment(self, dashboard):
        """Test adding data to nonexistent experiment creates it."""
        data = {"trial": 1, "response_time": 0.5}

        dashboard.add_data_to_experiment("exp_new", data)
        assert "exp_new" in dashboard.experiments

    def test_get_experiment_data_as_dataframe(self, dashboard):
        """Test getting experiment data as DataFrame."""
        dashboard.experiments["exp_001"] = {
            "data": [{"trial": 1, "rt": 0.5}, {"trial": 2, "rt": 0.6}]
        }

        df = dashboard.get_experiment_data_as_dataframe("exp_001")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_get_empty_experiment_data(self, dashboard):
        """Test getting data for experiment with no data."""
        dashboard.experiments["exp_001"] = {"data": []}

        df = dashboard.get_experiment_data_as_dataframe("exp_001")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


class TestDataDashboardStatistics:
    """Test statistics calculation."""

    @pytest.fixture
    def dashboard(self):
        """Create a dashboard instance for testing."""
        from apgi_framework.data.dashboard import DataDashboard

        return DataDashboard()

    def test_calculate_summary_statistics(self, dashboard):
        """Test calculating summary statistics."""
        dashboard.experiments = {
            "exp_001": {
                "participants": 20,
                "trials": 100,
                "data": [
                    {"response_time": 0.5, "correct": True},
                    {"response_time": 0.6, "correct": False},
                    {"response_time": 0.4, "correct": True},
                ],
            }
        }

        stats = dashboard.calculate_summary_statistics()
        assert "exp_001" in stats

    def test_update_experiment_stats(self, dashboard):
        """Test updating statistics for an experiment."""
        dashboard.experiments["exp_001"] = {
            "data": [{"rt": 0.5}, {"rt": 0.6}, {"rt": 0.4}]
        }

        dashboard.update_experiment_stats("exp_001")
        assert "exp_001" in dashboard.summary_stats

    def test_get_summary_stats(self, dashboard):
        """Test getting summary statistics."""
        dashboard.summary_stats = {"total_experiments": 5}

        stats = dashboard.get_summary_stats()
        assert stats["total_experiments"] == 5


class TestDataDashboardFiltering:
    """Test filtering and search functionality."""

    @pytest.fixture
    def dashboard(self):
        """Create a dashboard instance for testing."""
        from apgi_framework.data.dashboard import DataDashboard

        return DataDashboard()

    def test_filter_experiments_by_name(self, dashboard):
        """Test filtering experiments by name."""
        dashboard.experiments = {
            "exp_001": {"name": "Memory Study"},
            "exp_002": {"name": "Attention Study"},
            "exp_003": {"name": "Memory Recall"},
        }

        results = dashboard.filter_experiments(name_contains="Memory")
        assert len(results) == 2

    def test_filter_experiments_by_date(self, dashboard):
        """Test filtering experiments by date range."""
        from datetime import datetime, timedelta

        dashboard.experiments = {
            "exp_001": {
                "name": "Old Exp",
                "created_at": datetime.now() - timedelta(days=30),
            },
            "exp_002": {
                "name": "New Exp",
                "created_at": datetime.now() - timedelta(days=5),
            },
        }

        results = dashboard.filter_experiments(
            date_from=datetime.now() - timedelta(days=10)
        )
        assert len(results) == 1
        assert results[0]["name"] == "New Exp"

    def test_search_experiments(self, dashboard):
        """Test searching experiments."""
        dashboard.experiments = {
            "exp_001": {
                "name": "Visual Attention",
                "description": "Study of visual attention",
            },
            "exp_002": {
                "name": "Auditory Memory",
                "description": "Study of auditory memory",
            },
        }

        results = dashboard.search_experiments("visual")
        assert len(results) == 1
        assert results[0]["name"] == "Visual Attention"


class TestDataDashboardExport:
    """Test export functionality."""

    @pytest.fixture
    def dashboard(self):
        """Create a dashboard instance for testing."""
        from apgi_framework.data.dashboard import DataDashboard

        return DataDashboard()

    def test_export_experiment_summary(self, dashboard):
        """Test exporting experiment summary."""
        dashboard.experiments = {"exp_001": {"name": "Test", "participants": 20}}

        summary = dashboard.export_experiment_summary()
        assert "exp_001" in summary

    def test_export_to_json(self, dashboard):
        """Test exporting to JSON format."""
        dashboard.experiments = {"exp_001": {"name": "Test Experiment"}}

        json_data = dashboard.export_to_json()
        assert isinstance(json_data, str)
        assert "Test Experiment" in json_data

    def test_export_to_csv(self, dashboard):
        """Test exporting experiment data to CSV."""
        dashboard.experiments["exp_001"] = {
            "data": [{"trial": 1, "rt": 0.5}, {"trial": 2, "rt": 0.6}]
        }

        csv_data = dashboard.export_to_csv("exp_001")
        assert isinstance(csv_data, str)
        assert "trial" in csv_data


class TestDataDashboardVisualization:
    """Test visualization preparation methods."""

    @pytest.fixture
    def dashboard(self):
        """Create a dashboard instance for testing."""
        from apgi_framework.data.dashboard import DataDashboard

        return DataDashboard()

    def test_prepare_time_series_data(self, dashboard):
        """Test preparing data for time series visualization."""
        dashboard.experiments["exp_001"] = {
            "data": [
                {"trial": 1, "accuracy": 0.8, "timestamp": 1},
                {"trial": 2, "accuracy": 0.9, "timestamp": 2},
                {"trial": 3, "accuracy": 0.85, "timestamp": 3},
            ]
        }

        series = dashboard.prepare_time_series_data("exp_001", "accuracy", "timestamp")
        assert isinstance(series, dict)

    def test_prepare_scatter_data(self, dashboard):
        """Test preparing data for scatter plot."""
        dashboard.experiments["exp_001"] = {
            "data": [{"rt": 0.5, "accuracy": 0.8}, {"rt": 0.6, "accuracy": 0.9}]
        }

        data = dashboard.prepare_scatter_data("exp_001", "rt", "accuracy")
        assert isinstance(data, dict)

    def test_prepare_histogram_data(self, dashboard):
        """Test preparing data for histogram."""
        dashboard.experiments["exp_001"] = {
            "data": [{"rt": 0.5}, {"rt": 0.6}, {"rt": 0.5}]
        }

        data = dashboard.prepare_histogram_data("exp_001", "rt")
        assert isinstance(data, list) or isinstance(data, dict)
