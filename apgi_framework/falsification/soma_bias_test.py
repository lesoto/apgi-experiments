"""
Soma-Bias Test

Implements the secondary falsification test for soma-bias absence. Tests whether
interoceptive prediction errors receive preferential weighting compared to
exteroceptive prediction errors when precision is matched.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
from datetime import datetime
from scipy import stats

from ..core.equation import APGIEquation
from ..core.precision import PrecisionCalculator
from ..core.prediction_error import PredictionErrorProcessor
from ..exceptions import ValidationError, SimulationError
from .error_handling_wrapper import with_error_handling, log_test_execution
import logging

logger = logging.getLogger(__name__)


@dataclass
class SomaBiasTrialResult:
    """Result of a single soma-bias trial"""

    trial_id: str
    participant_id: str
    timestamp: datetime

    # Prediction errors
    extero_error: float
    intero_error: float

    # Matched precision values
    extero_precision: float
    intero_precision: float
    precision_match_quality: float

    # Ignition responses
    extero_ignition_probability: float
    intero_ignition_probability: float
    ignition_difference: float

    # Bias calculation
    beta_value: float  # Bias coefficient
    bias_direction: str  # "intero", "extero", or "none"
    bias_magnitude: float

    # Statistical measures
    confidence_interval: Tuple[float, float]
    p_value: float

    # Falsification assessment
    is_falsifying: bool  # True if β ≈ 1.0 (no bias)
    confidence_level: float


@dataclass
class SomaBiasTestResult:
    """Complete result of soma-bias testing"""

    test_id: str
    n_trials: int
    n_participants: int
    timestamp: datetime

    trial_results: List[SomaBiasTrialResult]

    # Participant-level analysis
    participant_beta_values: Dict[str, float]
    participant_bias_directions: Dict[str, str]

    # Population-level statistics
    mean_beta: float
    median_beta: float
    beta_std: float
    beta_confidence_interval: Tuple[float, float]

    # Bias analysis
    intero_bias_participants: int
    extero_bias_participants: int
    no_bias_participants: int
    bias_distribution: Dict[str, float]

    # Statistical analysis
    population_p_value: float
    effect_size: float
    statistical_power: float

    # Falsification assessment (β ≈ 1.0 indicates no soma-bias)
    meets_sample_size_requirement: bool  # n > 100
    is_framework_falsified: bool
    interpretation: str


class SomaBiasTest:
    """
    Test controller for soma-bias falsification criterion.

    Tests whether interoceptive prediction errors receive preferential weighting
    when precision is matched between interoceptive and exteroceptive domains.

    Falsification occurs when β ≈ 1.0 (no bias toward interoceptive signals)
    in a large sample (n > 100).
    """

    def __init__(self):
        self.equation = APGIEquation()
        self.precision_calculator = PrecisionCalculator()
        self.error_processor = PredictionErrorProcessor()

        # Bias thresholds
        self.no_bias_threshold = (0.95, 1.05)  # β values indicating no bias
        self.intero_bias_threshold = 1.2  # β > 1.2 indicates intero bias
        self.extero_bias_threshold = 0.8  # β < 0.8 indicates extero bias

        # Statistical requirements
        self.minimum_sample_size = 100
        self.falsification_threshold = 0.6  # Proportion with no bias for falsification

    @with_error_handling(validate_params=True, enable_retry=True, log_errors=True)
    def run_soma_bias_test(
        self,
        n_trials_per_participant: int = 50,
        n_participants: int = 120,
        test_id: Optional[str] = None,
    ) -> SomaBiasTestResult:
        """
        Run soma-bias test across multiple trials and participants.

        Args:
            n_trials_per_participant: Number of trials per participant
            n_participants: Number of participants (should be > 100)
            test_id: Optional test identifier

        Returns:
            Complete soma-bias test results

        Raises:
            ValidationError: If parameters are invalid
            SimulationError: If simulation fails
        """
        start_time = datetime.now()

        try:
            # Validate parameters
            if n_trials_per_participant <= 0:
                raise ValidationError(
                    f"n_trials_per_participant must be positive, got {n_trials_per_participant}"
                )
            if n_participants < self.minimum_sample_size:
                raise ValidationError(
                    f"Sample size {n_participants} below minimum {self.minimum_sample_size}"
                )

            if test_id is None:
                test_id = f"soma_bias_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            logger.info(f"Starting soma-bias test: {test_id}")
            logger.info(
                f"Parameters: n_trials_per_participant={n_trials_per_participant}, n_participants={n_participants}"
            )

            trial_results = []
            participant_results = {}

            for participant_id in range(n_participants):
                participant_key = f"P{participant_id:03d}"
                participant_trials = []

                for trial_num in range(n_trials_per_participant):
                    trial_id = f"{test_id}_p{participant_id:03d}_t{trial_num:03d}"

                    try:
                        trial_result = self._run_single_trial(
                            trial_id=trial_id, participant_id=participant_key
                        )
                        trial_results.append(trial_result)
                        participant_trials.append(trial_result)
                    except Exception as e:
                        logger.error(f"Trial {trial_id} failed: {str(e)}")
                        continue

                participant_results[participant_key] = participant_trials

            if not trial_results:
                raise SimulationError("All trials failed - no results to analyze")

            # Analyze results
            result = self._analyze_results(
                test_id,
                trial_results,
                participant_results,
                n_trials_per_participant,
                n_participants,
            )

            end_time = datetime.now()
            log_test_execution("Soma-Bias Test", start_time, end_time, True)

            return result

        except Exception as e:
            end_time = datetime.now()
            log_test_execution("Soma-Bias Test", start_time, end_time, False, e)
            raise

    def _run_single_trial(
        self, trial_id: str, participant_id: str
    ) -> SomaBiasTrialResult:
        """
        Run a single soma-bias trial with matched precision.

        Args:
            trial_id: Unique trial identifier
            participant_id: Participant identifier

        Returns:
            Single trial result
        """
        timestamp = datetime.now()

        # Generate matched precision values
        extero_precision, intero_precision, match_quality = (
            self._generate_matched_precision()
        )

        # Generate prediction errors
        extero_error, intero_error = self._generate_prediction_errors()

        # Calculate ignition probabilities for each domain
        extero_ignition_prob = self._calculate_ignition_probability(
            extero_error, extero_precision, domain="exteroceptive"
        )

        intero_ignition_prob = self._calculate_ignition_probability(
            intero_error, intero_precision, domain="interoceptive"
        )

        ignition_difference = intero_ignition_prob - extero_ignition_prob

        # Calculate bias coefficient (β)
        beta_value = self._calculate_beta_coefficient(
            extero_error,
            intero_error,
            extero_precision,
            intero_precision,
            extero_ignition_prob,
            intero_ignition_prob,
        )

        # Determine bias direction and magnitude
        bias_direction, bias_magnitude = self._analyze_bias(beta_value)

        # Calculate statistical measures
        confidence_interval = self._calculate_confidence_interval(beta_value)
        p_value = self._calculate_p_value(beta_value)

        # Determine if this trial is falsifying
        is_falsifying = self._determine_falsification(beta_value)

        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(
            beta_value, match_quality, ignition_difference
        )

        return SomaBiasTrialResult(
            trial_id=trial_id,
            participant_id=participant_id,
            timestamp=timestamp,
            extero_error=extero_error,
            intero_error=intero_error,
            extero_precision=extero_precision,
            intero_precision=intero_precision,
            precision_match_quality=match_quality,
            extero_ignition_probability=extero_ignition_prob,
            intero_ignition_probability=intero_ignition_prob,
            ignition_difference=ignition_difference,
            beta_value=beta_value,
            bias_direction=bias_direction,
            bias_magnitude=bias_magnitude,
            confidence_interval=confidence_interval,
            p_value=p_value,
            is_falsifying=is_falsifying,
            confidence_level=confidence_level,
        )

    def _generate_matched_precision(self) -> Tuple[float, float, float]:
        """Generate matched precision values for extero and intero domains"""
        # Base precision value
        base_precision = np.random.uniform(1.0, 3.0)

        # Add small random variation to simulate matching procedure
        extero_precision = base_precision + np.random.normal(0, 0.1)
        intero_precision = base_precision + np.random.normal(0, 0.1)

        # Ensure positive values
        extero_precision = max(0.1, extero_precision)
        intero_precision = max(0.1, intero_precision)

        # Calculate match quality (1.0 = perfect match)
        precision_difference = abs(extero_precision - intero_precision)
        max_precision = max(extero_precision, intero_precision)
        match_quality = 1.0 - (precision_difference / max_precision)

        return extero_precision, intero_precision, match_quality

    def _generate_prediction_errors(self) -> Tuple[float, float]:
        """Generate prediction errors for both domains"""
        # Generate errors from similar distributions
        extero_error = np.random.normal(0, 1.0)
        intero_error = np.random.normal(0, 1.0)

        # Standardize to z-scores
        extero_error = self.error_processor.standardize_error(extero_error)
        intero_error = self.error_processor.standardize_error(intero_error)

        return abs(extero_error), abs(intero_error)

    def _calculate_ignition_probability(
        self, error: float, precision: float, domain: str
    ) -> float:
        """Calculate ignition probability for a given domain"""
        # Calculate precision-weighted surprise
        surprise = precision * error

        # Use standard threshold and steepness
        threshold = 3.5
        steepness = 2.0

        # Calculate ignition probability
        ignition_prob = self.equation.calculate_ignition_probability(
            surprise, threshold, steepness
        )

        return ignition_prob

    def _calculate_beta_coefficient(
        self,
        extero_error: float,
        intero_error: float,
        extero_precision: float,
        intero_precision: float,
        extero_ignition: float,
        intero_ignition: float,
    ) -> float:
        """
        Calculate bias coefficient β.

        β = (intero_ignition / intero_weighted_error) / (extero_ignition / extero_weighted_error)

        β > 1: Interoceptive bias
        β < 1: Exteroceptive bias
        β ≈ 1: No bias
        """
        # Calculate weighted errors
        extero_weighted = extero_precision * extero_error
        intero_weighted = intero_precision * intero_error

        # Avoid division by zero
        if extero_weighted == 0 or intero_weighted == 0:
            return 1.0

        # Calculate response ratios
        extero_ratio = extero_ignition / extero_weighted if extero_weighted > 0 else 0
        intero_ratio = intero_ignition / intero_weighted if intero_weighted > 0 else 0

        # Calculate β
        if extero_ratio == 0:
            beta = 2.0 if intero_ratio > 0 else 1.0
        else:
            beta = intero_ratio / extero_ratio

        # Bound β to reasonable range
        return np.clip(beta, 0.1, 10.0)

    def _analyze_bias(self, beta_value: float) -> Tuple[str, float]:
        """Analyze bias direction and magnitude from β value"""
        if self.no_bias_threshold[0] <= beta_value <= self.no_bias_threshold[1]:
            bias_direction = "none"
            bias_magnitude = abs(beta_value - 1.0)
        elif beta_value > self.intero_bias_threshold:
            bias_direction = "intero"
            bias_magnitude = beta_value - 1.0
        elif beta_value < self.extero_bias_threshold:
            bias_direction = "extero"
            bias_magnitude = 1.0 - beta_value
        else:
            # Intermediate values
            if beta_value > 1.0:
                bias_direction = "intero"
                bias_magnitude = beta_value - 1.0
            else:
                bias_direction = "extero"
                bias_magnitude = 1.0 - beta_value

        return bias_direction, bias_magnitude

    def _calculate_confidence_interval(self, beta_value: float) -> Tuple[float, float]:
        """Calculate confidence interval for β value"""
        # Simplified confidence interval calculation
        # In reality, this would use bootstrap or analytical methods

        std_error = 0.1 * beta_value  # Proportional error
        margin_error = 1.96 * std_error  # 95% CI

        lower_bound = max(0.1, beta_value - margin_error)
        upper_bound = min(10.0, beta_value + margin_error)

        return (lower_bound, upper_bound)

    def _calculate_p_value(self, beta_value: float) -> float:
        """Calculate p-value for test against null hypothesis β = 1"""
        # Null hypothesis: β = 1 (no bias)
        # Alternative: β ≠ 1 (bias present)

        # Simplified p-value calculation
        deviation = abs(beta_value - 1.0)

        if deviation < 0.05:
            return 0.8  # Not significant
        elif deviation < 0.1:
            return 0.3
        elif deviation < 0.2:
            return 0.1
        else:
            return 0.01  # Highly significant

    def _determine_falsification(self, beta_value: float) -> bool:
        """Determine if this trial shows absence of soma-bias (falsification)"""
        return self.no_bias_threshold[0] <= beta_value <= self.no_bias_threshold[1]

    def _calculate_confidence_level(
        self, beta_value: float, match_quality: float, ignition_difference: float
    ) -> float:
        """Calculate confidence level for the trial result"""
        base_confidence = 0.5

        # Higher confidence with better precision matching
        base_confidence += 0.2 * match_quality

        # Higher confidence with clear bias or lack thereof
        deviation_from_unity = abs(beta_value - 1.0)
        if deviation_from_unity < 0.1:  # Close to no bias
            base_confidence += 0.2
        elif deviation_from_unity > 0.5:  # Clear bias
            base_confidence += 0.2

        # Higher confidence with larger ignition differences
        if abs(ignition_difference) > 0.2:
            base_confidence += 0.1

        return min(base_confidence, 1.0)

    def _analyze_results(
        self,
        test_id: str,
        trial_results: List[SomaBiasTrialResult],
        participant_results: Dict[str, List],
        n_trials_per_participant: int,
        n_participants: int,
    ) -> SomaBiasTestResult:
        """Analyze complete soma-bias test results"""
        timestamp = datetime.now()

        # Calculate participant-level β values
        participant_beta_values = {}
        participant_bias_directions = {}

        for participant_id, trials in participant_results.items():
            participant_betas = [t.beta_value for t in trials]
            participant_beta_values[participant_id] = np.mean(participant_betas)

            # Determine predominant bias direction
            bias_directions = [t.bias_direction for t in trials]
            most_common_bias = max(set(bias_directions), key=bias_directions.count)
            participant_bias_directions[participant_id] = most_common_bias

        # Population-level statistics
        all_betas = list(participant_beta_values.values())
        mean_beta = np.mean(all_betas)
        median_beta = np.median(all_betas)
        beta_std = np.std(all_betas)

        # Calculate population confidence interval
        sem = beta_std / np.sqrt(len(all_betas))
        margin_error = 1.96 * sem
        beta_confidence_interval = (mean_beta - margin_error, mean_beta + margin_error)

        # Analyze bias distribution
        intero_bias_participants = sum(
            1 for bias in participant_bias_directions.values() if bias == "intero"
        )
        extero_bias_participants = sum(
            1 for bias in participant_bias_directions.values() if bias == "extero"
        )
        no_bias_participants = sum(
            1 for bias in participant_bias_directions.values() if bias == "none"
        )

        bias_distribution = {
            "intero": intero_bias_participants / n_participants,
            "extero": extero_bias_participants / n_participants,
            "none": no_bias_participants / n_participants,
        }

        # Statistical analysis
        population_p_value = self._calculate_population_p_value(all_betas)
        effect_size = self._calculate_effect_size(all_betas)
        statistical_power = self._calculate_statistical_power(n_participants)

        # Check sample size requirement
        meets_sample_size_requirement = n_participants >= self.minimum_sample_size

        # Determine if framework is falsified
        no_bias_proportion = bias_distribution["none"]
        is_falsified = (
            meets_sample_size_requirement
            and no_bias_proportion > self.falsification_threshold
            and population_p_value < 0.05
        )

        # Generate interpretation
        interpretation = self._generate_interpretation(
            mean_beta,
            no_bias_proportion,
            is_falsified,
            intero_bias_participants,
            extero_bias_participants,
            no_bias_participants,
        )

        return SomaBiasTestResult(
            test_id=test_id,
            n_trials=len(trial_results),
            n_participants=n_participants,
            timestamp=timestamp,
            trial_results=trial_results,
            participant_beta_values=participant_beta_values,
            participant_bias_directions=participant_bias_directions,
            mean_beta=mean_beta,
            median_beta=median_beta,
            beta_std=beta_std,
            beta_confidence_interval=beta_confidence_interval,
            intero_bias_participants=intero_bias_participants,
            extero_bias_participants=extero_bias_participants,
            no_bias_participants=no_bias_participants,
            bias_distribution=bias_distribution,
            population_p_value=population_p_value,
            effect_size=effect_size,
            statistical_power=statistical_power,
            meets_sample_size_requirement=meets_sample_size_requirement,
            is_framework_falsified=is_falsified,
            interpretation=interpretation,
        )

    def _calculate_population_p_value(self, beta_values: List[float]) -> float:
        """Calculate population-level p-value for soma-bias test"""
        # Test against null hypothesis: population mean β = 1 (no bias)
        t_stat, p_value = stats.ttest_1samp(beta_values, 1.0)
        return p_value

    def _calculate_effect_size(self, beta_values: List[float]) -> float:
        """Calculate effect size (Cohen's d) for deviation from β = 1"""
        mean_beta = np.mean(beta_values)
        std_beta = np.std(beta_values)

        if std_beta == 0:
            return 0.0

        # Cohen's d for one-sample test against μ = 1
        cohens_d = abs(mean_beta - 1.0) / std_beta
        return cohens_d

    def _calculate_statistical_power(self, n_participants: int) -> float:
        """Calculate statistical power for detecting soma-bias"""
        # Simplified power calculation based on sample size
        if n_participants < 50:
            return 0.5
        elif n_participants < 100:
            return 0.7
        elif n_participants < 200:
            return 0.85
        else:
            return 0.95

    def _generate_interpretation(
        self,
        mean_beta: float,
        no_bias_proportion: float,
        is_falsified: bool,
        intero_bias_count: int,
        extero_bias_count: int,
        no_bias_count: int,
    ) -> str:
        """Generate interpretation of soma-bias test results"""
        total_participants = intero_bias_count + extero_bias_count + no_bias_count

        if is_falsified:
            return (
                f"FRAMEWORK FALSIFIED: {no_bias_count}/{total_participants} participants "
                f"({no_bias_proportion:.1%}) showed no soma-bias (β ≈ 1.0). "
                f"Population mean β = {mean_beta:.3f}. This contradicts the APGI Framework's "
                f"prediction that interoceptive signals should receive preferential weighting."
            )

        elif no_bias_proportion > 0.3:
            return (
                f"PARTIAL SOMA-BIAS ABSENCE: {no_bias_count}/{total_participants} participants "
                f"({no_bias_proportion:.1%}) showed no soma-bias, but this does not reach "
                f"the falsification threshold. Population mean β = {mean_beta:.3f}. "
                f"Results suggest potential limitations but are not conclusive."
            )

        elif mean_beta > 1.2:
            return (
                f"STRONG INTEROCEPTIVE BIAS: Population mean β = {mean_beta:.3f} with "
                f"{intero_bias_count}/{total_participants} participants showing interoceptive bias. "
                f"Results strongly support the APGI Framework's prediction of soma-bias."
            )

        elif mean_beta < 0.8:
            return (
                f"UNEXPECTED EXTEROCEPTIVE BIAS: Population mean β = {mean_beta:.3f} with "
                f"{extero_bias_count}/{total_participants} participants showing exteroceptive bias. "
                f"This suggests the opposite of predicted soma-bias and warrants investigation."
            )

        else:
            return (
                f"MODERATE SOMA-BIAS: Population mean β = {mean_beta:.3f} with mixed bias patterns. "
                f"Intero bias: {intero_bias_count}, Extero bias: {extero_bias_count}, "
                f"No bias: {no_bias_count}. Results provide moderate support for soma-bias prediction."
            )

    def calculate_required_sample_size(
        self, effect_size: float = 0.3, power: float = 0.8, alpha: float = 0.05
    ) -> int:
        """
        Calculate required sample size for detecting soma-bias.

        Args:
            effect_size: Expected Cohen's d
            power: Desired statistical power
            alpha: Type I error rate

        Returns:
            Required sample size
        """
        # Simplified sample size calculation
        # In practice, would use power analysis formulas

        if effect_size <= 0.2:  # Small effect
            base_n = 200
        elif effect_size <= 0.5:  # Medium effect
            base_n = 100
        else:  # Large effect
            base_n = 50

        # Adjust for power and alpha
        power_adjustment = (0.8 / power) ** 2
        alpha_adjustment = (alpha / 0.05) ** 0.5

        required_n = int(base_n * power_adjustment * alpha_adjustment)

        # Ensure minimum sample size requirement
        return max(required_n, self.minimum_sample_size)

    def validate_precision_matching(
        self, extero_precision: float, intero_precision: float, tolerance: float = 0.1
    ) -> Tuple[bool, float]:
        """
        Validate that precision values are adequately matched.

        Args:
            extero_precision: Exteroceptive precision
            intero_precision: Interoceptive precision
            tolerance: Maximum acceptable relative difference

        Returns:
            Tuple of (is_matched, match_quality)
        """
        if extero_precision <= 0 or intero_precision <= 0:
            return False, 0.0

        relative_difference = abs(extero_precision - intero_precision) / max(
            extero_precision, intero_precision
        )
        match_quality = 1.0 - relative_difference

        is_matched = relative_difference <= tolerance

        return is_matched, match_quality

    def simulate_individual_differences(
        self, n_participants: int
    ) -> Dict[str, Dict[str, float]]:
        """
        Simulate individual differences in soma-bias.

        Args:
            n_participants: Number of participants to simulate

        Returns:
            Dictionary of participant characteristics
        """
        participants = {}

        for i in range(n_participants):
            participant_id = f"P{i:03d}"

            # Simulate individual bias tendencies
            base_bias = np.random.normal(1.2, 0.3)  # Slight intero bias on average
            base_bias = np.clip(base_bias, 0.5, 2.5)

            # Simulate individual variability
            trial_variability = np.random.uniform(0.1, 0.3)

            # Simulate interoceptive sensitivity
            intero_sensitivity = np.random.uniform(0.7, 1.3)

            # Simulate exteroceptive sensitivity
            extero_sensitivity = np.random.uniform(0.8, 1.2)

            participants[participant_id] = {
                "base_bias": base_bias,
                "trial_variability": trial_variability,
                "intero_sensitivity": intero_sensitivity,
                "extero_sensitivity": extero_sensitivity,
            }

        return participants

    def run_test(self, parameters: Optional[Dict] = None) -> SomaBiasTestResult:
        """
        Execute the soma-bias test with given parameters.

        Args:
            parameters: Optional dictionary of test parameters
                - n_trials: Number of trials to run (default: 200)
                - n_participants: Number of participants (default: 30)
                - confidence_threshold: Threshold for falsification confidence (default: 0.8)
                - precision_matching_tolerance: Tolerance for precision matching (default: 0.1)

        Returns:
            SomaBiasTestResult: Complete test results with analysis
        """
        if parameters is None:
            parameters = {}

        # Extract parameters with defaults
        n_trials = parameters.get("n_trials", 200)
        n_participants = parameters.get("n_participants", 30)
        confidence_threshold = parameters.get("confidence_threshold", 0.8)
        precision_tolerance = parameters.get("precision_matching_tolerance", 0.1)

        logger.info(
            f"Starting Soma-Bias Test: {n_trials} trials, {n_participants} participants"
        )

        # Generate test ID
        test_id = f"soma_bias_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Generate participant profiles
        participants = self._generate_participant_profiles(n_participants)

        # Run trials
        trial_results = []
        for trial_idx in range(n_trials):
            participant_id = f"participant_{(trial_idx % n_participants) + 1:02d}"
            participant_profile = participants[participant_id]

            try:
                trial_result = self._run_single_trial(
                    trial_id=f"{test_id}_trial_{trial_idx:03d}",
                    participant_id=participant_id,
                    participant_profile=participant_profile,
                    precision_tolerance=precision_tolerance,
                    confidence_threshold=confidence_threshold,
                )
                trial_results.append(trial_result)

                if trial_idx % 20 == 0:
                    logger.info(f"Completed {trial_idx}/{n_trials} trials")

            except Exception as e:
                logger.error(f"Trial {trial_idx} failed: {e}")
                # Continue with other trials

        # Analyze results
        result = self._analyze_results(test_id, trial_results, n_trials, n_participants)

        logger.info(
            f"Test completed: mean β = {result.mean_beta:.3f}, "
            f"falsified = {result.is_framework_falsified}"
        )

        return result
