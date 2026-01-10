"""
Primary Falsification Test Controller

Implements the primary falsification test for the APGI Framework, testing whether
full ignition signatures can occur without consciousness.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime

from ..core.equation import APGIEquation
from ..simulators.signature_validator import SignatureValidator
from ..simulators.p3b_simulator import P3bSimulator
from ..simulators.gamma_simulator import GammaSimulator
from ..simulators.bold_simulator import BOLDSimulator
from ..simulators.pci_calculator import PCICalculator
from ..exceptions import ValidationError, SimulationError
from .error_handling_wrapper import with_error_handling, log_test_execution
import logging

logger = logging.getLogger(__name__)


@dataclass
class FalsificationTrialResult:
    """Result of a single falsification trial"""

    trial_id: str
    participant_id: str
    timestamp: datetime

    # Neural signatures
    p3b_amplitude: float
    p3b_latency: float
    gamma_plv: float
    gamma_duration: float
    bold_activations: Dict[str, float]
    pci_value: float

    # Signature validation
    p3b_threshold_met: bool
    gamma_threshold_met: bool
    bold_threshold_met: bool
    pci_threshold_met: bool
    all_signatures_present: bool

    # Consciousness assessment
    subjective_report: bool
    forced_choice_accuracy: float
    consciousness_absent: bool

    # AI/ACC validation
    ai_acc_activation_absent: bool
    gamma_coherence_low: bool

    # Experimental controls
    controls_valid: bool

    # Final assessment
    is_falsifying: bool
    confidence_level: float


@dataclass
class FalsificationTestResult:
    """Complete result of primary falsification testing"""

    test_id: str
    n_trials: int
    n_participants: int
    timestamp: datetime

    trial_results: List[FalsificationTrialResult]

    # Summary statistics
    total_falsifying_trials: int
    falsification_rate: float
    mean_confidence: float

    # Statistical analysis
    p_value: float
    effect_size: float
    statistical_power: float

    is_framework_falsified: bool
    interpretation: str


class PrimaryFalsificationTest:
    """
    Primary falsification test controller for the APGI Framework.

    Tests the primary falsification criterion: whether full ignition signatures
    (P3b, gamma synchrony, BOLD activation, PCI) can occur without consciousness.
    """

    def __init__(self):
        self.equation = APGIEquation()
        self.signature_validator = SignatureValidator()
        self.p3b_simulator = P3bSimulator()
        self.gamma_simulator = GammaSimulator()
        self.bold_simulator = BOLDSimulator()
        self.pci_calculator = PCICalculator()

        # Thresholds for ignition signatures
        self.p3b_threshold = 5.0  # μV at Pz electrode
        self.gamma_plv_threshold = 0.3  # Phase-locking value
        self.gamma_duration_threshold = 200  # ms
        self.bold_z_threshold = 3.1  # Z-score
        self.pci_threshold = 0.4  # Perturbational Complexity Index

        # AI/ACC validation thresholds
        self.ai_acc_gamma_threshold = 0.25  # PLV threshold for AI/ACC

    @with_error_handling(validate_params=True, enable_retry=True, log_errors=True)
    def run_falsification_test(
        self,
        n_trials: int = 100,
        n_participants: int = 20,
        test_id: Optional[str] = None,
    ) -> FalsificationTestResult:
        """
        Run the primary falsification test across multiple trials and participants.

        Args:
            n_trials: Number of trials per participant
            n_participants: Number of simulated participants
            test_id: Optional test identifier

        Returns:
            Complete falsification test results

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
                test_id = (
                    f"primary_falsification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

            logger.info(f"Starting primary falsification test: {test_id}")
            logger.info(
                f"Parameters: n_trials={n_trials}, n_participants={n_participants}"
            )

            trial_results = []

            for participant_id in range(n_participants):
                for trial_num in range(n_trials):
                    trial_id = f"{test_id}_p{participant_id:03d}_t{trial_num:03d}"

                    try:
                        trial_result = self._run_single_trial(
                            trial_id=trial_id, participant_id=f"P{participant_id:03d}"
                        )
                        trial_results.append(trial_result)
                    except Exception as e:
                        logger.error(f"Trial {trial_id} failed: {str(e)}")
                        # Continue with other trials
                        continue

            if not trial_results:
                raise SimulationError("All trials failed - no results to analyze")

            # Analyze results
            result = self._analyze_results(
                test_id, trial_results, n_trials, n_participants
            )

            end_time = datetime.now()
            log_test_execution("Primary Falsification Test", start_time, end_time, True)

            return result

        except Exception as e:
            end_time = datetime.now()
            log_test_execution(
                "Primary Falsification Test", start_time, end_time, False, e
            )
            raise

    def _run_single_trial(
        self, trial_id: str, participant_id: str
    ) -> FalsificationTrialResult:
        """
        Run a single falsification trial.

        Args:
            trial_id: Unique trial identifier
            participant_id: Participant identifier

        Returns:
            Single trial result
        """
        timestamp = datetime.now()

        # Generate neural signatures
        neural_signatures = self._generate_neural_signatures()

        # Validate signatures against thresholds
        signature_validation = self._validate_signatures(neural_signatures)

        # Assess consciousness (simulated)
        consciousness_assessment = self._assess_consciousness()

        # Validate AI/ACC engagement
        ai_acc_validation = self._validate_ai_acc_engagement(neural_signatures)

        # Validate experimental controls
        controls_valid = self._validate_experimental_controls()

        # Determine if this trial is falsifying
        is_falsifying = self._determine_falsification(
            signature_validation,
            consciousness_assessment,
            ai_acc_validation,
            controls_valid,
        )

        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(
            signature_validation, consciousness_assessment
        )

        return FalsificationTrialResult(
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
            p3b_threshold_met=signature_validation["p3b_met"],
            gamma_threshold_met=signature_validation["gamma_met"],
            bold_threshold_met=signature_validation["bold_met"],
            pci_threshold_met=signature_validation["pci_met"],
            all_signatures_present=signature_validation["all_present"],
            # Consciousness assessment
            subjective_report=consciousness_assessment["subjective_report"],
            forced_choice_accuracy=consciousness_assessment["forced_choice_accuracy"],
            consciousness_absent=consciousness_assessment["consciousness_absent"],
            # AI/ACC validation
            ai_acc_activation_absent=ai_acc_validation["activation_absent"],
            gamma_coherence_low=ai_acc_validation["coherence_low"],
            # Experimental controls
            controls_valid=controls_valid,
            # Final assessment
            is_falsifying=is_falsifying,
            confidence_level=confidence_level,
        )

    def _generate_neural_signatures(self) -> Dict:
        """Generate neural signatures for the trial"""
        # Generate P3b signature
        p3b_result = self.p3b_simulator.simulate_p3b(
            amplitude_range=(4.0, 8.0), latency_range=(250, 500)  # Around threshold
        )

        # Generate gamma synchrony
        gamma_result = self.gamma_simulator.simulate_gamma_synchrony(
            plv_range=(0.25, 0.4), duration_range=(150, 300)  # Around threshold
        )

        # Generate BOLD activation
        bold_result = self.bold_simulator.simulate_bold_activation(
            regions=[
                "dlpfc_left",
                "dlpfc_right",
                "ips_left",
                "ips_right",
                "anterior_insula",
                "acc",
            ],
            z_range=(2.5, 4.0),  # Around threshold
        )

        # Calculate PCI
        # Simulate connectivity matrix for PCI calculation
        connectivity_matrix = np.random.rand(64, 64) * 0.5
        pci_value = self.pci_calculator.calculate_pci(connectivity_matrix)

        return {
            "p3b_amplitude": p3b_result.amplitude,
            "p3b_latency": p3b_result.latency,
            "gamma_plv": gamma_result.plv,
            "gamma_duration": gamma_result.duration,
            "bold_activations": bold_result.activations,
            "pci_value": pci_value,
        }

    def _validate_signatures(self, signatures: Dict) -> Dict:
        """Validate neural signatures against thresholds"""
        p3b_met = signatures["p3b_amplitude"] > self.p3b_threshold

        gamma_met = (
            signatures["gamma_plv"] > self.gamma_plv_threshold
            and signatures["gamma_duration"] > self.gamma_duration_threshold
        )

        # Check BOLD activation in key regions
        key_regions = [
            "dlpfc_left",
            "dlpfc_right",
            "ips_left",
            "ips_right",
            "anterior_insula",
        ]
        bold_met = all(
            signatures["bold_activations"].get(region, 0) > self.bold_z_threshold
            for region in key_regions
        )

        pci_met = signatures["pci_value"] > self.pci_threshold

        all_present = p3b_met and gamma_met and bold_met and pci_met

        return {
            "p3b_met": p3b_met,
            "gamma_met": gamma_met,
            "bold_met": bold_met,
            "pci_met": pci_met,
            "all_present": all_present,
        }

    def _assess_consciousness(self) -> Dict:
        """Simulate consciousness assessment"""
        # For falsification testing, we need cases where consciousness is absent
        # despite full ignition signatures

        # Simulate subjective report (binary)
        subjective_report = np.random.choice(
            [True, False], p=[0.3, 0.7]
        )  # Bias toward absent

        # Simulate forced-choice accuracy (should be at chance level for absent consciousness)
        if subjective_report:
            forced_choice_accuracy = np.random.normal(
                0.75, 0.1
            )  # Above chance if conscious
        else:
            forced_choice_accuracy = np.random.normal(
                0.5, 0.05
            )  # At chance if unconscious

        forced_choice_accuracy = np.clip(forced_choice_accuracy, 0.0, 1.0)

        # Consciousness is considered absent if both subjective report is negative
        # and forced-choice is at chance level (≤ 0.55)
        consciousness_absent = not subjective_report and forced_choice_accuracy <= 0.55

        return {
            "subjective_report": subjective_report,
            "forced_choice_accuracy": forced_choice_accuracy,
            "consciousness_absent": consciousness_absent,
        }

    def _validate_ai_acc_engagement(self, signatures: Dict) -> Dict:
        """Validate AI/ACC engagement criteria"""
        # Check for absence of significant AI/ACC BOLD activation
        ai_acc_activation = signatures["bold_activations"].get("acc", 0)
        activation_absent = ai_acc_activation <= self.bold_z_threshold

        # Check for low gamma coherence in AI/ACC regions
        # Simulate AI/ACC gamma coherence (should be ≤ 0.25 for falsification)
        ai_acc_gamma_coherence = np.random.uniform(0.1, 0.3)
        coherence_low = ai_acc_gamma_coherence <= self.ai_acc_gamma_threshold

        return {
            "activation_absent": activation_absent,
            "coherence_low": coherence_low,
            "ai_acc_gamma_coherence": ai_acc_gamma_coherence,
        }

    def _validate_experimental_controls(self) -> bool:
        """Validate experimental control requirements"""
        # Simulate control validation (motor/verbal systems intact, etc.)
        # In a real implementation, this would check actual control measures
        return np.random.choice([True, False], p=[0.95, 0.05])  # Usually valid

    def _determine_falsification(
        self,
        signature_validation: Dict,
        consciousness_assessment: Dict,
        ai_acc_validation: Dict,
        controls_valid: bool,
    ) -> bool:
        """
        Determine if this trial represents a falsifying case.

        Falsification occurs when:
        1. All ignition signatures are present
        2. Consciousness is absent
        3. AI/ACC engagement criteria are met
        4. Experimental controls are valid
        """
        return (
            signature_validation["all_present"]
            and consciousness_assessment["consciousness_absent"]
            and ai_acc_validation["activation_absent"]
            and ai_acc_validation["coherence_low"]
            and controls_valid
        )

    def _calculate_confidence_level(
        self, signature_validation: Dict, consciousness_assessment: Dict
    ) -> float:
        """Calculate confidence level for the trial result"""
        # Higher confidence when signatures are clearly above/below thresholds
        # and consciousness assessment is unambiguous

        base_confidence = 0.5

        # Boost confidence if all signatures are clearly present or absent
        if signature_validation["all_present"]:
            base_confidence += 0.3

        # Boost confidence if consciousness assessment is unambiguous
        if consciousness_assessment["consciousness_absent"]:
            if consciousness_assessment["forced_choice_accuracy"] <= 0.52:
                base_confidence += 0.2  # Very close to chance

        return min(base_confidence, 1.0)

    def _analyze_results(
        self,
        test_id: str,
        trial_results: List[FalsificationTrialResult],
        n_trials: int,
        n_participants: int,
    ) -> FalsificationTestResult:
        """Analyze complete test results"""
        timestamp = datetime.now()

        # Count falsifying trials
        falsifying_trials = [r for r in trial_results if r.is_falsifying]
        total_falsifying = len(falsifying_trials)
        falsification_rate = total_falsifying / len(trial_results)

        # Calculate mean confidence
        mean_confidence = np.mean([r.confidence_level for r in trial_results])

        # Perform statistical analysis (simplified)
        # In a real implementation, this would use proper statistical tests
        p_value = self._calculate_p_value(falsification_rate)
        effect_size = self._calculate_effect_size(falsifying_trials, trial_results)
        statistical_power = self._calculate_statistical_power(len(trial_results))

        # Determine if framework is falsified
        # Framework is falsified if falsification rate is significantly > 0
        is_falsified = falsification_rate > 0.05 and p_value < 0.05

        # Generate interpretation
        interpretation = self._generate_interpretation(
            falsification_rate, is_falsified, total_falsifying
        )

        return FalsificationTestResult(
            test_id=test_id,
            n_trials=n_trials,
            n_participants=n_participants,
            timestamp=timestamp,
            trial_results=trial_results,
            total_falsifying_trials=total_falsifying,
            falsification_rate=falsification_rate,
            mean_confidence=mean_confidence,
            p_value=p_value,
            effect_size=effect_size,
            statistical_power=statistical_power,
            is_framework_falsified=is_falsified,
            interpretation=interpretation,
        )

    def _calculate_p_value(self, falsification_rate: float) -> float:
        """Calculate p-value for falsification test"""
        # Simplified p-value calculation
        # In reality, this would use proper statistical tests
        if falsification_rate == 0:
            return 1.0
        elif falsification_rate < 0.01:
            return 0.5
        elif falsification_rate < 0.05:
            return 0.1
        else:
            return 0.01

    def _calculate_effect_size(
        self, falsifying_trials: List, all_trials: List
    ) -> float:
        """Calculate effect size (Cohen's d)"""
        # Simplified effect size calculation
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
        # Simplified power calculation based on sample size
        if n_trials < 50:
            return 0.6
        elif n_trials < 100:
            return 0.8
        else:
            return 0.95

    def _generate_interpretation(
        self, falsification_rate: float, is_falsified: bool, total_falsifying: int
    ) -> str:
        """Generate interpretation of results"""
        if is_falsified:
            return (
                f"FRAMEWORK FALSIFIED: {total_falsifying} trials showed full ignition "
                f"signatures without consciousness ({falsification_rate:.1%} rate). "
                f"This provides strong evidence against the APGI Framework's core prediction."
            )
        elif falsification_rate > 0:
            return (
                f"PARTIAL FALSIFICATION: {total_falsifying} trials showed potential "
                f"falsification ({falsification_rate:.1%} rate), but results do not reach "
                f"statistical significance. Further investigation needed."
            )
        else:
            return (
                "NO FALSIFICATION: No trials showed full ignition signatures without "
                "consciousness. Results support the APGI Framework's predictions."
            )

    def run_test(self, parameters: Optional[Dict] = None) -> FalsificationTestResult:
        """
        Execute the primary falsification test with given parameters.

        Args:
            parameters: Optional dictionary of test parameters
                - n_trials: Number of trials to run (default: 100)
                - n_participants: Number of participants (default: 20)
                - confidence_threshold: Threshold for falsification confidence (default: 0.7)

        Returns:
            FalsificationTestResult: Complete test results with analysis
        """
        if parameters is None:
            parameters = {}

        # Extract parameters with defaults
        n_trials = parameters.get("n_trials", 100)
        n_participants = parameters.get("n_participants", 20)
        confidence_threshold = parameters.get("confidence_threshold", 0.7)

        logger.info(
            f"Starting Primary Falsification Test: {n_trials} trials, {n_participants} participants"
        )

        # Generate test ID
        test_id = f"primary_falsification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

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
        result = self._analyze_results(test_id, trial_results, n_trials, n_participants)

        logger.info(
            f"Test completed: {result.total_falsifying_trials} falsifying trials "
            f"({result.falsification_rate:.1%} rate)"
        )

        return result
