"""
Configuration management system for experimental parameters.

This module provides centralized configuration management for the APGI Framework,
including parameter validation, default values, and experimental settings.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json
from pathlib import Path

from .exceptions import ConfigurationError
from apgi_framework.utils.path_utils import get_path_manager


@dataclass
class APGIParameters:
    """Core APGI equation parameters."""

    extero_precision: float = 2.0
    intero_precision: float = 1.5
    extero_error: float = 1.2
    intero_error: float = 0.8
    somatic_gain: float = 1.3
    threshold: float = 3.5
    steepness: float = 2.0

    def __post_init__(self):
        """Validate parameter ranges."""
        # Import here to avoid circular dependency
        try:
            from .validation.parameter_validator import get_validator

            validator = get_validator()
            result = validator.validate_apgi_parameters(
                extero_precision=self.extero_precision,
                intero_precision=self.intero_precision,
                extero_error=self.extero_error,
                intero_error=self.intero_error,
                somatic_gain=self.somatic_gain,
                threshold=self.threshold,
                steepness=self.steepness,
            )
            if not result.is_valid:
                raise ConfigurationError(
                    f"Invalid APGI parameters:\n{result.get_message()}"
                )
        except ImportError:
            # Fallback to basic validation if validator not available
            if self.extero_precision <= 0:
                raise ConfigurationError("Exteroceptive precision must be positive")
            if self.intero_precision <= 0:
                raise ConfigurationError("Interoceptive precision must be positive")
            if self.somatic_gain <= 0:
                raise ConfigurationError("Somatic gain must be positive")
            if self.steepness <= 0:
                raise ConfigurationError("Steepness parameter must be positive")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    initial_delay: float = 1.0
    backoff_factor: float = 2.0
    max_delay: float = 30.0


@dataclass
class PerformanceThresholds:
    """Performance thresholds for validation."""

    # Response time thresholds
    min_rt: float = 0.1  # seconds
    max_rt: float = 10.0  # seconds
    outlier_iqr_multiplier: float = 3.0

    # Accuracy thresholds
    min_accuracy: float = 0.5
    target_accuracy: float = 0.8

    # Consistency thresholds
    min_consistency: float = 0.7
    stability_threshold: float = 0.8

    # Training criteria
    min_learning_curve_slope: float = 0.1
    min_performance_stability: float = 0.7

    # Metacognitive thresholds
    max_confidence_variance: float = 0.25
    min_meta_d_prime: float = 0.0

    # Statistical thresholds
    confidence_level: float = 0.95  # for CI calculations
    min_reliability_insufficient: float = 0.3
    min_reliability_moderate: float = 0.5

    # Fatigue and learning modifiers
    fatigue_impact_factor: float = 0.2
    learning_improvement_factor: float = 0.1
    difficulty_impact_factor: float = 0.3
    impulsivity_impact_factor: float = 0.1
    motivation_impact_factor: float = 0.1


@dataclass
class StimulusParameters:
    """Parameters for stimulus generation."""

    # QUEST+ parameters
    stimulus_min: float = 0.01
    stimulus_max: float = 1.0
    stimulus_steps: int = 50
    threshold_min: float = 0.01
    threshold_max: float = 1.0
    threshold_steps: int = 40
    slope_min: float = 1.0
    slope_max: float = 10.0
    slope_steps: int = 20
    lapse_rate: float = 0.02
    guess_rate: float = 0.5

    # Convergence criteria
    min_trials: int = 20
    max_trials: int = 200
    convergence_criterion: float = 0.05
    min_reversals: int = 4


@dataclass
class ExperimentalConfig:
    """Configuration for experimental parameters and settings."""

    n_trials: int = 1000
    n_participants: int = 100
    session_duration: float = 60.0  # minutes
    random_seed: Optional[int] = None
    output_directory: str = "results"
    log_level: str = "INFO"
    save_intermediate: bool = True

    # Neural signature thresholds
    p3b_threshold: float = 5.0  # μV
    gamma_plv_threshold: float = 0.3
    gamma_duration_threshold: int = 200  # ms
    bold_z_threshold: float = 3.1
    pci_threshold: float = 0.4

    # AI/ACC validation thresholds
    ai_acc_gamma_threshold: float = 0.25  # PLV threshold for AI/ACC

    # Statistical parameters
    alpha_level: float = 0.05
    effect_size_threshold: float = 0.5
    power_threshold: float = 0.8

    def __post_init__(self):
        """Validate experimental configuration."""
        # Import here to avoid circular dependency
        try:
            from .validation.parameter_validator import get_validator

            validator = get_validator()
            result = validator.validate_experimental_config(
                n_trials=self.n_trials,
                n_participants=self.n_participants,
                alpha_level=self.alpha_level,
                effect_size_threshold=self.effect_size_threshold,
                power_threshold=self.power_threshold,
            )
            if not result.is_valid:
                raise ConfigurationError(
                    f"Invalid experimental configuration:\n{result.get_message()}"
                )
        except ImportError:
            # Fallback to basic validation if validator not available
            if self.n_trials <= 0:
                raise ConfigurationError("Number of trials must be positive")
            if self.n_participants <= 0:
                raise ConfigurationError("Number of participants must be positive")
            if not 0 < self.alpha_level < 1:
                raise ConfigurationError("Alpha level must be between 0 and 1")


class ConfigManager:
    """Manages configuration loading, validation, and access."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file. If None, uses defaults.
        """
        self.path_manager = get_path_manager()
        self.config_path = config_path
        self.apgi_params = APGIParameters()
        self.experimental_config = ExperimentalConfig()
        self.retry_config = RetryConfig()
        self.performance_thresholds = PerformanceThresholds()
        self.stimulus_params = StimulusParameters()

        if config_path:
            config_file = self.path_manager.resolve_path(config_path)
            if config_file.exists():
                self.load_config(config_path)

    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file.

        Args:
            config_path: Path to JSON configuration file.

        Raises:
            ConfigurationError: If configuration file is invalid.
        """
        try:
            config_file = self.path_manager.resolve_path(config_path)
            with open(config_file, "r") as f:
                config_data = json.load(f)

            # Validate configuration structure
            self._validate_config_structure(config_data)

            # Load APGI parameters with validation
            if "apgi_parameters" in config_data:
                apgi_data = config_data["apgi_parameters"]
                self._validate_parameter_section("apgi_parameters", apgi_data)
                self.apgi_params = APGIParameters(**apgi_data)

            # Load experimental configuration with validation
            if "experimental_config" in config_data:
                exp_data = config_data["experimental_config"]
                self._validate_parameter_section("experimental_config", exp_data)
                self.experimental_config = ExperimentalConfig(**exp_data)

            # Load retry configuration with validation
            if "retry_config" in config_data:
                retry_data = config_data["retry_config"]
                self._validate_parameter_section("retry_config", retry_data)
                self.retry_config = RetryConfig(**retry_data)

            # Load performance thresholds with validation
            if "performance_thresholds" in config_data:
                perf_data = config_data["performance_thresholds"]
                self._validate_parameter_section("performance_thresholds", perf_data)
                self.performance_thresholds = PerformanceThresholds(**perf_data)

            # Load stimulus parameters with validation
            if "stimulus_parameters" in config_data:
                stim_data = config_data["stimulus_parameters"]
                self._validate_parameter_section("stimulus_parameters", stim_data)
                self.stimulus_params = StimulusParameters(**stim_data)

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise ConfigurationError(f"Invalid configuration file: {e}")
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def save_config(self, config_path: str) -> None:
        """Save current configuration to JSON file.

        Args:
            config_path: Path where to save configuration file.
        """
        config_data = {
            "apgi_parameters": self.apgi_params.__dict__,
            "experimental_config": self.experimental_config.__dict__,
            "retry_config": self.retry_config.__dict__,
            "performance_thresholds": self.performance_thresholds.__dict__,
            "stimulus_parameters": self.stimulus_params.__dict__,
        }

        # Create directory if it doesn't exist
        config_file = self.path_manager.resolve_path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)

    def get_apgi_parameters(self) -> APGIParameters:
        """Get current APGI parameters."""
        return self.apgi_params

    def get_experimental_config(self) -> ExperimentalConfig:
        """Get current experimental configuration."""
        return self.experimental_config

    def get_retry_config(self) -> RetryConfig:
        """Get current retry configuration."""
        return self.retry_config

    def get_performance_thresholds(self) -> PerformanceThresholds:
        """Get current performance thresholds."""
        return self.performance_thresholds

    def get_stimulus_parameters(self) -> StimulusParameters:
        """Get current stimulus parameters."""
        return self.stimulus_params

    def _validate_config_structure(self, config_data: Dict[str, Any]) -> None:
        """Validate overall configuration structure."""
        if not isinstance(config_data, dict):
            raise ConfigurationError("Configuration must be a JSON object/dictionary")

        valid_sections = [
            "apgi_parameters",
            "experimental_config",
            "retry_config",
            "performance_thresholds",
            "stimulus_parameters",
        ]

        for section in config_data:
            if section not in valid_sections:
                raise ConfigurationError(
                    f"Unknown configuration section: '{section}'. "
                    f"Valid sections are: {', '.join(valid_sections)}"
                )

    def _validate_parameter_section(
        self, section_name: str, section_data: Dict[str, Any]
    ) -> None:
        """Validate a parameter section with detailed error messages."""
        if not isinstance(section_data, dict):
            raise ConfigurationError(
                f"Section '{section_name}' must be a JSON object/dictionary"
            )

        # Import validator for detailed validation
        try:
            from .validation.parameter_validator import get_validator

            validator = get_validator()

            if section_name == "apgi_parameters":
                result = validator.validate_apgi_parameters(**section_data)
            elif section_name == "experimental_config":
                result = validator.validate_experimental_config(**section_data)
            elif section_name == "retry_config":
                result = validator.validate_retry_config(**section_data)
            elif section_name == "performance_thresholds":
                result = validator.validate_performance_thresholds(**section_data)
            elif section_name == "stimulus_parameters":
                result = validator.validate_stimulus_parameters(**section_data)
            else:
                return  # Skip validation for unknown sections

            if not result.is_valid:
                raise ConfigurationError(
                    f"Validation failed for section '{section_name}':\n"
                    f"{result.get_message()}"
                )

        except ImportError:
            # Fallback to basic validation if validator not available
            self._basic_parameter_validation(section_name, section_data)

    def _basic_parameter_validation(
        self, section_name: str, section_data: Dict[str, Any]
    ) -> None:
        """Basic validation when detailed validator is not available."""
        for param_name, param_value in section_data.items():
            # Type validation
            if not isinstance(param_value, (int, float, str, bool)):
                raise ConfigurationError(
                    f"Parameter '{section_name}.{param_name}' must be a number, string, or boolean, "
                    f"but got {type(param_value).__name__}"
                )

            # Range validation for numeric parameters
            if isinstance(param_value, (int, float)):
                if param_value < 0 and "precision" in param_name.lower():
                    raise ConfigurationError(
                        f"Parameter '{section_name}.{param_name}' must be positive, "
                        f"but got {param_value}. Precision values represent inverse variance "
                        f"and cannot be negative."
                    )
                if param_value <= 0 and "threshold" in param_name.lower():
                    raise ConfigurationError(
                        f"Parameter '{section_name}.{param_name}' must be positive, "
                        f"but got {param_value}. Threshold values must be greater than zero."
                    )
                if param_value <= 0 and "gain" in param_name.lower():
                    raise ConfigurationError(
                        f"Parameter '{section_name}.{param_name}' must be positive, "
                        f"but got {param_value}. Gain values must be greater than zero."
                    )
                if "steepness" in param_name.lower() and param_value <= 0:
                    raise ConfigurationError(
                        f"Parameter '{section_name}.{param_name}' must be positive, "
                        f"but got {param_value}. Steepness controls sigmoid slope and must be positive."
                    )

                # Specific range validations
                if section_name == "apgi_parameters":
                    self._validate_apgi_parameter_range(param_name, param_value)
                elif section_name == "experimental_config":
                    self._validate_experimental_parameter_range(param_name, param_value)
                elif section_name == "performance_thresholds":
                    self._validate_performance_parameter_range(param_name, param_value)
                elif section_name == "stimulus_parameters":
                    self._validate_stimulus_parameter_range(param_name, param_value)

    def _validate_apgi_parameter_range(self, param_name: str, value: float) -> None:
        """Validate APGI parameter ranges."""
        if param_name == "extero_precision" and not (0.1 <= value <= 10.0):
            raise ConfigurationError(
                f"Exteroceptive precision must be between 0.1 and 10.0, "
                f"but got {value}. Typical values: 1.0-3.0"
            )
        if param_name == "intero_precision" and not (0.1 <= value <= 10.0):
            raise ConfigurationError(
                f"Interoceptive precision must be between 0.1 and 10.0, "
                f"but got {value}. Typical values: 0.5-2.0"
            )
        if param_name == "threshold" and not (0.5 <= value <= 10.0):
            raise ConfigurationError(
                f"Ignition threshold must be between 0.5 and 10.0, "
                f"but got {value}. Typical values: 2.0-5.0"
            )
        if param_name == "steepness" and not (0.1 <= value <= 10.0):
            raise ConfigurationError(
                f"Sigmoid steepness must be between 0.1 and 10.0, "
                f"but got {value}. Typical values: 1.0-3.0"
            )

    def _validate_experimental_parameter_range(
        self, param_name: str, value: float
    ) -> None:
        """Validate experimental parameter ranges."""
        if param_name == "n_trials" and not (1 <= value <= 100000):
            raise ConfigurationError(
                f"Number of trials must be between 1 and 100,000, "
                f"but got {value}. Recommended: 100-1000 for most experiments"
            )
        if param_name == "n_participants" and not (1 <= value <= 10000):
            raise ConfigurationError(
                f"Number of participants must be between 1 and 10,000, "
                f"but got {value}. Recommended: 10-500 for most studies"
            )
        if param_name == "alpha_level" and not (0.001 <= value <= 0.5):
            raise ConfigurationError(
                f"Alpha level must be between 0.001 and 0.5, "
                f"but got {value}. Common values: 0.05, 0.01, 0.001"
            )

    def _validate_performance_parameter_range(
        self, param_name: str, value: float
    ) -> None:
        """Validate performance threshold parameter ranges."""
        if param_name == "min_rt" and not (0.05 <= value <= 5.0):
            raise ConfigurationError(
                f"Minimum response time must be between 0.05 and 5.0 seconds, "
                f"but got {value}. Typical: 0.1-0.3s"
            )
        if param_name == "max_rt" and not (0.5 <= value <= 30.0):
            raise ConfigurationError(
                f"Maximum response time must be between 0.5 and 30.0 seconds, "
                f"but got {value}. Typical: 2.0-10.0s"
            )
        if param_name == "min_accuracy" and not (0.0 <= value <= 1.0):
            raise ConfigurationError(
                f"Minimum accuracy must be between 0.0 and 1.0, "
                f"but got {value}. Typical: 0.5-0.8"
            )

    def _validate_stimulus_parameter_range(self, param_name: str, value: float) -> None:
        """Validate stimulus parameter ranges."""
        if param_name == "lapse_rate" and not (0.0 <= value <= 0.5):
            raise ConfigurationError(
                f"Lapse rate must be between 0.0 and 0.5, "
                f"but got {value}. Typical: 0.01-0.05"
            )
        if param_name == "guess_rate" and not (0.0 <= value <= 1.0):
            raise ConfigurationError(
                f"Guess rate must be between 0.0 and 1.0, "
                f"but got {value}. Typical: 0.5 for 2AFC"
            )

    def get_falsification_thresholds(self) -> ExperimentalConfig:
        """Get falsification thresholds from experimental config."""
        return self.experimental_config

    def update_apgi_parameters(self, **kwargs) -> None:
        """Update APGI parameters.

        Args:
            **kwargs: Parameter names and values to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.apgi_params, key):
                setattr(self.apgi_params, key, value)
            else:
                raise ConfigurationError(f"Unknown APGI parameter: {key}")

        # Re-validate parameters
        self.apgi_params.__post_init__()

    def update_experimental_config(self, **kwargs) -> None:
        """Update experimental configuration.

        Args:
            **kwargs: Configuration names and values to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.experimental_config, key):
                setattr(self.experimental_config, key, value)
            else:
                raise ConfigurationError(f"Unknown experimental parameter: {key}")

        # Re-validate configuration
        self.experimental_config.__post_init__()

    def validate(self) -> bool:
        """Validate all configuration objects.

        Returns:
            True if all configurations are valid, False otherwise.

        Raises:
            ConfigurationError: If any configuration is invalid.
        """
        try:
            # Validate APGI parameters
            self.apgi_params.__post_init__()

            # Validate experimental configuration
            self.experimental_config.__post_init__()

            # Additional validation could be added here

            return True

        except ConfigurationError as e:
            raise e
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")

    def get_validation_report(self) -> Dict[str, Any]:
        """Get a detailed validation report.

        Returns:
            Dictionary containing validation status and details.
        """
        report = {"valid": True, "errors": [], "warnings": [], "details": {}}

        try:
            # Validate APGI parameters
            self.apgi_params.__post_init__()
            report["details"]["apgi_parameters"] = "Valid"
        except ConfigurationError as e:
            report["valid"] = False
            report["errors"].append(f"APGI Parameters: {e}")
            report["details"]["apgi_parameters"] = str(e)

        try:
            # Validate experimental configuration
            self.experimental_config.__post_init__()
            report["details"]["experimental_config"] = "Valid"
        except ConfigurationError as e:
            report["valid"] = False
            report["errors"].append(f"Experimental Config: {e}")
            report["details"]["experimental_config"] = str(e)

        return report

    def validate_apgi_parameter(self, param_name: str, value: float) -> bool:
        """Validate a single APGI parameter.

        Args:
            param_name: Name of parameter to validate
            value: Value to validate

        Returns:
            True if parameter is valid, False otherwise
        """
        try:
            # Import here to avoid circular dependency
            from .validation.parameter_validator import get_validator

            validator = get_validator()

            # Create a temporary parameters object with the test value
            temp_params = APGIParameters()
            setattr(temp_params, param_name, value)

            # Validate will raise an exception if invalid
            temp_params.__post_init__()
            return True

        except ImportError:
            # Fallback to basic validation if validator not available
            if param_name in [
                "extero_precision",
                "intero_precision",
                "somatic_gain",
                "steepness",
            ]:
                return value > 0
            elif param_name == "threshold":
                return 0 < value <= 10
            return True
        except Exception:
            return False


# Global configuration instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def initialize_config(config_path: Optional[str] = None) -> ConfigManager:
    """Initialize global configuration manager.

    Args:
        config_path: Path to configuration file.

    Returns:
        Initialized configuration manager.
    """
    global _config_manager
    _config_manager = ConfigManager(config_path)
    return _config_manager
