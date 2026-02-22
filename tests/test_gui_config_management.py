"""
Test suite for GUI configuration management and parameter handling.

This module tests the integration between GUI components and the configuration system,
ensuring proper parameter validation, loading, and persistence.
"""

import tempfile
import unittest
from pathlib import Path

try:
    import tkinter as tk

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from apgi_gui.config import DefaultParameters, ParameterConfig
    from apgi_framework.config.manager import ConfigManager
    from apgi_gui.components.common_gui_components import ParameterInput, ResultsDisplay
    from apgi_gui.utils.config import ConfigLoader, ConfigValidator

    GUI_CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"GUI configuration components not available: {e}")
    GUI_CONFIG_AVAILABLE = False


@unittest.skipUnless(
    TKINTER_AVAILABLE and GUI_CONFIG_AVAILABLE, "GUI config components not available"
)
class TestParameterConfig(unittest.TestCase):
    """Test cases for parameter configuration GUI components."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.config = ParameterConfig()
        self.default_params = DefaultParameters()

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, "root") and self.root:
            self.root.destroy()

    def test_default_parameters_initialization(self):
        """Test DefaultParameters initializes with expected structure."""
        self.assertIsInstance(self.default_params.parameters, dict)
        self.assertGreater(len(self.default_params.parameters), 0)

        # Check for expected parameter categories
        self.assertIn("consciousness", self.default_params.parameters)
        self.assertIn("experiment", self.default_params.parameters)

    def test_parameter_config_validation(self):
        """Test parameter configuration validation."""
        # Valid configuration
        valid_config = {
            "consciousness": {"threshold": 0.5, "sensitivity": 0.8},
            "experiment": {"duration": 300, "trials": 100},
        }
        self.assertTrue(self.config.validate_config(valid_config))

        # Invalid configuration
        invalid_config = {
            "consciousness": {"threshold": 1.5},  # Invalid range
            "experiment": {"duration": -100},  # Invalid negative value
        }
        self.assertFalse(self.config.validate_config(invalid_config))

    def test_parameter_config_save_load(self):
        """Test saving and loading parameter configurations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"

            test_config = {
                "consciousness": {"threshold": 0.7, "sensitivity": 0.9},
                "experiment": {"duration": 600, "trials": 50},
            }

            # Save configuration
            self.config.save_config(test_config, config_file)

            # Load configuration
            loaded_config = self.config.load_config(config_file)

            self.assertEqual(loaded_config, test_config)


@unittest.skipUnless(
    TKINTER_AVAILABLE and GUI_CONFIG_AVAILABLE, "GUI config components not available"
)
class TestConfigManagerIntegration(unittest.TestCase):
    """Test integration between GUI and ConfigManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = ConfigManager(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_config_manager_gui_integration(self):
        """Test ConfigManager integration with GUI components."""
        # Test loading default parameters
        defaults = self.config_manager.get_default_parameters()
        self.assertIsInstance(defaults, dict)
        self.assertIn("consciousness", defaults)

    def test_parameter_validation_integration(self):
        """Test parameter validation through ConfigManager."""
        # Valid parameters
        valid_params = {
            "consciousness_threshold": 0.6,
            "experiment_duration": 300,
            "trials_per_block": 20,
        }
        self.assertTrue(self.config_manager.validate_parameters(valid_params))

        # Invalid parameters
        invalid_params = {
            "consciousness_threshold": 1.5,  # Out of range
            "experiment_duration": -100,  # Negative
        }
        self.assertFalse(self.config_manager.validate_parameters(invalid_params))


@unittest.skipUnless(
    TKINTER_AVAILABLE and GUI_CONFIG_AVAILABLE, "GUI config components not available"
)
class TestCommonGUIComponents(unittest.TestCase):
    """Test cases for common GUI components."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, "root") and self.root:
            self.root.destroy()

    def test_parameter_input_component(self):
        """Test ParameterInput component functionality."""
        # Create mock parameter input
        param_input = ParameterInput(self.root, "test_param", "Test Parameter", 0.5)

        # Test initial value
        self.assertEqual(param_input.get_value(), 0.5)

        # Test setting value
        param_input.set_value(0.8)
        self.assertEqual(param_input.get_value(), 0.8)

    def test_results_display_component(self):
        """Test ResultsDisplay component functionality."""
        results_display = ResultsDisplay(self.root)

        # Test displaying results
        test_results = {
            "experiment_id": "test_exp",
            "consciousness_score": 0.75,
            "confidence": 0.9,
        }

        # This should not raise an exception
        try:
            results_display.display_results(test_results)
        except Exception as e:
            # GUI operations might fail in headless environment
            self.assertIn("display", str(e).lower())


@unittest.skipUnless(GUI_CONFIG_AVAILABLE, "GUI config utils not available")
class TestConfigUtils(unittest.TestCase):
    """Test cases for GUI configuration utilities."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_loader = ConfigLoader(self.temp_dir)
        self.config_validator = ConfigValidator()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_config_loader_functionality(self):
        """Test ConfigLoader functionality."""
        # Create test config file
        config_file = self.temp_dir / "test_config.yaml"
        config_file.write_text(
            """
consciousness:
  threshold: 0.6
  sensitivity: 0.8
experiment:
  duration: 300
  trials: 50
"""
        )

        # Load configuration
        config = self.config_loader.load_config("test_config.yaml")
        self.assertIsNotNone(config)
        self.assertIn("consciousness", config)

    def test_config_validator_functionality(self):
        """Test ConfigValidator functionality."""
        # Valid configuration
        valid_config = {
            "consciousness": {"threshold": 0.5, "sensitivity": 0.7},
            "experiment": {"duration": 300, "trials": 100},
        }
        self.assertTrue(self.config_validator.validate(valid_config))

        # Invalid configuration
        invalid_config = {
            "consciousness": {"threshold": -0.1},  # Invalid negative value
            "experiment": {"duration": 0},  # Invalid zero duration
        }
        self.assertFalse(self.config_validator.validate(invalid_config))

        # Get validation errors
        errors = self.config_validator.get_validation_errors(invalid_config)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
