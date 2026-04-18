"""
Example 4: Extending with New Falsification Criteria

This example demonstrates how to extend the APGI Framework with custom
falsification criteria and tests. This is useful for:
- Testing novel predictions of the framework
- Implementing domain-specific falsification tests
- Exploring edge cases and boundary conditions
- Developing new experimental paradigms

This example shows the architecture and patterns for creating new tests.

NOTE: These experiments use mock/simulated data for demonstration purposes.
Random seeds are used to ensure reproducible but varied results across experiments.
For actual scientific experiments, real empirical data would be required.
"""

import hashlib  # noqa: F401 - used in wrapper functions for seed generation
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

from apgi_framework.simulators import (
    GammaSimulator,
    P3bSimulator,
)

# Setup logging with standardized system
try:
    from apgi_framework.logging.standardized_logging import get_logger

    logger = get_logger("extending_falsification_example")
except ImportError:
    # Fallback to basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)  # type: ignore


@dataclass
class CustomFalsificationResult:
    """Custom result structure for extended falsification tests."""

    test_name: str
    is_falsified: bool
    confidence_level: float
    effect_size: float
    p_value: float
    statistical_power: float
    detailed_metrics: Dict[str, Any]
    interpretation: str


@dataclass
class ConsciousnessAssessment:
    """Mock consciousness assessment for metacognitive calibration test."""

    confidence_rating: float
    forced_choice_accuracy: float


class ConsciousnessAssessmentSimulator:
    """Mock simulator for consciousness assessment in metacognitive calibration test."""

    def __init__(self, random_seed: Optional[int] = None):
        """Initialize the mock simulator."""
        self.rng = np.random.RandomState(random_seed)

    def simulate_conscious_trial(self) -> ConsciousnessAssessment:
        """Simulate a consciousness assessment trial."""
        confidence = self.rng.uniform(0.3, 0.9)
        # For conscious trials, accuracy should correlate with confidence
        accuracy = confidence + self.rng.normal(0, 0.15)
        accuracy = np.clip(accuracy, 0.0, 1.0)
        return ConsciousnessAssessment(
            confidence_rating=confidence, forced_choice_accuracy=accuracy
        )


class TemporalDynamicsFalsificationTest:
    """
    Example 4A: Custom test for temporal dynamics of ignition.

    This test examines whether ignition can occur with incorrect temporal
    dynamics (e.g., P3b before stimulus, gamma synchrony too brief).
    """

    def __init__(self, random_seed: Optional[int] = None):
        """Initialize the temporal dynamics test."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.random_seed = random_seed
        self.rng = np.random.RandomState(random_seed)
        self.p3b_simulator = P3bSimulator(random_seed=random_seed)
        self.gamma_simulator = GammaSimulator(random_seed=random_seed)

    def run_test(self, n_trials: int = 1000) -> CustomFalsificationResult:
        """
        Run temporal dynamics falsification test.

        Args:
            n_trials: Number of trials to simulate

        Returns:
            CustomFalsificationResult with test outcomes
        """
        self.logger.info(f"Running temporal dynamics test with {n_trials} trials")

        # Track violations
        temporal_violations = 0
        p3b_timing_violations = []
        gamma_duration_violations = []

        for trial in range(n_trials):
            # Generate neural signatures
            p3b_sig = self.p3b_simulator.generate_conscious_signature()
            gamma_sig = self.gamma_simulator.generate_conscious_signature()

            # Check temporal constraints
            # P3b should occur 250-500ms post-stimulus
            if p3b_sig.latency < 250 or p3b_sig.latency > 500:
                p3b_timing_violations.append(p3b_sig.latency)

            # Gamma synchrony should be sustained >200ms
            if gamma_sig.duration < 200:
                gamma_duration_violations.append(gamma_sig.duration)

            # Count as violation if either constraint is violated
            if (
                p3b_sig.latency < 250
                or p3b_sig.latency > 500
                or gamma_sig.duration < 200
            ):
                temporal_violations += 1

        # Calculate statistics
        violation_rate = temporal_violations / n_trials

        # Test is falsified if >5% of trials show temporal violations
        # with full ignition signatures
        is_falsified = violation_rate > 0.05
        confidence = violation_rate if is_falsified else (1 - violation_rate)

        # Calculate effect size (Cohen's h for proportions)
        expected_rate = 0.05
        effect_size = 2 * (
            np.arcsin(np.sqrt(violation_rate)) - np.arcsin(np.sqrt(expected_rate))
        )

        # Simple binomial test p-value
        from scipy import stats

        p_value = stats.binomtest(
            temporal_violations, n_trials, expected_rate, alternative="greater"
        ).pvalue

        # Statistical power (simplified)
        statistical_power = 0.8 if n_trials >= 1000 else 0.6

        # Interpretation
        if is_falsified:
            interpretation = (
                f"FALSIFIED: {violation_rate:.1%} of trials showed temporal violations. "
                f"Ignition signatures occurred with incorrect timing, suggesting the "
                f"framework's temporal predictions are not supported."
            )
        else:
            interpretation = (
                f"NOT FALSIFIED: Only {violation_rate:.1%} of trials showed temporal "
                f"violations, within expected range. Temporal dynamics are consistent "
                f"with framework predictions."
            )

        result = CustomFalsificationResult(
            test_name="Temporal Dynamics Falsification Test",
            is_falsified=is_falsified,
            confidence_level=confidence,
            effect_size=effect_size,
            p_value=p_value,
            statistical_power=statistical_power,
            detailed_metrics={
                "total_trials": n_trials,
                "temporal_violations": temporal_violations,
                "violation_rate": violation_rate,
                "p3b_timing_violations": len(p3b_timing_violations),
                "gamma_duration_violations": len(gamma_duration_violations),
                "mean_p3b_latency": (
                    np.mean(p3b_timing_violations) if p3b_timing_violations else None
                ),
                "mean_gamma_duration": (
                    np.mean(gamma_duration_violations)
                    if gamma_duration_violations
                    else None
                ),
            },
            interpretation=interpretation,
        )

        self.logger.info(f"Test completed: {interpretation}")
        return result


class CrossModalIntegrationTest:
    """
    Example 4B: Custom test for cross-modal integration requirements.

    This test examines whether ignition requires integration across
    sensory modalities or can occur with isolated modality processing.
    """

    def __init__(self, random_seed: Optional[int] = None):
        """Initialize the cross-modal integration test."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.random_seed = random_seed
        self.rng = np.random.RandomState(random_seed)
        self.bold_simulator = GammaSimulator(random_seed=random_seed)

    def run_test(self, n_trials: int = 1000) -> CustomFalsificationResult:
        """
        Run cross-modal integration falsification test.

        Args:
            n_trials: Number of trials to simulate

        Returns:
            CustomFalsificationResult with test outcomes
        """
        self.logger.info(f"Running cross-modal integration test with {n_trials} trials")

        # Track isolated modality activations
        isolated_activations = 0
        modality_patterns = []

        for trial in range(n_trials):
            # Generate BOLD signatures
            bold_sig = self.bold_simulator.generate_conscious_signature()

            # Check for cross-modal integration using available PLV data
            # Framework predicts activation across multiple sensory regions
            # Use frontal connections as proxy for sensory activation
            visual_active = any(
                plv > 0.3
                for conn, plv in bold_sig.plv_values.items()
                if "frontal" in conn and ("parietal" in conn or "temporal" in conn)
            )
            auditory_active = any(
                plv > 0.3
                for conn, plv in bold_sig.plv_values.items()
                if "temporal" in conn
            )
            somatosensory_active = any(
                plv > 0.3
                for conn, plv in bold_sig.plv_values.items()
                if "parietal" in conn
            )

            active_modalities = sum(
                [visual_active, auditory_active, somatosensory_active]
            )
            modality_patterns.append(active_modalities)

            # Count as isolated if only one modality is active
            if active_modalities == 1:
                isolated_activations += 1

        # Calculate statistics
        isolation_rate = isolated_activations / n_trials

        # Test is falsified if >10% show isolated modality activation
        is_falsified = isolation_rate > 0.10
        confidence = isolation_rate if is_falsified else (1 - isolation_rate)

        # Effect size
        expected_rate = 0.10
        effect_size = 2 * (
            np.arcsin(np.sqrt(isolation_rate)) - np.arcsin(np.sqrt(expected_rate))
        )

        # P-value
        from scipy import stats

        p_value = stats.binomtest(
            isolated_activations, n_trials, expected_rate, alternative="greater"
        ).pvalue

        statistical_power = 0.8 if n_trials >= 1000 else 0.6

        # Interpretation
        if is_falsified:
            interpretation = (
                f"FALSIFIED: {isolation_rate:.1%} of trials showed isolated modality "
                f"activation. Ignition can occur without cross-modal integration, "
                f"contradicting framework predictions."
            )
        else:
            interpretation = (
                f"NOT FALSIFIED: Only {isolation_rate:.1%} of trials showed isolated "
                f"activation. Cross-modal integration requirement is supported."
            )

        result = CustomFalsificationResult(
            test_name="Cross-Modal Integration Test",
            is_falsified=is_falsified,
            confidence_level=confidence,
            effect_size=effect_size,
            p_value=p_value,
            statistical_power=statistical_power,
            detailed_metrics={
                "total_trials": n_trials,
                "isolated_activations": isolated_activations,
                "isolation_rate": isolation_rate,
                "mean_active_modalities": np.mean(modality_patterns),
                "modality_distribution": {
                    "0_modalities": modality_patterns.count(0),
                    "1_modality": modality_patterns.count(1),
                    "2_modalities": modality_patterns.count(2),
                    "3_modalities": modality_patterns.count(3),
                },
            },
            interpretation=interpretation,
        )

        self.logger.info(f"Test completed: {interpretation}")
        return result


class MetacognitiveCalibrationTest:
    """
    Example 4C: Custom test for metacognitive calibration requirements.

    This test examines whether consciousness requires calibrated metacognition
    or can occur with severely miscalibrated confidence judgments.
    """

    def __init__(self, random_seed: Optional[int] = None):
        """Initialize the metacognitive calibration test."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.random_seed = random_seed
        self.consciousness_simulator = ConsciousnessAssessmentSimulator(random_seed)

    def run_test(self, n_trials: int = 1000) -> CustomFalsificationResult:
        """
        Run metacognitive calibration falsification test.

        Args:
            n_trials: Number of trials to simulate

        Returns:
            CustomFalsificationResult with test outcomes
        """
        self.logger.info(
            f"Running metacognitive calibration test with {n_trials} trials"
        )

        # Track calibration violations
        miscalibration_count = 0
        calibration_errors = []

        for trial in range(n_trials):
            # Simulate consciousness assessment
            assessment = self.consciousness_simulator.simulate_conscious_trial()

            # Calculate calibration: correlation between confidence and accuracy
            # For simplicity, use confidence rating vs forced choice accuracy
            confidence = assessment.confidence_rating
            accuracy = assessment.forced_choice_accuracy

            # Calibration error: absolute difference
            calibration_error = abs(confidence - accuracy)
            calibration_errors.append(calibration_error)

            # Count as miscalibrated if error > 0.3
            if calibration_error > 0.3:
                miscalibration_count += 1

        # Calculate statistics
        miscalibration_rate = miscalibration_count / n_trials
        mean_calibration_error = np.mean(calibration_errors)

        # Test is falsified if >20% show severe miscalibration
        is_falsified = miscalibration_rate > 0.20
        confidence = miscalibration_rate if is_falsified else (1 - miscalibration_rate)

        # Effect size
        expected_rate = 0.20
        effect_size = 2 * (
            np.arcsin(np.sqrt(miscalibration_rate)) - np.arcsin(np.sqrt(expected_rate))
        )

        # P-value
        from scipy import stats

        p_value = stats.binomtest(
            miscalibration_count, n_trials, expected_rate, alternative="greater"
        ).pvalue

        statistical_power = 0.8 if n_trials >= 1000 else 0.6

        # Interpretation
        if is_falsified:
            interpretation = (
                f"FALSIFIED: {miscalibration_rate:.1%} of trials showed severe "
                f"metacognitive miscalibration. Consciousness can occur without "
                f"calibrated metacognition, contradicting framework predictions."
            )
        else:
            interpretation = (
                f"NOT FALSIFIED: Only {miscalibration_rate:.1%} of trials showed "
                f"severe miscalibration. Metacognitive calibration requirement is supported."
            )

        result = CustomFalsificationResult(
            test_name="Metacognitive Calibration Test",
            is_falsified=is_falsified,
            confidence_level=confidence,
            effect_size=effect_size,
            p_value=p_value,
            statistical_power=statistical_power,
            detailed_metrics={
                "total_trials": n_trials,
                "miscalibration_count": miscalibration_count,
                "miscalibration_rate": miscalibration_rate,
                "mean_calibration_error": mean_calibration_error,
                "std_calibration_error": np.std(calibration_errors),
                "max_calibration_error": np.max(calibration_errors),
            },
            interpretation=interpretation,
        )

        self.logger.info(f"Test completed: {interpretation}")
        return result


def display_custom_test_result(result: CustomFalsificationResult):
    """Display custom test result in formatted output."""
    logger.info("\n" + "=" * 60)
    logger.info(f"TEST: {result.test_name}")
    logger.info("=" * 60)
    logger.info(
        f"Falsification Status: {'FALSIFIED' if result.is_falsified else 'NOT FALSIFIED'}"
    )
    logger.info(f"Confidence Level: {result.confidence_level:.3f}")
    logger.info(f"Effect Size: {result.effect_size:.3f}")
    logger.info(f"P-value: {result.p_value:.6f}")
    logger.info(f"Statistical Power: {result.statistical_power:.3f}")
    logger.info("\nDetailed Metrics:")
    for key, value in result.detailed_metrics.items():
        if isinstance(value, dict):
            logger.info(f"  {key}:")
            for sub_key, sub_value in value.items():
                logger.info(f"    {sub_key}: {sub_value}")
        else:
            logger.info(f"  {key}: {value}")
    logger.info("\nInterpretation:")
    logger.info(f"  {result.interpretation}")
    logger.info("=" * 60 + "\n")


def run_ai_benchmarking_experiment(**kwargs):
    """
    Wrapper function for ai_benchmarking experiment.
    Maps to temporal dynamics falsification test.
    """
    # Use experiment name to generate unique seed
    seed = int(hashlib.sha256("ai_benchmarking".encode()).hexdigest(), 16) % (2**32)
    temporal_test = TemporalDynamicsFalsificationTest(random_seed=seed)
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 1000))
    result = temporal_test.run_test(n_trials=n_trials)
    display_custom_test_result(result)
    return result


def run_change_blindness_experiment(**kwargs):
    """Wrapper for change_blindness experiment."""
    seed = int(hashlib.sha256("change_blindness".encode()).hexdigest(), 16) % (2**32)
    temporal_test = TemporalDynamicsFalsificationTest(random_seed=seed)
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 1000))
    result = temporal_test.run_test(n_trials=n_trials)
    display_custom_test_result(result)
    return result


def run_simon_effect_experiment(**kwargs):
    """Wrapper for simon_effect experiment."""
    seed = int(hashlib.sha256("simon_effect".encode()).hexdigest(), 16) % (2**32)
    crossmodal_test = CrossModalIntegrationTest(random_seed=seed)
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 1000))
    result = crossmodal_test.run_test(n_trials=n_trials)
    display_custom_test_result(result)
    return result


def run_inattentional_blindness_experiment(**kwargs):
    """Wrapper for inattentional_blindness experiment."""
    seed = int(hashlib.sha256("inattentional_blindness".encode()).hexdigest(), 16) % (
        2**32
    )
    crossmodal_test = CrossModalIntegrationTest(random_seed=seed)
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 1000))
    result = crossmodal_test.run_test(n_trials=n_trials)
    display_custom_test_result(result)
    return result


def run_drm_false_memory_experiment(**kwargs):
    """Wrapper for drm_false_memory experiment."""
    seed = int(hashlib.sha256("drm_false_memory".encode()).hexdigest(), 16) % (2**32)
    metacog_test = MetacognitiveCalibrationTest(random_seed=seed)
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 1000))
    result = metacog_test.run_test(n_trials=n_trials)
    display_custom_test_result(result)
    return result


def run_multisensory_integration_experiment(**kwargs):
    """Wrapper for multisensory_integration experiment."""
    seed = int(hashlib.sha256("multisensory_integration".encode()).hexdigest(), 16) % (
        2**32
    )
    metacog_test = MetacognitiveCalibrationTest(random_seed=seed)
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 1000))
    result = metacog_test.run_test(n_trials=n_trials)
    display_custom_test_result(result)
    return result


def run_virtual_navigation_experiment(**kwargs):
    """Wrapper for virtual_navigation experiment."""
    seed = int(hashlib.sha256("virtual_navigation".encode()).hexdigest(), 16) % (2**32)
    temporal_test = TemporalDynamicsFalsificationTest(random_seed=seed)
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 1000))
    result = temporal_test.run_test(n_trials=n_trials)
    display_custom_test_result(result)
    return result


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("APGI Framework - Extended Falsification Criteria Examples")
    print("=" * 70 + "\n")

    # Example 4A: Temporal Dynamics Test
    print("Running Example 4A: Temporal Dynamics Test...")
    temporal_test = TemporalDynamicsFalsificationTest()
    temporal_result = temporal_test.run_test(n_trials=1000)
    display_custom_test_result(temporal_result)

    print("-" * 70 + "\n")

    # Example 4B: Cross-Modal Integration Test
    print("Running Example 4B: Cross-Modal Integration Test...")
    crossmodal_test = CrossModalIntegrationTest()
    crossmodal_result = crossmodal_test.run_test(n_trials=1000)
    display_custom_test_result(crossmodal_result)

    print("-" * 70 + "\n")

    # Example 4C: Metacognitive Calibration Test
    print("Running Example 4C: Metacognitive Calibration Test...")
    metacog_test = MetacognitiveCalibrationTest()
    metacog_result = metacog_test.run_test(n_trials=1000)
    display_custom_test_result(metacog_result)

    print("=" * 70)
    print("All extended falsification tests completed!")
    print("\nNote: These are example custom tests demonstrating how to extend")
    print("the framework with new falsification criteria. Actual implementation")
    print("would require domain expertise and empirical validation.")
    print("=" * 70 + "\n")
