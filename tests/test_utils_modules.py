"""
Comprehensive unit tests for utility modules.

This test suite provides coverage for all major utility functions in the utils directory.
Tests are organized by module and cover both happy paths and error conditions.
"""

import pytest
import tempfile
import shutil
import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import threading
import time

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import utility modules to test
try:
    from utils.backup_manager import BackupManager
    from utils.cache_manager import CacheManager
    from utils.config_manager import ConfigManager
    from utils.error_handler import ErrorHandler
    from utils.performance_profiler import PerformanceProfiler
    from utils.parameter_validator import APGIParameterValidator
    from utils.data_validation import DataValidator
except ImportError as e:
    # Try alternative import path if utils is not in Python path
    try:
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from utils.backup_manager import BackupManager
        from utils.cache_manager import CacheManager
        from utils.config_manager import ConfigManager
        from utils.error_handler import ErrorHandler
        from utils.performance_profiler import PerformanceProfiler
        from utils.parameter_validator import APGIParameterValidator
        from utils.data_validation import DataValidator
    except ImportError:
        pytest.skip(f"Utility modules not available: {e}", allow_module_level=True)


class TestBackupManager:
    """Test cases for BackupManager functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_manager = BackupManager(str(Path(self.temp_dir) / "backups"))

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_backup_creation(self):
        """Test creating a backup."""
        # Create a test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")

        # Test backup creation
        backup_path = self.backup_manager.create_backup(str(test_file))
        assert backup_path.exists()
        assert backup_path.read_text() == "test content"

    def test_backup_restoration(self):
        """Test restoring a backup."""
        # Create and backup a test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("original content")
        backup_path = self.backup_manager.create_backup(str(test_file))

        # Modify original file
        test_file.write_text("modified content")

        # Restore from backup
        self.backup_manager.restore_backup(str(test_file), str(backup_path))
        assert test_file.read_text() == "original content"

    def test_backup_listing(self):
        """Test listing available backups."""
        # Create multiple backups
        for i in range(3):
            test_file = Path(self.temp_dir) / f"test_{i}.txt"
            test_file.write_text(f"content {i}")
            self.backup_manager.create_backup(str(test_file))

        backups = self.backup_manager.list_backups()
        assert len(backups) >= 3

    def test_backup_cleanup(self):
        """Test cleaning up old backups."""
        # Create old backup
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")
        backup_path = self.backup_manager.create_backup(str(test_file))

        # Mock old timestamp
        old_time = time.time() - (30 * 24 * 60 * 60)  # 30 days ago
        os.utime(backup_path, (old_time, old_time))

        # Clean up old backups
        cleaned = self.backup_manager.cleanup_old_backups(max_age_days=7)
        assert cleaned > 0


class TestCacheManager:
    """Test cases for CacheManager functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(
            str(Path(self.temp_dir) / "cache"), max_size_mb=1
        )

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_storage_and_retrieval(self):
        """Test storing and retrieving cached data."""
        key = "test_key"
        value = {"data": "test_value", "number": 42}

        # Store data
        self.cache_manager.set(key, value)

        # Retrieve data
        retrieved = self.cache_manager.get(key)
        assert retrieved == value

    def test_cache_expiration(self):
        """Test cache expiration."""
        key = "test_key"
        value = "test_value"

        # Store with short TTL
        self.cache_manager.set(key, value, ttl_seconds=1)

        # Should be available immediately
        assert self.cache_manager.get(key) == value

        # Wait for expiration
        time.sleep(2)
        assert self.cache_manager.get(key) is None

    def test_cache_size_limit(self):
        """Test cache size limit enforcement."""
        # Fill cache beyond limit
        large_data = "x" * (2 * 1024 * 1024)  # 2MB

        for i in range(5):
            self.cache_manager.set(f"key_{i}", large_data)

        # Cache should enforce size limit
        assert len(self.cache_manager.list_keys()) <= 3  # Approximate

    def test_cache_clear(self):
        """Test clearing the cache."""
        # Add some data
        for i in range(3):
            self.cache_manager.set(f"key_{i}", f"value_{i}")

        # Clear cache
        self.cache_manager.clear()
        assert len(self.cache_manager.list_keys()) == 0


class TestConfigManager:
    """Test cases for ConfigManager functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "config.json"
        self.config_manager = ConfigManager(str(self.config_file))

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_creation_and_loading(self):
        """Test creating and loading configuration."""
        config_data = {"param1": "value1", "param2": 42, "param3": True}

        # Save configuration
        self.config_manager.save_config(config_data)

        # Load configuration
        loaded_config = self.config_manager.load_config()
        assert loaded_config == config_data

    def test_config_update(self):
        """Test updating configuration values."""
        initial_config = {"param1": "value1", "param2": 42}
        self.config_manager.save_config(initial_config)

        # Update specific parameter
        self.config_manager.update_config("param2", 100)
        updated_config = self.config_manager.load_config()
        assert updated_config["param2"] == 100
        assert updated_config["param1"] == "value1"

    def test_config_validation(self):
        """Test configuration validation."""
        schema = {
            "type": "object",
            "properties": {"param1": {"type": "string"}, "param2": {"type": "number"}},
            "required": ["param1"],
        }

        # Valid config should pass
        valid_config = {"param1": "value1", "param2": 42}
        assert self.config_manager.validate_config(valid_config, schema) is True

        # Invalid config should fail
        invalid_config = {"param2": "not_a_number"}
        assert self.config_manager.validate_config(invalid_config, schema) is False


class TestErrorHandler:
    """Test cases for ErrorHandler functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.error_handler = ErrorHandler(str(Path(self.temp_dir) / "errors.log"))

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_error_logging(self):
        """Test error logging."""
        test_error = ValueError("Test error message")

        # Log error
        self.error_handler.log_error(test_error, context="test_context")

        # Check error was logged
        errors = self.error_handler.get_recent_errors()
        assert len(errors) > 0
        assert "Test error message" in str(errors[0])

    def test_error_recovery_strategies(self):
        """Test error recovery strategies."""

        # Register recovery strategy
        def recovery_strategy(error, context):
            return "recovered"

        self.error_handler.register_recovery_strategy(ValueError, recovery_strategy)

        # Test recovery
        result = self.error_handler.handle_error(ValueError("test"), {})
        assert result == "recovered"

    def test_error_statistics(self):
        """Test error statistics tracking."""
        # Log multiple errors
        for i in range(5):
            self.error_handler.log_error(ValueError(f"Error {i}"))

        stats = self.error_handler.get_error_statistics()
        assert stats["total_errors"] == 5
        assert "ValueError" in stats["error_types"]


class TestPerformanceProfiler:
    """Test cases for PerformanceProfiler functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.profiler = PerformanceProfiler(str(Path(self.temp_dir) / "profiles"))

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_function_profiling(self):
        """Test profiling function execution."""

        @self.profiler.profile_function
        def test_function():
            time.sleep(0.1)
            return "result"

        # Execute profiled function
        result = test_function()
        assert result == "result"

        # Check profiling data
        profiles = self.profiler.get_profiles()
        assert len(profiles) > 0
        assert profiles[0]["execution_time"] > 0.05

    def test_context_manager_profiling(self):
        """Test profiling using context manager."""
        with self.profiler.profile_block("test_block"):
            time.sleep(0.05)

        profiles = self.profiler.get_profiles()
        assert any(p["name"] == "test_block" for p in profiles)

    def test_performance_report(self):
        """Test generating performance report."""
        # Profile some operations
        with self.profiler.profile_block("operation1"):
            time.sleep(0.01)

        with self.profiler.profile_block("operation2"):
            time.sleep(0.02)

        # Generate report
        report = self.profiler.generate_report()
        assert "operation1" in report
        assert "operation2" in report


class TestDependencyChecker:
    """Test cases for DependencyChecker functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.dependency_checker = DependencyChecker()

    def test_dependency_checking(self):
        """Test checking package dependencies."""
        # Check for built-in package
        result = self.dependency_checker.check_dependency("sys")
        assert result["installed"] is True

        # Check for non-existent package
        result = self.dependency_checker.check_dependency("nonexistent_package_12345")
        assert result["installed"] is False

    def test_version_checking(self):
        """Test checking package versions."""
        result = self.dependency_checker.check_dependency("sys")
        assert "version" in result
        assert result["version"] is not None

    def test_dependency_resolution(self):
        """Test dependency resolution."""
        dependencies = ["sys", "os", "json"]
        resolved = self.dependency_checker.resolve_dependencies(dependencies)

        assert all(dep["installed"] for dep in resolved.values())
        assert len(resolved) == len(dependencies)


class TestParameterValidator:
    """Test cases for ParameterValidator functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.validator = ParameterValidator()

    def test_numeric_validation(self):
        """Test numeric parameter validation."""
        # Valid number
        assert self.validator.validate_number(42, min_value=0, max_value=100) is True
        assert self.validator.validate_number(3.14, min_value=0) is True

        # Invalid number
        assert self.validator.validate_number(-5, min_value=0) is False
        assert self.validator.validate_number(150, max_value=100) is False

    def test_string_validation(self):
        """Test string parameter validation."""
        # Valid string
        assert (
            self.validator.validate_string("test", min_length=1, max_length=10) is True
        )

        # Invalid string
        assert self.validator.validate_string("", min_length=1) is False
        assert self.validator.validate_string("x" * 20, max_length=10) is False

    def test_email_validation(self):
        """Test email format validation."""
        # Valid emails
        assert self.validator.validate_email("test@example.com") is True
        assert self.validator.validate_email("user.name@domain.co.uk") is True

        # Invalid emails
        assert self.validator.validate_email("invalid_email") is False
        assert self.validator.validate_email("@domain.com") is False

    def test_range_validation(self):
        """Test range validation."""
        # Within range
        assert self.validator.validate_range(50, 0, 100) is True

        # Outside range
        assert self.validator.validate_range(-5, 0, 100) is False
        assert self.validator.validate_range(150, 0, 100) is False


class TestDataValidator:
    """Test cases for DataValidator functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.validator = DataValidator()

    def test_data_type_validation(self):
        """Test data type validation."""
        # Correct types
        assert self.validator.validate_type(42, int) is True
        assert self.validator.validate_type("test", str) is True
        assert self.validator.validate_type([1, 2, 3], list) is True

        # Incorrect types
        assert self.validator.validate_type("42", int) is False
        assert self.validator.validate_type(42, str) is False

    def test_data_structure_validation(self):
        """Test data structure validation."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "email": {"type": "string", "format": "email"},
            },
            "required": ["name", "age"],
        }

        # Valid data
        valid_data = {"name": "John", "age": 30, "email": "john@example.com"}
        assert self.validator.validate_structure(valid_data, schema) is True

        # Invalid data
        invalid_data = {"name": "John", "age": "thirty"}
        assert self.validator.validate_structure(invalid_data, schema) is False

    def test_data_quality_checks(self):
        """Test data quality assessment."""
        # Test with clean data
        clean_data = [1, 2, 3, 4, 5]
        quality = self.validator.assess_data_quality(clean_data)
        assert quality["completeness"] == 1.0
        assert quality["consistency"] == 1.0

        # Test with missing data
        dirty_data = [1, None, 3, None, 5]
        quality = self.validator.assess_data_quality(dirty_data)
        assert quality["completeness"] < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
