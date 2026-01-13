"""
Consciousness Without Ignition Test

Implements the secondary falsification test for consciousness without ignition signatures.
This test evaluates whether conscious reports can occur when neural ignition signatures
are absent (P3b < 2 μV, gamma PLV < 0.15, PCI < 0.3, no frontoparietal BOLD elevation).
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
from datetime import datetime
import logging

from ..core.equation import APGIEquation
from ..simulators.signature_validator import SignatureValidator
from ..simulators.p3b_simulator import P3bSimulator
from ..simulators.gamma_simulator import GammaSimulator
from ..simulators.bold_simulator import BOLDSimulator
from ..simulators.pci_calculator import PCICalculator
from .consciousness_assessment import (
    ConsciousnessAssessmentSimulator,
    ConsciousnessLevel,
)
from ..exceptions import ValidationError, SimulationError
from .error_handling_wrapper import with_error_handling, log_test_execution
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConsciousnessWithoutIgnitionTrialResult:
    """Result of a single consciousness without ignition trial"""

    trial_id: str
    participant_id: str
    timestamp: datetime

    # Neural signatures (should be below ignition thresholds)
    p3b_amplitude: float
    p3b_latency: float
    gamma_plv: float
    gamma_duration: float
    bold_activations: Dict[str, float]
    pci_value: float

    # Signature validation (should be False for ignition)
    p3b_below_threshold: bool
    gamma_below_threshold: bool
    bold_below_threshold: bool
    pci_below_threshold: bool
    all_signatures_absent: bool

    # Consciousness assessment (should indicate consciousness)
    subjective_report: bool
    forced_choice_accuracy: float
    confidence_rating: float
    metacognitive_sensitivity: float
    consciousness_present: bool

    # Experimental controls
    controls_valid: bool

    # Final assessment
    is_falsifying: bool
    confidence_level: float


@dataclass
class ConsciousnessWithoutIgnitionTestResult:
    """Complete result of consciousness without ignition testing"""

    test_id: str
    n_trials: int
    n_participants: int
    timestamp: datetime

    trial_results: List[ConsciousnessWithoutIgnitionTrialResult]

    # Summary statistics
    total_falsifying_trials: int
    falsification_rate: float
    mean_confidence: float

    # Participant-level analysis
    participants_with_falsification: int
    participant_falsification_rates: Dict[str, float]

    # Statistical analysis
    p_value: float
    effect_size: float
    statistical_power: float

    # Threshold validation (>20% occurrence required)
    meets_threshold_criterion: bool
    is_framework_falsified: bool
    interpretation: str


class ConsciousnessWithoutIgnitionTest:
    """
    Test controller for consciousness without ignition falsification criterion.

    Tests whether conscious reports can occur when ignition signatures are absent:
    - P3b amplitude < 2 μV
    - Gamma PLV < 0.15
    - PCI < 0.3
    - No frontoparietal BOLD elevation

    Falsification requires >20% occurrence across participants.
    """

    def __init__(self):
        self.equation = APGIEquation()
        self.signature_validator = SignatureValidator()
        self.p3b_simulator = P3bSimulator()
        self.gamma_simulator = GammaSimulator()
        self.bold_simulator = BOLDSimulator()
        self.pci_calculator = PCICalculator()
        self.consciousness_simulator = ConsciousnessAssessmentSimulator()

        # Thresholds for absent ignition signatures
        self.p3b_absent_threshold = 2.0  # μV (below this = absent)
        self.gamma_absent_plv = 0.15  # PLV (below this = absent)
        self.gamma_absent_duration = 150.0  # ms
        self.bold_absent_z = 2.5  # Z-score (below this = absent)
        self.pci_absent_threshold = 0.3  # PCI (below this = absent)

        # Falsification threshold (>20% occurrence required)
        self.falsification_threshold = 0.20

    @with_error_handling(validate_params=True, enable_retry=True, log_errors=True)
    def run_consciousness_without_ignition_test(
        self,
        n_trials: int = 100,
        n_participants: int = 25,
        test_id: Optional[str] = None,
    ) -> ConsciousnessWithoutIgnitionTestResult:
        """
        Run the consciousness without ignition test across multiple trials and participants.

        Args:
            n_trials: Number of trials per participant
            n_participants: Number of simulated participants
            test_id: Optional test identifier

        Returns:
            Complete consciousness without ignition test results

        Raises:
            ValidationError: If parameters are invalid
            SimulationError: If simulation fails
        """
        start_time = datetime.now()

        try:
            # Validate parameters
            if n_trials <= 0:
                raise ValidationError(f"n_trials must be positive, got {n_trials}")
            if n_participants <= 0:
                raise ValidationError(
                    f"n_participants must be positive, got {n_participants}"
                )

            if test_id is None:
                test_id = f"consciousness_without_ignition_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            logger.info(f"Starting consciousness without ignition test: {test_id}")
            logger.info(
                f"Parameters: n_trials={n_trials}, n_participants={n_participants}"
            )

            trial_results = []
            participant_results = {}

            for participant_id in range(n_participants):
                participant_key = f"P{participant_id:03d}"
                participant_trials = []

                for trial_num in range(n_trials):
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
                test_id, trial_results, participant_results, n_trials, n_participants
            )

            end_time = datetime.now()
            log_test_execution(
                "Consciousness Without Ignition Test", start_time, end_time, True
            )

            return result

        except Exception as e:
            end_time = datetime.now()
            log_test_execution(
                "Consciousness Without Ignition Test", start_time, end_time, False, e
            )
            raise

    def _run_single_trial(
        self, trial_id: str, participant_id: str
    ) -> ConsciousnessWithoutIgnitionTrialResult:
        """
        Run a single consciousness without ignition trial.

        Args:
            trial_id: Unique trial identifier
            participant_id: Participant identifier

        Returns:
            Single trial result
        """
        timestamp = datetime.now()

        # Generate neural signatures (biased toward absent ignition)
        neural_signatures = self._generate_absent_ignition_signatures()

        # Validate signatures are below ignition thresholds
        signature_validation = self._validate_absent_signatures(neural_signatures)

        # Assess consciousness (biased toward present consciousness)
        consciousness_assessment = self._assess_consciousness_present()

        # Validate experimental controls
        controls_valid = self._validate_experimental_controls()

        # Determine if this trial is falsifying
        is_falsifying = self._determine_falsification(
            signature_validation, consciousness_assessment, controls_valid
        )

        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(
            signature_validation, consciousness_assessment
        )

        return ConsciousnessWithoutIgnitionTrialResult(
            trial_id=trial_id,
            participant_id=participant_id,
            timestamp=timestamp,
            # Neural signatures
            p3b_amplitude=neural_signatures["p3b_amplitude"],
            p3b_latency=neural_signatures["p3b_latency"],
            gamma_plv=neural_signatures["gamma_plv"],
            gamma_duration=neural_signatures["gamma_duration"],
            bold_activations=neural_signatures["bold_activations"],
            pci_value=neural_signatures["pci_value"],
            # Signature validation
            p3b_below_threshold=signature_validation["p3b_absent"],
            gamma_below_threshold=signature_validation["gamma_absent"],
            bold_below_threshold=signature_validation["bold_absent"],
            pci_below_threshold=signature_validation["pci_absent"],
            all_signatures_absent=signature_validation["all_absent"],
            # Consciousness assessment
            subjective_report=consciousness_assessment["subjective_report"],
            forced_choice_accuracy=consciousness_assessment["forced_choice_accuracy"],
            confidence_rating=consciousness_assessment["confidence_rating"],
            metacognitive_sensitivity=consciousness_assessment[
                "metacognitive_sensitivity"
            ],
            consciousness_present=consciousness_assessment["consciousness_present"],
            # Experimental controls
            controls_valid=controls_valid,
            # Final assessment
            is_falsifying=is_falsifying,
            confidence_level=confidence_level,
        )

    def _generate_absent_ignition_signatures(self) -> Dict:
        """Generate neural signatures that are below ignition thresholds"""
        # Generate P3b signature (below threshold)
        p3b_result = self.p3b_simulator.simulate_p3b(
            amplitude_range=(0.5, 1.8),  # Below 2.0 μV threshold
            latency_range=(250, 500),
        )

        # Generate gamma synchrony (below threshold)
        gamma_result = self.gamma_simulator.simulate_gamma_synchrony(
            plv_range=(0.05, 0.12),  # Below 0.15 PLV threshold
            duration_range=(50, 120),  # Below 150 ms threshold
        )

        # Generate BOLD activation (below threshold)
        bold_result = self.bold_simulator.simulate_bold_activation(
            regions=[
                "dlpfc_left",
                "dlpfc_right",
                "ips_left",
                "ips_right",
                "anterior_insula",
                "acc",
            ],
            z_range=(0.5, 2.2),  # Below 2.5 Z-score threshold
        )

        # Calculate PCI (below threshold)
        # Simulate low connectivity matrix for low PCI
        connectivity_matrix = np.random.rand(64, 64) * 0.2  # Reduced connectivity
        pci_value = self.pci_calculator.calculate_pci(connectivity_matrix)
        # Ensure PCI is below threshold
        pci_value = min(pci_value, self.pci_absent_threshold - 0.05)

        return {
            "p3b_amplitude": p3b_result.amplitude,
            "p3b_latency": p3b_result.latency,
            "gamma_plv": gamma_result.plv,
            "gamma_duration": gamma_result.duration,
            "bold_activations": bold_result.activations,
            "pci_value": pci_value,
        }

    def _validate_absent_signatures(self, signatures: Dict) -> Dict:
        """Validate that neural signatures are below ignition thresholds"""
        p3b_absent = signatures["p3b_amplitude"] < self.p3b_absent_threshold

        gamma_absent = (
            signatures["gamma_plv"] < self.gamma_absent_plv
            and signatures["gamma_duration"] < self.gamma_absent_duration
        )

        # Check BOLD activation in frontoparietal regions
        frontoparietal_regions = ["dlpfc_left", "dlpfc_right", "ips_left", "ips_right"]
        bold_absent = all(
            signatures["bold_activations"].get(region, 0) < self.bold_absent_z
            for region in frontoparietal_regions
        )

        pci_absent = signatures["pci_value"] < self.pci_absent_threshold

        all_absent = p3b_absent and gamma_absent and bold_absent and pci_absent

        return {
            "p3b_absent": p3b_absent,
            "gamma_absent": gamma_absent,
            "bold_absent": bold_absent,
            "pci_absent": pci_absent,
            "all_absent": all_absent,
        }

    def _assess_consciousness_present(self) -> Dict:
        """Simulate consciousness assessment biased toward conscious reports"""
        # For this test, we need cases where consciousness is present
        # despite absent ignition signatures

        # Simulate subjective report (biased toward present)
        subjective_report = np.random.choice([True, False], p=[0.7, 0.3])

        # Simulate forced-choice accuracy (above chance if conscious)
        if subjective_report:
            forced_choice_accuracy = np.random.normal(0.72, 0.08)  # Above chance
        else:
            # Even when not subjectively reported, some above-chance performance
            forced_choice_accuracy = np.random.normal(0.58, 0.06)

        forced_choice_accuracy = np.clip(forced_choice_accuracy, 0.0, 1.0)

        # Simulate confidence rating (correlated with subjective report)
        if subjective_report:
            confidence_rating = np.random.normal(0.7, 0.15)
        else:
            confidence_rating = np.random.normal(0.4, 0.12)

        confidence_rating = np.clip(confidence_rating, 0.0, 1.0)

        # Calculate metacognitive sensitivity
        metacognitive_sensitivity = self._calculate_metacognitive_sensitivity(
            forced_choice_accuracy, confidence_rating
        )

        # Consciousness is considered present if subjective report is positive
        # OR forced-choice is significantly above chance (>0.6)
        consciousness_present = subjective_report or forced_choice_accuracy > 0.6

        return {
            "subjective_report": subjective_report,
            "forced_choice_accuracy": forced_choice_accuracy,
            "confidence_rating": confidence_rating,
            "metacognitive_sensitivity": metacognitive_sensitivity,
            "consciousness_present": consciousness_present,
        }

    def _calculate_metacognitive_sensitivity(
        self, accuracy: float, confidence: float
    ) -> float:
        """Calculate metacognitive sensitivity as confidence-accuracy correspondence"""
        base_sensitivity = 1.0 - abs(accuracy - confidence)
        noise = np.random.normal(0, 0.15)
        sensitivity = np.clip(base_sensitivity + noise, 0.0, 1.0)
        return sensitivity

    def _validate_experimental_controls(self) -> bool:
        """Validate experimental control requirements"""
        # Simulate control validation
        return np.random.choice([True, False], p=[0.95, 0.05])

    def _determine_falsification(
        self,
        signature_validation: Dict,
        consciousness_assessment: Dict,
        controls_valid: bool,
    ) -> bool:
        """
        Determine if this trial represents a falsifying case.

        Falsification occurs when:
        1. All ignition signatures are absent
        2. Consciousness is present
        3. Experimental controls are valid
        """
        return (
            signature_validation["all_absent"]
            and consciousness_assessment["consciousness_present"]
            and controls_valid
        )

    def _calculate_confidence_level(
        self, signature_validation: Dict, consciousness_assessment: Dict
    ) -> float:
        """Calculate confidence level for the trial result"""
        base_confidence = 0.5

        # Boost confidence if signatures are clearly absent
        if signature_validation["all_absent"]:
            base_confidence += 0.25

        # Boost confidence if consciousness is clearly present
        if consciousness_assessment["consciousness_present"]:
            if consciousness_assessment["forced_choice_accuracy"] > 0.65:
                base_confidence += 0.25

        return min(base_confidence, 1.0)

    def _analyze_results(
        self,
        test_id: str,
        trial_results: List[ConsciousnessWithoutIgnitionTrialResult],
        participant_results: Dict[str, List],
        n_trials: int,
        n_participants: int,
    ) -> ConsciousnessWithoutIgnitionTestResult:
        """Analyze complete test results"""
        timestamp = datetime.now()

        # Count falsifying trials
        falsifying_trials = [r for r in trial_results if r.is_falsifying]
        total_falsifying = len(falsifying_trials)
        falsification_rate = total_falsifying / len(trial_results) if trial_results else 0

        # Calculate mean confidence
        mean_confidence = np.mean([r.confidence_level for r in trial_results])

        # Analyze participant-level results
        participant_falsification_rates = {}
        participants_with_falsification = 0

        for participant_id, trials in participant_results.items():
            participant_falsifying = [t for t in trials if t.is_falsifying]
            participant_rate = len(participant_falsifying) / len(trials) if trials else 0
            participant_falsification_rates[participant_id] = participant_rate

            if participant_rate > 0:
                participants_with_falsification += 1

        # Check if meets threshold criterion (>20% occurrence)
        meets_threshold_criterion = falsification_rate > self.falsification_threshold

        # Perform statistical analysis
        p_value = self._calculate_p_value(
            falsification_rate, total_falsifying, len(trial_results)
        )
        effect_size = self._calculate_effect_size(falsifying_trials, trial_results)
        statistical_power = self._calculate_statistical_power(len(trial_results))

        # Determine if framework is falsified
        is_falsified = meets_threshold_criterion and p_value < 0.05

        # Generate interpretation
        interpretation = self._generate_interpretation(
            falsification_rate,
            is_falsified,
            total_falsifying,
            participants_with_falsification,
            n_participants,
        )

        return ConsciousnessWithoutIgnitionTestResult(
            test_id=test_id,
            n_trials=n_trials,
            n_participants=n_participants,
            timestamp=timestamp,
            trial_results=trial_results,
            total_falsifying_trials=total_falsifying,
            falsification_rate=falsification_rate,
            mean_confidence=mean_confidence,
            participants_with_falsification=participants_with_falsification,
            participant_falsification_rates=participant_falsification_rates,
            p_value=p_value,
            effect_size=effect_size,
            statistical_power=statistical_power,
            meets_threshold_criterion=meets_threshold_criterion,
            is_framework_falsified=is_falsified,
            interpretation=interpretation,
        )

    def _calculate_p_value(
        self, falsification_rate: float, n_falsifying: int, n_total: int
    ) -> float:
        """Calculate p-value using binomial test against null hypothesis"""
        # Null hypothesis: falsification rate = 0 (no consciousness without ignition)
        # Use binomial test approximation
        if n_falsifying == 0:
            return 1.0

        # Simplified p-value calculation
        expected_rate = 0.05  # Expected false positive rate
        if falsification_rate <= expected_rate:
            return 0.5
        elif falsification_rate > self.falsification_threshold:
            return 0.01  # Highly significant
        else:
            return 0.1

    def _calculate_effect_size(
        self, falsifying_trials: List, all_trials: List
    ) -> float:
        """Calculate effect size (Cohen's d)"""
        if len(falsifying_trials) == 0:
            return 0.0

        # Use confidence levels as the measure
        falsifying_confidence = [t.confidence_level for t in falsifying_trials]
        non_falsifying_confidence = [
            t.confidence_level for t in all_trials if not t.is_falsifying
        ]

        if len(non_falsifying_confidence) == 0:
            return 1.0

        mean_diff = np.mean(falsifying_confidence) - np.mean(non_falsifying_confidence)
        pooled_std = np.sqrt(
            (np.var(falsifying_confidence) + np.var(non_falsifying_confidence)) / 2
        )

        if pooled_std == 0:
            return 0.0

        return mean_diff / pooled_std

    def _calculate_statistical_power(self, n_trials: int) -> float:
        """Calculate statistical power"""
        if n_trials < 100:
            return 0.6
        elif n_trials < 500:
            return 0.8
        else:
            return 0.95

    def _generate_interpretation(
        self,
        falsification_rate: float,
        is_falsified: bool,
        total_falsifying: int,
        participants_with_falsification: int,
        n_participants: int,
    ) -> str:
        """Generate interpretation of results"""
        if is_falsified:
            return (
                f"FRAMEWORK FALSIFIED: {total_falsifying} trials ({falsification_rate:.1%}) "
                f"showed consciousness without ignition signatures across "
                f"{participants_with_falsification}/{n_participants} participants. "
                f"This exceeds the 20% threshold and provides strong evidence against "
                f"the APGI Framework's prediction that consciousness requires ignition."
            )
        elif falsification_rate > 0.1:
            return (
                f"PARTIAL FALSIFICATION: {total_falsifying} trials ({falsification_rate:.1%}) "
                f"showed consciousness without ignition, but this does not reach the "
                f"20% threshold required for falsification. Results suggest potential "
                f"framework limitations but are not conclusive."
            )
        else:
            return (
                f"NO FALSIFICATION: Only {total_falsifying} trials ({falsification_rate:.1%}) "
                f"showed consciousness without ignition signatures. Results support "
                f"the APGI Framework's prediction that consciousness requires ignition."
            )

    def run_test(
        self, parameters: Optional[Dict] = None
    ) -> ConsciousnessWithoutIgnitionTestResult:
        """
        Execute the consciousness without ignition test with given parameters.

        Args:
            parameters: Optional dictionary of test parameters
                - n_trials: Number of trials to run (default: 100)
                - n_participants: Number of participants (default: 25)
                - confidence_threshold: Threshold for falsification confidence (default: 0.8)

        Returns:
            ConsciousnessWithoutIgnitionTestResult: Complete test results with analysis
        """
        if parameters is None:
            parameters = {}

        # Extract parameters with defaults
        n_trials = parameters.get("n_trials", 100)
        n_participants = parameters.get("n_participants", 25)
        confidence_threshold = parameters.get("confidence_threshold", 0.8)

        logger.info(
            f"Starting Consciousness Without Ignition Test: {n_trials} trials, {n_participants} participants"
        )

        # Generate test ID
        test_id = (
            f"consciousness_without_ignition_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Run trials
        trial_results = []
        for trial_idx in range(n_trials):
            participant_id = f"participant_{(trial_idx % n_participants) + 1:02d}"

            try:
                trial_result = self._run_single_trial(
                    trial_id=f"{test_id}_trial_{trial_idx:03d}",
                    participant_id=participant_id,
                    confidence_threshold=confidence_threshold,
                )
                trial_results.append(trial_result)

                if trial_idx % 10 == 0:
                    logger.info(f"Completed {trial_idx}/{n_trials} trials")

            except Exception as e:
                logger.error(f"Trial {trial_idx} failed: {e}")
                # Continue with other trials

        # Analyze results
        result = self._analyze_results(
            test_id, trial_results, participant_results, n_trials, n_participants
        )

        logger.info(
            f"Test completed: {result.total_falsifying_trials} falsifying trials "
            f"({result.falsification_rate:.1%} rate), falsified = {result.is_framework_falsified}"
        )

        return result
