"""
APGI Framework Testing Module

This module implements the primary falsification testing framework for the APGI
(Interoceptive Predictive Integration) Framework, including consciousness assessment,
neural signature validation, and experimental control mechanisms.
"""

import logging
from datetime import datetime
from typing import Type, Union

try:
    from .primary_falsification import (
        PrimaryFalsificationTest as ImportedPrimaryFalsificationTest,
        FalsificationResult as ImportedFalsificationResult,
    )

    # Use imported classes
    PrimaryFalsificationTest: Union[
        "_PrimaryFalsificationTest", ImportedPrimaryFalsificationTest
    ] = ImportedPrimaryFalsificationTest
    FalsificationResult: Union[
        "_FalsificationResult", ImportedFalsificationResult
    ] = ImportedFalsificationResult
except ImportError:
    # Fallback to a basic implementation if specialized test implementation is missing
    class _PrimaryFalsificationTest:
        """Stub for PrimaryFalsificationTest providing basic interface."""

        def run_falsification_test(self, n_trials=100, n_participants=20):
            return {"framework_falsified": False, "status": "staged"}

        def run_test(self, **kwargs):
            return {"framework_falsified": False, "status": "staged"}

    class _FalsificationResult:
        """Fallback result object."""

        def __init__(self, **kwargs):
            self.is_falsified = kwargs.get(
                "falsified", kwargs.get("framework_falsified", False)
            )
            self.framework_falsified = kwargs.get("framework_falsified", False)
            self.confidence_level = kwargs.get("confidence_level", 0.5)
            self.p_value = kwargs.get("p_value", 0.5)
            self.effect_size = kwargs.get("effect_size", 0.0)
            self.statistical_power = kwargs.get("statistical_power", 0.0)

            # Set additional attributes
            for key, value in kwargs.items():
                if key not in ["falsified", "framework_falsified"]:
                    setattr(self, key, value)

    # Use fallback classes


# Consciousness assessment classes - implemented inline below
class ConsciousnessAssessment:
    """Basic consciousness assessment functionality."""

    def __init__(
        self,
        subjective_report: bool = False,
        forced_choice_accuracy: float = 0.5,
        confidence_rating: float = 0.5,
        response_time: float = 1.0,
        metacognitive_sensitivity: float = 0.5,
    ):
        self.subjective_report = subjective_report
        self.forced_choice_accuracy = forced_choice_accuracy
        self.confidence_rating = confidence_rating
        self.response_time = response_time
        self.metacognitive_sensitivity = metacognitive_sensitivity
        self.timestamp = datetime.now()


class ConsciousnessAssessmentSimulator:
    """Simulator for consciousness assessment."""

    def simulate_assessment(
        self, consciousness_present: bool = True
    ) -> ConsciousnessAssessment:
        """Simulate a consciousness assessment."""
        import numpy as np

        if consciousness_present:
            subjective = np.random.choice([True, False], p=[0.8, 0.2])
            accuracy = np.random.normal(0.75, 0.1)
            confidence = np.random.normal(0.7, 0.15)
        else:
            subjective = np.random.choice([True, False], p=[0.2, 0.8])
            accuracy = np.random.normal(0.5, 0.05)
            confidence = np.random.normal(0.3, 0.1)

        accuracy = np.clip(accuracy, 0.0, 1.0)
        confidence = np.clip(confidence, 0.0, 1.0)
        response_time = np.random.exponential(1.0)

        return ConsciousnessAssessment(subjective, accuracy, confidence, response_time)


class ConsciousnessValidator:
    """Validator for consciousness measures."""

    def validate_assessment(self, assessment: ConsciousnessAssessment) -> bool:
        """Validate a consciousness assessment."""
        return (
            0.0 <= assessment.forced_choice_accuracy <= 1.0
            and 0.0 <= assessment.confidence_rating <= 1.0
            and assessment.response_time > 0.0
        )


from .ai_acc_validation import AIACCValidator
from .edge_case_interpreter import EdgeCaseInterpreter, EdgeCaseType, FrameworkBoundary
from .experimental_control import ExperimentalControlValidator
from .result_interpretation import FalsificationInterpreter, ResultLogger


# Additional falsification test classes
class ConsciousnessWithoutIgnitionTest:
    """
    Tests whether consciousness can occur without full neural ignition signatures.

    This falsification test examines the converse of the primary test: whether
    subjective reports of consciousness can occur in the absence of the complete
    set of neural signatures (P3b, gamma synchrony, BOLD activation, PCI).
    """

    def __init__(self):
        """Initialize the test with default parameters."""
        self.logger = logging.getLogger(__name__)
        self.signature_thresholds = {
            "p3b_amplitude": 5.0,  # μV
            "gamma_plv": 0.3,  # Phase locking value
            "bold_activation": 0.1,  # Percent signal change
            "pci_value": 0.3,  # Perturbational complexity index
        }
        self.consciousness_thresholds = {
            "subjective_report": True,
            "forced_choice_accuracy": 0.6,  # Above chance
            "confidence_rating": 0.5,
        }

    def run_test(self, n_trials: int = 100, noise_level: float = 0.1) -> dict:
        """
        Run the consciousness without ignition test.

        Args:
            n_trials: Number of experimental trials to simulate
            noise_level: Level of neural noise to add (0.0-1.0)

        Returns:
            Dictionary containing test results and statistics
        """
        from datetime import datetime

        import numpy as np

        # Simulate trials
        consciousness_without_ignition = 0
        ignition_without_consciousness = 0
        both_present = 0
        both_absent = 0

        trial_results = []

        for trial in range(n_trials):
            # Simulate neural signatures with noise
            p3b_present = np.random.random() > (0.3 + noise_level)
            gamma_present = np.random.random() > (0.3 + noise_level)
            bold_present = np.random.random() > (0.3 + noise_level)
            pci_present = np.random.random() > (0.3 + noise_level)

            # Full ignition requires all signatures
            full_ignition = (
                p3b_present and gamma_present and bold_present and pci_present
            )

            # Simulate consciousness measures
            subjective_conscious = np.random.random() > (0.4 - noise_level * 0.5)
            forced_choice_acc = (
                np.random.beta(8, 4) if subjective_conscious else np.random.beta(4, 8)
            )
            confidence = forced_choice_acc + np.random.normal(0, 0.1)
            confidence = np.clip(confidence, 0, 1)

            full_consciousness = (
                subjective_conscious
                and forced_choice_acc
                > self.consciousness_thresholds["forced_choice_accuracy"]
                and confidence > self.consciousness_thresholds["confidence_rating"]
            )

            # Categorize trial
            if full_consciousness and not full_ignition:
                consciousness_without_ignition += 1
                category = "consciousness_without_ignition"
            elif full_ignition and not full_consciousness:
                ignition_without_consciousness += 1
                category = "ignition_without_consciousness"
            elif full_consciousness and full_ignition:
                both_present += 1
                category = "both_present"
            else:
                both_absent += 1
                category = "both_absent"

            trial_results.append(
                {
                    "trial_id": trial,
                    "category": category,
                    "full_ignition": full_ignition,
                    "full_consciousness": full_consciousness,
                    "p3b_present": p3b_present,
                    "gamma_present": gamma_present,
                    "bold_present": bold_present,
                    "pci_present": pci_present,
                    "subjective_conscious": subjective_conscious,
                    "forced_choice_acc": forced_choice_acc,
                    "confidence": confidence,
                }
            )

        # Calculate statistics
        consciousness_without_ignition_rate = consciousness_without_ignition / n_trials
        ignition_without_consciousness_rate = ignition_without_consciousness / n_trials

        # Statistical test
        from scipy import stats

        contingency_table = [
            [
                consciousness_without_ignition,
                both_present - consciousness_without_ignition,
            ],
            [both_absent, ignition_without_consciousness],
        ]

        chi2_stat = None
        p_value = None
        try:
            chi2_stat, p_value, _, _ = stats.chi2_contingency(contingency_table)
        except (ValueError, RuntimeError) as e:
            self.logger.warning(
                f"Chi-square test failed: {e}. Using conservative fallback p-value."
            )
            p_value = (
                0.5  # Conservative fallback that won't falsely indicate significance
            )

        # Determine if framework is falsified
        falsified = consciousness_without_ignition_rate > 0.1 and p_value < 0.05

        return {
            "status": "completed",
            "test_name": "ConsciousnessWithoutIgnitionTest",
            "timestamp": datetime.now().isoformat(),
            "n_trials": n_trials,
            "results": {
                "consciousness_without_ignition_count": consciousness_without_ignition,
                "consciousness_without_ignition_rate": consciousness_without_ignition_rate,
                "ignition_without_consciousness_count": ignition_without_consciousness,
                "ignition_without_consciousness_rate": ignition_without_consciousness_rate,
                "both_present_count": both_present,
                "both_absent_count": both_absent,
            },
            "statistical_test": {"chi2_statistic": chi2_stat, "p_value": p_value},
            "framework_falsified": falsified,
            "interpretation": self._interpret_results(
                consciousness_without_ignition_rate, p_value
            ),
            "trial_data": trial_results,
        }

    def _interpret_results(self, rate: float, p_value: float) -> str:
        """Interpret the test results."""
        if rate > 0.2 and p_value < 0.01:
            return "Strong evidence that consciousness can occur without full ignition - framework falsified"
        elif rate > 0.1 and p_value < 0.05:
            return "Moderate evidence that consciousness can occur without full ignition - framework challenged"
        elif rate > 0.05:
            return "Weak evidence that consciousness can occur without full ignition - framework partially supported"
        else:
            return "No evidence that consciousness occurs without full ignition - framework supported"


class ThresholdInsensitivityTest:
    """
    Tests whether the framework is insensitive to reasonable threshold variations.

    This falsification test examines whether small changes in the thresholds
    for neural signatures and consciousness measures lead to dramatically different
    conclusions about framework validity.
    """

    def __init__(self):
        """Initialize the test with default parameters."""
        self.logger = logging.getLogger(__name__)
        self.base_thresholds = {
            "p3b_amplitude": 5.0,
            "gamma_plv": 0.3,
            "bold_activation": 0.1,
            "pci_value": 0.3,
            "forced_choice_accuracy": 0.6,
            "confidence_rating": 0.5,
        }

    def run_test(self, n_trials: int = 100, threshold_variations: float = 0.2) -> dict:
        """
        Run the threshold insensitivity test.

        Args:
            n_trials: Number of trials per threshold configuration
            threshold_variations: Fraction to vary thresholds (e.g., 0.2 = ±20%)

        Returns:
            Dictionary containing test results and sensitivity analysis
        """
        from datetime import datetime

        import numpy as np

        # Test different threshold configurations
        threshold_configs = []
        results_by_config = []

        # Base configuration
        threshold_configs.append(
            {"name": "baseline", "thresholds": self.base_thresholds.copy()}
        )

        # Lower thresholds
        lower_thresholds = {}
        for key, value in self.base_thresholds.items():
            lower_thresholds[key] = value * (1 - threshold_variations)
        threshold_configs.append({"name": "lower", "thresholds": lower_thresholds})

        # Higher thresholds
        higher_thresholds = {}
        for key, value in self.base_thresholds.items():
            higher_thresholds[key] = value * (1 + threshold_variations)
        threshold_configs.append({"name": "higher", "thresholds": higher_thresholds})

        # Run simulation for each configuration
        for config in threshold_configs:
            config_results = self._run_configuration_simulation(
                n_trials, config["thresholds"]
            )
            results_by_config.append(
                {
                    "config_name": config["name"],
                    "thresholds": config["thresholds"],
                    "results": config_results,
                }
            )

        # Analyze sensitivity
        falsification_rates = [
            r["results"]["falsification_rate"] for r in results_by_config
        ]
        sensitivity = np.std(falsification_rates) / (
            np.mean(falsification_rates) + 1e-8
        )

        # Determine if framework is falsified (too sensitive)
        falsified = sensitivity > 0.5  # High sensitivity indicates threshold dependence

        return {
            "status": "completed",
            "test_name": "ThresholdInsensitivityTest",
            "timestamp": datetime.now().isoformat(),
            "n_trials_per_config": n_trials,
            "threshold_variations": threshold_variations,
            "configurations": results_by_config,
            "sensitivity_analysis": {
                "falsification_rates": falsification_rates,
                "mean_rate": np.mean(falsification_rates),
                "std_rate": np.std(falsification_rates),
                "sensitivity_coefficient": sensitivity,
            },
            "framework_falsified": falsified,
            "interpretation": self._interpret_sensitivity(sensitivity),
        }

    def _run_configuration_simulation(self, n_trials: int, thresholds: dict) -> dict:
        """Run simulation for a specific threshold configuration."""
        import numpy as np

        falsifying_trials = 0

        for trial in range(n_trials):
            # Simulate neural data
            p3b_amp = np.random.normal(6, 2)  # μV
            gamma_plv = np.random.beta(3, 7)  # Phase locking value
            bold_act = np.random.normal(0.12, 0.05)  # Percent signal change
            pci_val = np.random.normal(0.35, 0.1)  # PCI value

            # Check if signatures meet thresholds
            signatures_met = (
                p3b_amp > thresholds["p3b_amplitude"]
                and gamma_plv > thresholds["gamma_plv"]
                and bold_act > thresholds["bold_activation"]
                and pci_val > thresholds["pci_value"]
            )

            # Simulate consciousness measures
            forced_choice_acc = (
                np.random.beta(8, 4) if signatures_met else np.random.beta(4, 8)
            )
            confidence = forced_choice_acc + np.random.normal(0, 0.1)
            confidence = np.clip(confidence, 0, 1)

            consciousness_met = (
                forced_choice_acc > thresholds["forced_choice_accuracy"]
                and confidence > thresholds["confidence_rating"]
            )

            # Check for falsification (signatures without consciousness)
            if signatures_met and not consciousness_met:
                falsifying_trials += 1

        return {
            "falsifying_trials": falsifying_trials,
            "falsification_rate": falsifying_trials / n_trials,
        }

    def _interpret_sensitivity(self, sensitivity: float) -> str:
        """Interpret the sensitivity results."""
        if sensitivity > 1.0:
            return "Extremely high threshold sensitivity - framework falsified"
        elif sensitivity > 0.5:
            return "High threshold sensitivity - framework unreliable"
        elif sensitivity > 0.2:
            return "Moderate threshold sensitivity - framework questionable"
        elif sensitivity > 0.1:
            return "Low threshold sensitivity - framework reasonably robust"
        else:
            return "Very low threshold sensitivity - framework highly robust"


class SomaBiasTest:
    """
    Tests whether somatic (interoceptive) biases systematically affect framework predictions.

    This falsification test examines whether the framework's predictions are
    systematically distorted by somatic/interoceptive influences, which would
    indicate a bias in the model.
    """

    def __init__(self):
        """Initialize the test with default parameters."""
        self.logger = logging.getLogger(__name__)
        self.soma_bias_levels = [-0.5, -0.2, 0.0, 0.2, 0.5]  # Negative to positive bias
        self.neutral_baseline = 0.0

    def run_test(self, n_trials: int = 100, bias_strength: float = 0.3) -> dict:
        """
        Run the soma bias test.

        Args:
            n_trials: Number of trials per bias level
            bias_strength: Maximum strength of somatic bias to apply

        Returns:
            Dictionary containing test results and bias analysis
        """
        from datetime import datetime

        import numpy as np
        from scipy import stats

        results_by_bias = []

        for bias_level in self.soma_bias_levels:
            bias_results = self._run_bias_simulation(
                n_trials, bias_level, bias_strength
            )
            results_by_bias.append({"bias_level": bias_level, "results": bias_results})

        # Analyze bias effects
        falsification_rates = [
            r["results"]["falsification_rate"] for r in results_by_bias
        ]
        bias_levels = [r["bias_level"] for r in results_by_bias]

        # Test for systematic bias (correlation between bias level and falsification rate)
        correlation, p_value = stats.pearsonr(bias_levels, falsification_rates)

        # Test for bias asymmetry (different effects for positive vs negative bias)
        positive_bias_rates = [
            r["results"]["falsification_rate"]
            for r in results_by_bias
            if r["bias_level"] > 0
        ]
        negative_bias_rates = [
            r["results"]["falsification_rate"]
            for r in results_by_bias
            if r["bias_level"] < 0
        ]

        asymmetry_test = None
        asymmetry_p = None
        if positive_bias_rates and negative_bias_rates:
            asymmetry_test, asymmetry_p = stats.ttest_ind(
                positive_bias_rates, negative_bias_rates
            )

        # Determine if framework is falsified
        falsified = (abs(correlation) > 0.7 and p_value < 0.05) or (
            asymmetry_p and asymmetry_p < 0.05
        )

        return {
            "status": "completed",
            "test_name": "SomaBiasTest",
            "timestamp": datetime.now().isoformat(),
            "n_trials_per_bias": n_trials,
            "bias_strength": bias_strength,
            "bias_levels_tested": self.soma_bias_levels,
            "results_by_bias": results_by_bias,
            "bias_analysis": {
                "correlation_coefficient": correlation,
                "correlation_p_value": p_value,
                "asymmetry_t_stat": asymmetry_test,
                "asymmetry_p_value": asymmetry_p,
                "positive_bias_mean": (
                    np.mean(positive_bias_rates) if positive_bias_rates else None
                ),
                "negative_bias_mean": (
                    np.mean(negative_bias_rates) if negative_bias_rates else None
                ),
            },
            "framework_falsified": falsified,
            "interpretation": self._interpret_bias(
                correlation, p_value, asymmetry_p or 0.0
            ),
        }

    def _run_bias_simulation(
        self, n_trials: int, bias_level: float, bias_strength: float
    ) -> dict:
        """Run simulation for a specific bias level."""
        import numpy as np

        falsifying_trials = 0

        for trial in range(n_trials):
            # Apply somatic bias to neural signature generation
            bias_effect = bias_level * bias_strength

            # Simulate neural signatures with bias
            p3b_amp = np.random.normal(6 + bias_effect * 2, 2)  # Bias affects P3b
            gamma_plv = np.random.beta(
                3 + bias_effect * 2, 7 - bias_effect
            )  # Bias affects gamma
            bold_act = np.random.normal(
                0.12 + bias_effect * 0.05, 0.05
            )  # Bias affects BOLD
            pci_val = np.random.normal(
                0.35 + bias_effect * 0.1, 0.1
            )  # Bias affects PCI

            # Standard thresholds
            signatures_met = (
                p3b_amp > 5.0 and gamma_plv > 0.3 and bold_act > 0.1 and pci_val > 0.3
            )

            # Simulate consciousness (also affected by bias through interoceptive awareness)
            bias_consciousness_effect = bias_level * bias_strength * 0.3
            forced_choice_acc = np.random.beta(
                8 + bias_consciousness_effect * 4, 4 - bias_consciousness_effect * 2
            )
            confidence = forced_choice_acc + np.random.normal(0, 0.1)
            confidence = np.clip(confidence, 0, 1)

            consciousness_met = forced_choice_acc > 0.6 and confidence > 0.5

            # Check for falsification
            if signatures_met and not consciousness_met:
                falsifying_trials += 1

        return {
            "falsifying_trials": falsifying_trials,
            "falsification_rate": falsifying_trials / n_trials,
        }

    def _interpret_bias(
        self, correlation: float, corr_p: float, asymmetry_p: float
    ) -> str:
        """Interpret the bias test results."""
        if abs(correlation) > 0.8 and corr_p < 0.01:
            return f"Strong systematic bias detected (r={correlation:.3f}) - framework falsified"
        elif abs(correlation) > 0.6 and corr_p < 0.05:
            return f"Moderate systematic bias detected (r={correlation:.3f}) - framework challenged"
        elif asymmetry_p and asymmetry_p < 0.05:
            return "Significant bias asymmetry detected - framework questionable"
        elif abs(correlation) > 0.3:
            return f"Weak bias effects detected (r={correlation:.3f}) - framework partially supported"
        else:
            return "No significant bias effects detected - framework supported"


__all__ = [
    "ConsciousnessAssessment",
    "ConsciousnessAssessmentSimulator",
    "ConsciousnessValidator",
    "AIACCValidator",
    "ExperimentalControlValidator",
    "FalsificationInterpreter",
    "ResultLogger",
    "EdgeCaseInterpreter",
    "EdgeCaseType",
    "FrameworkBoundary",
    "ConsciousnessWithoutIgnitionTest",
    "ThresholdInsensitivityTest",
    "SomaBiasTest",
]

# Conditionally add PrimaryFalsificationTest if available
if PrimaryFalsificationTest is not None:
    __all__.append("PrimaryFalsificationTest")


# Mock classes for testing
class FalsificationEngine:
    """Mock falsification engine for testing purposes."""

    def __init__(self):
        self.test_results = {}

    def run_falsification_test(self, test_name, parameters):
        """Run a falsification test."""
        result_id = f"test_{hash(str(parameters)) % 10000:04d}"
        result = {
            "result_id": result_id,
            "test_name": test_name,
            "framework_falsified": False,
            "confidence_level": 0.95,
            "p_value": 0.03,
            "parameters": parameters,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        self.test_results[result_id] = result
        return result

    def get_result(self, result_id):
        """Get test result by ID."""
        return self.test_results.get(result_id)


if "FalsificationEngine" not in __all__:
    __all__.append("FalsificationEngine")
