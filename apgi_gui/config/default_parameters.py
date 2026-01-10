"""Default parameters configuration for APGI Framework GUI."""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ParameterConfig:
    """Configuration for a single parameter."""

    label: str
    key: str
    default_value: str
    description: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    parameter_type: str = "float"  # "float", "int", "string"


class DefaultParameters:
    """Default parameters and settings for the APGI Framework."""

    # APGI Model Parameters
    APGI_PARAMETERS: List[ParameterConfig] = [
        ParameterConfig(
            label="Learning Rate",
            key="learning_rate",
            default_value="0.01",
            description="Controls the rate of learning in the model",
            min_value=0.0001,
            max_value=1.0,
            parameter_type="float",
        ),
        ParameterConfig(
            label="Precision Weight",
            key="precision_weight",
            default_value="1.0",
            description="Weight for precision in belief updating",
            min_value=0.1,
            max_value=10.0,
            parameter_type="float",
        ),
        ParameterConfig(
            label="Prediction Error Threshold",
            key="prediction_error_threshold",
            default_value="0.5",
            description="Threshold for prediction error detection",
            min_value=0.01,
            max_value=2.0,
            parameter_type="float",
        ),
        ParameterConfig(
            label="Interoceptive Gain",
            key="interoceptive_gain",
            default_value="1.0",
            description="Gain factor for interoceptive signals",
            min_value=0.1,
            max_value=5.0,
            parameter_type="float",
        ),
        ParameterConfig(
            label="Somatic Bias",
            key="somatic_bias",
            default_value="0.0",
            description="Baseline bias for somatic signals",
            min_value=-2.0,
            max_value=2.0,
            parameter_type="float",
        ),
        ParameterConfig(
            label="Ignition Threshold",
            key="ignition_threshold",
            default_value="2.0",
            description="Threshold for neural ignition",
            min_value=0.5,
            max_value=5.0,
            parameter_type="float",
        ),
    ]

    # Neural Signature Options
    NEURAL_SIGNATURES: List[Tuple[str, str, str]] = [
        ("P3b Component", "p3b", "P3b ERP component for conscious access"),
        ("Gamma Oscillations", "gamma", "Gamma-band neural synchrony"),
        ("Microstate Dynamics", "microstate", "Brain microstate transitions"),
        ("Pupillometry", "pupil", "Pupil diameter measurements"),
    ]

    # Experimental Settings
    EXPERIMENTAL_SETTINGS: List[ParameterConfig] = [
        ParameterConfig(
            label="Sample Rate (Hz)",
            key="sample_rate",
            default_value="1000",
            description="Sampling rate for data acquisition",
            min_value=125,
            max_value=2000,
            parameter_type="int",
        ),
        ParameterConfig(
            label="Epoch Duration (s)",
            key="epoch_duration",
            default_value="2.0",
            description="Duration of analysis epochs",
            min_value=0.1,
            max_value=10.0,
            parameter_type="float",
        ),
        ParameterConfig(
            label="Number of Trials",
            key="num_trials",
            default_value="100",
            description="Number of experimental trials",
            min_value=10,
            max_value=1000,
            parameter_type="int",
        ),
        ParameterConfig(
            label="Baseline Duration (s)",
            key="baseline_duration",
            default_value="0.5",
            description="Duration of baseline period",
            min_value=0.1,
            max_value=2.0,
            parameter_type="float",
        ),
    ]

    # UI Configuration
    UI_CONFIG = {
        "font_sizes": {"title": 18, "header": 16, "label": 12, "button": 12},
        "spacing": {
            "padding_x": 10,
            "padding_y": 5,
            "padding_large_y": 10,
            "padding_section_y": 20,
        },
        "button_height": 40,
        "frame_corner_radius": 8,
    }

    # Validation Rules
    VALIDATION_RULES = {
        "learning_rate": {"min": 0.0001, "max": 1.0, "type": "float"},
        "precision_weight": {"min": 0.1, "max": 10.0, "type": "float"},
        "prediction_error_threshold": {"min": 0.01, "max": 2.0, "type": "float"},
        "interoceptive_gain": {"min": 0.1, "max": 5.0, "type": "float"},
        "somatic_bias": {"min": -2.0, "max": 2.0, "type": "float"},
        "ignition_threshold": {"min": 0.5, "max": 5.0, "type": "float"},
        "sample_rate": {"min": 125, "max": 2000, "type": "int"},
        "epoch_duration": {"min": 0.1, "max": 10.0, "type": "float"},
        "num_trials": {"min": 10, "max": 1000, "type": "int"},
        "baseline_duration": {"min": 0.1, "max": 2.0, "type": "float"},
    }

    @classmethod
    def get_parameter_defaults(cls) -> Dict[str, str]:
        """Get all parameter defaults as a dictionary."""
        defaults = {}

        for param in cls.APGI_PARAMETERS:
            defaults[param.key] = param.default_value

        for setting in cls.EXPERIMENTAL_SETTINGS:
            defaults[setting.key] = setting.default_value

        return defaults

    @classmethod
    def validate_parameter(cls, key: str, value: str) -> Tuple[bool, str]:
        """Validate a parameter value.

        Args:
            key: Parameter key
            value: Parameter value as string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if key not in cls.VALIDATION_RULES:
            return True, ""

        rules = cls.VALIDATION_RULES[key]

        try:
            if rules["type"] == "float":
                float_value = float(value)
                min_val = rules["min"]
                max_val = rules["max"]

                if float_value < min_val or float_value > max_val:
                    return False, f"Value must be between {min_val} and {max_val}"

            elif rules["type"] == "int":
                int_value = int(value)
                min_val = rules["min"]
                max_val = rules["max"]

                if int_value < min_val or int_value > max_val:
                    return False, f"Value must be between {min_val} and {max_val}"

        except ValueError:
            return False, f"Invalid {rules['type']} value"

        return True, ""

    @classmethod
    def get_parameter_info(cls, key: str) -> Optional[ParameterConfig]:
        """Get parameter configuration by key.

        Args:
            key: Parameter key

        Returns:
            ParameterConfig or None if not found
        """
        for param in cls.APGI_PARAMETERS:
            if param.key == key:
                return param

        for setting in cls.EXPERIMENTAL_SETTINGS:
            if setting.key == key:
                return setting

        return None
