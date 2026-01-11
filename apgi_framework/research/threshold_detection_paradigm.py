"""
Enhanced Threshold Detection Paradigm for APGI Framework.

Provides comprehensive threshold estimation across multiple modalities with
advanced psychophysical methods and neural validation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from enum import Enum
import numpy as np
from scipy import stats, optimize
from scipy.signal import find_peaks
import logging
from datetime import datetime
import json

from ...exceptions import ValidationError, SimulationError
from ...logging.standardized_logging import get_logger

logger = get_logger("threshold_detection")


class ModalityType(Enum):
    """Sensory modalities for threshold detection."""

    VISUAL = "visual"
    AUDITORY = "auditory"
    INTEROCEPTIVE = "interoceptive"
    SOMATOSENSORY = "somatosensory"
    OLFACTORY = "olfactory"
    GUSTATORY = "gustatory"


class ThresholdMethod(Enum):
    """Threshold estimation methods."""

    ADAPTIVE_STAIRCASE = "adaptive_staircase"
    CONSTANT_STIMULI = "constant_stimuli"
    PEST = "pest"  # Parameter Estimation by Sequential Testing
    BAYESIAN_ADAPTIVE = "bayesian_adaptive"
    PSI_METHOD = "psi_method"  # Point of Subjective Information
    ML_METHOD = "ml_method"  # Maximum Likelihood


class ConsciousnessLevel(Enum):
    """Levels of conscious awareness for threshold detection."""

    NO_AWARENESS = "no_awareness"
    WEAK_AWARENESS = "weak_awareness"
    CLEAR_AWARENESS = "clear_awareness"
    CERTAIN_AWARENESS = "certain_awareness"


@dataclass
class StimulusParameters:
    """Parameters for stimulus generation."""

    modality: ModalityType
    intensity: float
    duration: float  # ms
    frequency: Optional[float] = None  # Hz for auditory/visual
    spatial_location: Optional[str] = None
    contrast: Optional[float] = None  # For visual
    amplitude: Optional[float] = None  # For auditory

    # Additional modality-specific parameters
    gabor_orientation: Optional[float] = None  # degrees
    gabor_frequency: Optional[float] = None  # cycles/degree
    tone_frequency: Optional[float] = None  # Hz
    co2_concentration: Optional[float] = None  # % for interoceptive

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "modality": self.modality.value,
            "intensity": self.intensity,
            "duration": self.duration,
            "frequency": self.frequency,
            "spatial_location": self.spatial_location,
            "contrast": self.contrast,
            "amplitude": self.amplitude,
            "gabor_orientation": self.gabor_orientation,
            "gabor_frequency": self.gabor_frequency,
            "tone_frequency": self.tone_frequency,
            "co2_concentration": self.co2_concentration,
        }


@dataclass
class TrialResponse:
    """Response data from a single threshold trial."""

    trial_id: str
    timestamp: datetime
    stimulus_params: StimulusParameters

    # Behavioral response
    detection: bool  # Whether stimulus was detected
    confidence: float  # 0-1 confidence rating
    reaction_time: float  # ms
    consciousness_level: ConsciousnessLevel

    # Neural response (optional)
    p3b_amplitude: Optional[float] = None
    p3b_latency: Optional[float] = None
    gamma_power: Optional[float] = None
    pupil_dilation: Optional[float] = None
    heart_rate_change: Optional[float] = None

    # Quality metrics
    signal_quality: float = 1.0  # 0-1
    artifact_detected: bool = False


@dataclass
class ThresholdEstimate:
    """Threshold estimation results."""

    modality: ModalityType
    method: ThresholdMethod
    threshold_value: float
    confidence_interval: Tuple[float, float]

    # Psychometric function parameters
    alpha: float  # Threshold
    beta: float  # Slope
    gamma: float  # Guess rate
    lambda_: float  # Lapse rate

    # Quality metrics
    goodness_of_fit: float  # R²
    log_likelihood: float
    bic_score: float
    aic_score: float

    # Neural validation
    neural_correlation: float = 0.0
    neural_threshold: Optional[float] = None

    # Metadata
    n_trials: int
    date_estimated: datetime = field(default_factory=datetime.now)


@dataclass
class CrossModalThreshold:
    """Cross-modal threshold comparison."""

    primary_modality: ModalityType
    comparison_modality: ModalityType

    # Threshold values
    primary_threshold: float
    comparison_threshold: float

    # Normalization metrics
    sensitivity_ratio: float
    cross_modal_correlation: float

    # Neural signatures
    shared_neural_signatures: List[str]
    modality_specific_signatures: List[str]


class PsychometricFunction:
    """
    Psychometric function fitting and analysis.

    Implements various psychometric function forms for threshold estimation.
    """

    def __init__(self, function_type: str = "cumulative_gaussian"):
        """
        Initialize psychometric function.

        Args:
            function_type: Type of psychometric function
        """
        self.function_type = function_type
        self.bounds = {
            "alpha": (0, 100),  # Threshold bounds
            "beta": (0.01, 10),  # Slope bounds
            "gamma": (0, 0.5),  # Guess rate bounds
            "lambda": (0, 0.1),  # Lapse rate bounds
        }

    def cumulative_gaussian(
        self, x: np.ndarray, alpha: float, beta: float, gamma: float, lambda_: float
    ) -> np.ndarray:
        """
        Cumulative Gaussian psychometric function.

        Args:
            x: Stimulus intensities
            alpha: Threshold parameter
            beta: Slope parameter
            gamma: Guess rate
            lambda_: Lapse rate

        Returns:
            Psychometric function values
        """
        return gamma + (1 - gamma - lambda_) * stats.norm.cdf(x, alpha, 1 / beta)

    def weibull(
        self, x: np.ndarray, alpha: float, beta: float, gamma: float, lambda_: float
    ) -> np.ndarray:
        """
        Weibull psychometric function.

        Args:
            x: Stimulus intensities
            alpha: Threshold parameter
            beta: Shape parameter
            gamma: Guess rate
            lambda_: Lapse rate

        Returns:
            Psychometric function values
        """
        return gamma + (1 - gamma - lambda_) * (1 - np.exp(-((x / alpha) ** beta)))

    def logistic(
        self, x: np.ndarray, alpha: float, beta: float, gamma: float, lambda_: float
    ) -> np.ndarray:
        """
        Logistic psychometric function.

        Args:
            x: Stimulus intensities
            alpha: Threshold parameter
            beta: Slope parameter
            gamma: Guess rate
            lambda_: Lapse rate

        Returns:
            Psychometric function values
        """
        return gamma + (1 - gamma - lambda_) / (1 + np.exp(-beta * (x - alpha)))

    def fit_function(
        self,
        intensities: np.ndarray,
        responses: np.ndarray,
        initial_params: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """
        Fit psychometric function to data.

        Args:
            intensities: Stimulus intensity values
            responses: Binary response values
            initial_params: Initial parameter estimates

        Returns:
            Fitted parameters and quality metrics
        """
        if initial_params is None:
            # Use reasonable initial estimates
            initial_params = [np.median(intensities), 1.0, 0.5, 0.05]

        # Select function based on type
        if self.function_type == "cumulative_gaussian":
            func = self.cumulative_gaussian
        elif self.function_type == "weibull":
            func = self.weibull
        elif self.function_type == "logistic":
            func = self.logistic
        else:
            func = self.cumulative_gaussian

        # Fit function
        try:
            popt, pcov = optimize.curve_fit(
                func,
                intensities,
                responses,
                p0=initial_params,
                bounds=(
                    [
                        self.bounds["alpha"][0],
                        self.bounds["beta"][0],
                        self.bounds["gamma"][0],
                        self.bounds["lambda"][0],
                    ],
                    [
                        self.bounds["alpha"][1],
                        self.bounds["beta"][1],
                        self.bounds["gamma"][1],
                        self.bounds["lambda"][1],
                    ],
                ),
                maxfev=10000,
            )

            alpha, beta, gamma, lambda_ = popt

            # Calculate quality metrics
            predicted = func(intensities, alpha, beta, gamma, lambda_)

            # Goodness of fit
            ss_res = np.sum((responses - predicted) ** 2)
            ss_tot = np.sum((responses - np.mean(responses)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            # Log likelihood
            log_likelihood = np.sum(
                responses * np.log(predicted + 1e-10)
                + (1 - responses) * np.log(1 - predicted + 1e-10)
            )

            # Information criteria
            n = len(responses)
            k = 4  # Number of parameters
            aic = 2 * k - 2 * log_likelihood
            bic = k * np.log(n) - 2 * log_likelihood

            return {
                "parameters": {
                    "alpha": alpha,
                    "beta": beta,
                    "gamma": gamma,
                    "lambda": lambda_,
                },
                "covariance": pcov,
                "r_squared": r_squared,
                "log_likelihood": log_likelihood,
                "aic": aic,
                "bic": bic,
                "predicted": predicted,
            }

        except Exception as e:
            logger.error(f"Failed to fit psychometric function: {e}")
            raise ValidationError(f"Psychometric function fitting failed: {e}")


class AdaptiveStaircase:
    """
    Adaptive staircase procedure for threshold estimation.

    Implements various staircase rules including 3-up/1-down, 2-up/1-down, etc.
    """

    def __init__(
        self,
        start_intensity: float,
        step_size: float,
        rule: str = "3up_1down",
        max_trials: int = 100,
        min_intensity: float = 0.0,
        max_intensity: float = 100.0,
    ):
        """
        Initialize adaptive staircase.

        Args:
            start_intensity: Starting stimulus intensity
            step_size: Initial step size
            rule: Staircase rule (e.g., "3up_1down")
            max_trials: Maximum number of trials
            min_intensity: Minimum allowed intensity
            max_intensity: Maximum allowed intensity
        """
        self.start_intensity = start_intensity
        self.step_size = step_size
        self.rule = rule
        self.max_trials = max_trials
        self.min_intensity = min_intensity
        self.max_intensity = max_intensity

        # Parse rule
        up_count, down_count = self._parse_rule(rule)
        self.up_count = up_count
        self.down_count = down_count

        # State variables
        self.current_intensity = start_intensity
        self.trial_count = 0
        self.consecutive_correct = 0
        self.consecutive_incorrect = 0
        self.intensity_history = []
        self.response_history = []

        # Reversal tracking
        self.reversals = []
        self.last_direction = None

        logger.info(f"Adaptive staircase initialized: {rule}, start={start_intensity}")

    def _parse_rule(self, rule: str) -> Tuple[int, int]:
        """Parse staircase rule string."""
        parts = rule.split("_")
        if len(parts) != 3 or parts[1] != "up" or parts[2] != "down":
            raise ValidationError(f"Invalid staircase rule: {rule}")

        up_count = int(parts[0])
        down_count = 1  # Standard down rule

        return up_count, down_count

    def get_next_intensity(self) -> float:
        """Get next stimulus intensity."""
        return self.current_intensity

    def update_staircase(self, response: bool) -> None:
        """
        Update staircase based on response.

        Args:
            response: Whether response was correct/detected
        """
        self.trial_count += 1
        self.intensity_history.append(self.current_intensity)
        self.response_history.append(response)

        # Update consecutive counters
        if response:
            self.consecutive_correct += 1
            self.consecutive_incorrect = 0
        else:
            self.consecutive_incorrect += 1
            self.consecutive_correct = 0

        # Check for reversal
        current_direction = "up" if response else "down"
        if self.last_direction and current_direction != self.last_direction:
            self.reversals.append(self.trial_count)
        self.last_direction = current_direction

        # Update intensity based on rule
        if response and self.consecutive_correct >= self.up_count:
            self._decrease_intensity()
            self.consecutive_correct = 0
        elif not response and self.consecutive_incorrect >= self.down_count:
            self._increase_intensity()
            self.consecutive_incorrect = 0

    def _increase_intensity(self) -> None:
        """Increase stimulus intensity."""
        self.current_intensity = min(
            self.current_intensity + self.step_size, self.max_intensity
        )

    def _decrease_intensity(self) -> None:
        """Decrease stimulus intensity."""
        self.current_intensity = max(
            self.current_intensity - self.step_size, self.min_intensity
        )

    def get_threshold_estimate(self) -> float:
        """Get threshold estimate from staircase."""
        if len(self.reversals) < 2:
            return self.current_intensity

        # Use mean of last few reversals
        recent_reversals = (
            self.reversals[-4:] if len(self.reversals) >= 4 else self.reversals
        )
        reversal_intensities = []

        for reversal_trial in recent_reversals:
            idx = reversal_trial - 1  # Index of intensity at reversal
            if idx >= 0 and idx < len(self.intensity_history):
                reversal_intensities.append(self.intensity_history[idx])

        if reversal_intensities:
            return np.mean(reversal_intensities)
        else:
            return self.current_intensity

    def is_complete(self) -> bool:
        """Check if staircase is complete."""
        return self.trial_count >= self.max_trials or len(self.reversals) >= 8


class ThresholdDetectionSystem:
    """
    Comprehensive threshold detection system for APGI Framework.

    Provides multi-modal threshold estimation with neural validation and
    cross-modal comparisons.
    """

    def __init__(self, significance_threshold: float = 0.05):
        """
        Initialize threshold detection system.

        Args:
            significance_threshold: Statistical significance threshold
        """
        self.significance_threshold = significance_threshold
        self.psychometric_functions = {
            "cumulative_gaussian": PsychometricFunction("cumulative_gaussian"),
            "weibull": PsychometricFunction("weibull"),
            "logistic": PsychometricFunction("logistic"),
        }

        # Storage for results
        self.threshold_estimates = {}
        self.trial_data = {}
        self.cross_modal_comparisons = {}

        logger.info("ThresholdDetectionSystem initialized")

    def run_threshold_estimation(
        self,
        modality: ModalityType,
        method: ThresholdMethod,
        n_trials: int = 100,
        target_performance: float = 0.75,
    ) -> ThresholdEstimate:
        """
        Run threshold estimation for a specific modality and method.

        Args:
            modality: Sensory modality
            method: Threshold estimation method
            n_trials: Number of trials to run
            target_performance: Target performance level (0-1)

        Returns:
            Threshold estimate with confidence intervals
        """
        logger.info(f"Running {method.value} threshold estimation for {modality.value}")

        # Generate trial data (mock implementation)
        trial_data = self._generate_trial_data(modality, n_trials)

        # Fit psychometric function
        intensities = np.array([t.stimulus_params.intensity for t in trial_data])
        responses = np.array([t.detection for t in trial_data])

        # Use best fitting function
        best_function = None
        best_fit = None
        best_bic = float("inf")

        for func_name, func in self.psychometric_functions.items():
            try:
                fit_result = func.fit_function(intensities, responses)
                if fit_result["bic"] < best_bic:
                    best_bic = fit_result["bic"]
                    best_fit = fit_result
                    best_function = func_name
            except Exception as e:
                logger.warning(f"Failed to fit {func_name}: {e}")
                continue

        if best_fit is None:
            raise ValidationError("Failed to fit any psychometric function")

        # Extract threshold at target performance
        threshold = self._extract_threshold_at_performance(
            best_function, best_fit["parameters"], target_performance
        )

        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(
            intensities, responses, threshold
        )

        # Neural validation
        neural_correlation, neural_threshold = self._validate_with_neural_data(
            trial_data
        )

        # Create threshold estimate
        estimate = ThresholdEstimate(
            modality=modality,
            method=method,
            threshold_value=threshold,
            confidence_interval=confidence_interval,
            alpha=best_fit["parameters"]["alpha"],
            beta=best_fit["parameters"]["beta"],
            gamma=best_fit["parameters"]["gamma"],
            lambda_=best_fit["parameters"]["lambda"],
            goodness_of_fit=best_fit["r_squared"],
            log_likelihood=best_fit["log_likelihood"],
            bic_score=best_fit["bic"],
            aic_score=best_fit["aic"],
            neural_correlation=neural_correlation,
            neural_threshold=neural_threshold,
            n_trials=n_trials,
        )

        # Store results
        key = f"{modality.value}_{method.value}"
        self.threshold_estimates[key] = estimate
        self.trial_data[key] = trial_data

        logger.info(
            f"Threshold estimation completed: {threshold:.3f} (95% CI: {confidence_interval[0]:.3f}-{confidence_interval[1]:.3f})"
        )

        return estimate

    def _generate_trial_data(
        self, modality: ModalityType, n_trials: int
    ) -> List[TrialResponse]:
        """Generate mock trial data for testing."""
        trial_data = []

        # Generate intensity range based on modality
        if modality == ModalityType.VISUAL:
            intensity_range = np.linspace(0.1, 10, n_trials)
        elif modality == ModalityType.AUDITORY:
            intensity_range = np.linspace(0, 100, n_trials)  # dB SPL
        elif modality == ModalityType.INTEROCEPTIVE:
            intensity_range = np.linspace(0, 10, n_trials)  # CO2 %
        else:
            intensity_range = np.linspace(0, 100, n_trials)

        # Simulate responses with psychometric function
        true_threshold = np.median(intensity_range)
        true_slope = 1.0

        for i, intensity in enumerate(intensity_range):
            # Generate response probability
            response_prob = stats.norm.cdf((intensity - true_threshold) * true_slope)
            response = np.random.random() < response_prob

            # Create stimulus parameters
            stim_params = StimulusParameters(
                modality=modality,
                intensity=intensity,
                duration=100,  # ms
                frequency=1000 if modality == ModalityType.AUDITORY else None,
            )

            # Create trial response
            trial = TrialResponse(
                trial_id=f"trial_{i}",
                timestamp=datetime.now(),
                stimulus_params=stim_params,
                detection=response,
                confidence=(
                    0.5 + 0.5 * response_prob if response else 0.5 * (1 - response_prob)
                ),
                reaction_time=300 + np.random.normal(0, 50),
                consciousness_level=self._determine_consciousness_level(response_prob),
                p3b_amplitude=(
                    response_prob * 5 + np.random.normal(0, 1)
                    if response
                    else np.random.normal(0, 1)
                ),
                gamma_power=(
                    response_prob * 2 + np.random.normal(0, 0.5)
                    if response
                    else np.random.normal(0, 0.5)
                ),
                pupil_dilation=(
                    response_prob * 0.5 + np.random.normal(0, 0.1)
                    if response
                    else np.random.normal(0, 0.1)
                ),
            )

            trial_data.append(trial)

        return trial_data

    def _determine_consciousness_level(
        self, response_prob: float
    ) -> ConsciousnessLevel:
        """Determine consciousness level from response probability."""
        if response_prob < 0.25:
            return ConsciousnessLevel.NO_AWARENESS
        elif response_prob < 0.5:
            return ConsciousnessLevel.WEAK_AWARENESS
        elif response_prob < 0.75:
            return ConsciousnessLevel.CLEAR_AWARENESS
        else:
            return ConsciousnessLevel.CERTAIN_AWARENESS

    def _extract_threshold_at_performance(
        self, function_name: str, params: Dict[str, float], target_performance: float
    ) -> float:
        """Extract threshold at target performance level."""
        func = self.psychometric_functions[function_name]

        # Find intensity that gives target performance
        def objective(x):
            return (
                func.cumulative_gaussian(
                    np.array([x]),
                    params["alpha"],
                    params["beta"],
                    params["gamma"],
                    params["lambda"],
                )[0]
                - target_performance
            )

        try:
            result = optimize.brentq(objective, 0, 100)
            return result
        except Exception:
            # Fallback to alpha parameter
            return params["alpha"]

    def _calculate_confidence_interval(
        self, intensities: np.ndarray, responses: np.ndarray, threshold: float
    ) -> Tuple[float, float]:
        """Calculate confidence interval for threshold estimate."""
        # Bootstrap confidence interval
        n_bootstrap = 1000
        bootstrap_thresholds = []

        for _ in range(n_bootstrap):
            # Resample with replacement
            indices = np.random.choice(len(intensities), len(intensities), replace=True)
            boot_intensities = intensities[indices]
            boot_responses = responses[indices]

            # Fit function and get threshold
            try:
                fit_result = self.psychometric_functions[
                    "cumulative_gaussian"
                ].fit_function(boot_intensities, boot_responses)
                boot_threshold = fit_result["parameters"]["alpha"]
                bootstrap_thresholds.append(boot_threshold)
            except Exception:
                continue

        if bootstrap_thresholds:
            ci_lower = np.percentile(bootstrap_thresholds, 2.5)
            ci_upper = np.percentile(bootstrap_thresholds, 97.5)
        else:
            # Fallback to simple standard error
            se = np.std(intensities) / np.sqrt(len(intensities))
            ci_lower = threshold - 1.96 * se
            ci_upper = threshold + 1.96 * se

        return (ci_lower, ci_upper)

    def _validate_with_neural_data(
        self, trial_data: List[TrialResponse]
    ) -> Tuple[float, Optional[float]]:
        """Validate threshold with neural data."""
        # Extract neural signatures
        p3b_amplitudes = [
            t.p3b_amplitude for t in trial_data if t.p3b_amplitude is not None
        ]
        intensities = [
            t.stimulus_params.intensity
            for t in trial_data
            if t.p3b_amplitude is not None
        ]
        detections = [t.detection for t in trial_data if t.p3b_amplitude is not None]

        if len(p3b_amplitudes) < 10:
            return 0.0, None

        # Correlate neural response with behavioral detection
        correlation = np.corrcoef(p3b_amplitudes, detections)[0, 1]
        if np.isnan(correlation):
            correlation = 0.0

        # Find neural threshold (50% of max neural response)
        max_neural = max(p3b_amplitudes)
        neural_threshold_idx = next(
            (i for i, amp in enumerate(p3b_amplitudes) if amp >= 0.5 * max_neural), None
        )

        neural_threshold = (
            intensities[neural_threshold_idx]
            if neural_threshold_idx is not None
            else None
        )

        return float(correlation), neural_threshold

    def compare_cross_modal_thresholds(
        self, modality1: ModalityType, modality2: ModalityType
    ) -> CrossModalThreshold:
        """
        Compare thresholds across modalities.

        Args:
            modality1: First modality
            modality2: Second modality

        Returns:
            Cross-modal threshold comparison
        """
        logger.info(f"Comparing thresholds: {modality1.value} vs {modality2.value}")

        # Get threshold estimates
        key1 = f"{modality1.value}_adaptive_staircase"
        key2 = f"{modality2.value}_adaptive_staircase"

        if key1 not in self.threshold_estimates or key2 not in self.threshold_estimates:
            raise ValidationError(
                "Threshold estimates not available for both modalities"
            )

        threshold1 = self.threshold_estimates[key1]
        threshold2 = self.threshold_estimates[key2]

        # Calculate sensitivity ratio
        sensitivity_ratio = threshold1.threshold_value / threshold2.threshold_value

        # Get neural data for correlation
        neural_data1 = self.trial_data[key1]
        neural_data2 = self.trial_data[key2]

        cross_modal_correlation = self._calculate_cross_modal_correlation(
            neural_data1, neural_data2
        )

        # Identify shared and modality-specific neural signatures
        shared_signatures, modality_specific_signatures = (
            self._analyze_neural_signatures(neural_data1, neural_data2)
        )

        comparison = CrossModalThreshold(
            primary_modality=modality1,
            comparison_modality=modality2,
            primary_threshold=threshold1.threshold_value,
            comparison_threshold=threshold2.threshold_value,
            sensitivity_ratio=sensitivity_ratio,
            cross_modal_correlation=cross_modal_correlation,
            shared_neural_signatures=shared_signatures,
            modality_specific_signatures=modality_specific_signatures,
        )

        # Store comparison
        comparison_key = f"{modality1.value}_vs_{modality2.value}"
        self.cross_modal_comparisons[comparison_key] = comparison

        logger.info(
            f"Cross-modal comparison completed: ratio={sensitivity_ratio:.3f}, correlation={cross_modal_correlation:.3f}"
        )

        return comparison

    def _calculate_cross_modal_correlation(
        self, data1: List[TrialResponse], data2: List[TrialResponse]
    ) -> float:
        """Calculate correlation between neural responses across modalities."""
        # Extract P3b amplitudes
        p3b1 = [t.p3b_amplitude for t in data1 if t.p3b_amplitude is not None]
        p3b2 = [t.p3b_amplitude for t in data2 if t.p3b_amplitude is not None]

        if len(p3b1) < 5 or len(p3b2) < 5:
            return 0.0

        # Align by trial count
        min_len = min(len(p3b1), len(p3b2))
        p3b1_aligned = p3b1[:min_len]
        p3b2_aligned = p3b2[:min_len]

        correlation = np.corrcoef(p3b1_aligned, p3b2_aligned)[0, 1]
        return float(correlation) if not np.isnan(correlation) else 0.0

    def _analyze_neural_signatures(
        self, data1: List[TrialResponse], data2: List[TrialResponse]
    ) -> Tuple[List[str], List[str]]:
        """Analyze shared and modality-specific neural signatures."""
        shared_signatures = []
        modality_specific_signatures = []

        # Check P3b presence in both
        p3b1_present = any(t.p3b_amplitude is not None for t in data1)
        p3b2_present = any(t.p3b_amplitude is not None for t in data2)

        if p3b1_present and p3b2_present:
            shared_signatures.append("P3b_component")
        elif p3b1_present:
            modality_specific_signatures.append("P3b_component_modality1")
        elif p3b2_present:
            modality_specific_signatures.append("P3b_component_modality2")

        # Check gamma synchrony
        gamma1_present = any(t.gamma_power is not None for t in data1)
        gamma2_present = any(t.gamma_power is not None for t in data2)

        if gamma1_present and gamma2_present:
            shared_signatures.append("gamma_synchrony")

        # Check pupil dilation
        pupil1_present = any(t.pupil_dilation is not None for t in data1)
        pupil2_present = any(t.pupil_dilation is not None for t in data2)

        if pupil1_present and gamma2_present:
            shared_signatures.append("pupil_dilation")

        return shared_signatures, modality_specific_signatures

    def generate_threshold_report(self) -> str:
        """
        Generate comprehensive threshold detection report.

        Returns:
            Formatted report string
        """
        report = []
        report.append("Threshold Detection Paradigm Report")
        report.append("=" * 50)
        report.append("")

        # Summary of threshold estimates
        report.append("## THRESHOLD ESTIMATES")
        report.append("")

        for key, estimate in self.threshold_estimates.items():
            report.append(f"### {key.replace('_', ' ').title()}")
            report.append(f"Threshold: {estimate.threshold_value:.3f}")
            report.append(
                f"95% CI: [{estimate.confidence_interval[0]:.3f}, {estimate.confidence_interval[1]:.3f}]"
            )
            report.append(f"Method: {estimate.method.value}")
            report.append(f"Trials: {estimate.n_trials}")
            report.append(f"Goodness of fit (R²): {estimate.goodness_of_fit:.3f}")
            report.append(f"BIC: {estimate.bic_score:.1f}")

            if estimate.neural_correlation > 0:
                report.append(f"Neural correlation: {estimate.neural_correlation:.3f}")
                if estimate.neural_threshold:
                    report.append(f"Neural threshold: {estimate.neural_threshold:.3f}")

            report.append("")

        # Cross-modal comparisons
        if self.cross_modal_comparisons:
            report.append("## CROSS-MODAL COMPARISONS")
            report.append("")

            for key, comparison in self.cross_modal_comparisons.items():
                report.append(f"### {key.replace('_', ' ').title()}")
                report.append(f"Sensitivity ratio: {comparison.sensitivity_ratio:.3f}")
                report.append(
                    f"Cross-modal correlation: {comparison.cross_modal_correlation:.3f}"
                )
                report.append(
                    f"Shared neural signatures: {', '.join(comparison.shared_neural_signatures)}"
                )
                report.append(
                    f"Modality-specific signatures: {', '.join(comparison.modality_specific_signatures)}"
                )
                report.append("")

        return "\n".join(report)


# Factory function for easy instantiation
def create_threshold_detection_system(
    significance_threshold: float = 0.05,
) -> ThresholdDetectionSystem:
    """
    Create a threshold detection system with default settings.

    Args:
        significance_threshold: Statistical significance threshold

    Returns:
        Configured ThresholdDetectionSystem instance
    """
    return ThresholdDetectionSystem(significance_threshold=significance_threshold)
