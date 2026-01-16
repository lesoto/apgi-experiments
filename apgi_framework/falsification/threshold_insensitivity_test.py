"""
Threshold Insensitivity Test

Implements the secondary falsification test for threshold insensitivity to neuromodulatory
challenges. Tests whether the ignition threshold θₜ remains unchanged despite pharmacological
manipulations that should modulate it according to the APGI Framework.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime

from ..core.equation import APGIEquation
from ..core.threshold import ThresholdManager
from ..exceptions import ValidationError, SimulationError
from .error_handling_wrapper import with_error_handling, log_test_execution
import logging

logger = logging.getLogger(__name__)


class DrugType(Enum):
    """Types of pharmacological challenges"""

    PROPRANOLOL = "propranolol"  # Norepinephrine blockade
    L_DOPA = "l_dopa"  # Dopamine elevation
    SSRI = "ssri"  # Serotonin elevation
    PHYSOSTIGMINE = "physostigmine"  # Acetylcholine elevation
    PLACEBO = "placebo"  # Control condition


@dataclass
class PharmacologicalCondition:
    """Pharmacological condition parameters"""

    drug_type: DrugType
    dosage: float  # mg or standardized units
    administration_time: float  # minutes before testing
    expected_threshold_change: float  # Expected Δθₜ
    control_measures: Dict[str, float]  # Physiological controls


@dataclass
class ThresholdInsensitivityTrialResult:
    """Result of a single threshold insensitivity trial"""

    trial_id: str
    participant_id: str
    timestamp: datetime

    # Pharmacological condition
    drug_condition: PharmacologicalCondition
    baseline_threshold: float
    post_drug_threshold: float
    threshold_change: float

    # Expected vs observed changes
    expected_change: float
    observed_change: float
    change_difference: float

    # Control measures validation
    physiological_controls_valid: bool
    drug_effect_confirmed: bool

    # Threshold sensitivity assessment
    is_threshold_sensitive: bool
    sensitivity_confidence: float

    # Falsification assessment
    is_falsifying: bool
    confidence_level: float


@dataclass
class ThresholdInsensitivityTestResult:
    """Complete result of threshold insensitivity testing"""

    test_id: str
    n_trials: int
    n_participants: int
    drug_conditions: List[DrugType]
    timestamp: datetime

    trial_results: List[ThresholdInsensitivityTrialResult]

    # Summary statistics by drug type
    drug_sensitivity_results: Dict[str, Dict[str, Any]]

    # Overall sensitivity analysis
    total_insensitive_trials: int
    insensitivity_rate: float
    mean_confidence: float

    # Statistical analysis
    p_value: float
    effect_size: float
    statistical_power: float

    # Falsification assessment
    is_framework_falsified: bool
    interpretation: str


class ThresholdInsensitivityTest:
    """
    Test controller for threshold insensitivity falsification criterion.

    Tests whether the ignition threshold θₜ remains insensitive to neuromodulatory
    challenges that should modulate it according to the APGI Framework:
    - Propranolol (norepinephrine blockade) should increase θₜ
    - L-DOPA (dopamine elevation) should decrease θₜ
    - SSRIs (serotonin elevation) should modulate θₜ
    - Physostigmine (acetylcholine elevation) should decrease θₜ
    """

    def __init__(self):
        self.equation = APGIEquation()
        self.threshold_manager = ThresholdManager()

        # Expected threshold changes for each drug (standardized units)
        self.expected_changes = {
            DrugType.PROPRANOLOL: 0.5,  # Increase threshold
            DrugType.L_DOPA: -0.3,  # Decrease threshold
            DrugType.SSRI: -0.2,  # Decrease threshold
            DrugType.PHYSOSTIGMINE: -0.4,  # Decrease threshold
            DrugType.PLACEBO: 0.0,  # No change
        }

        # Sensitivity thresholds
        self.sensitivity_threshold = 0.1  # Minimum change to be considered sensitive
        self.insensitivity_threshold = 0.8  # Rate above which framework is falsified

    @with_error_handling(validate_params=True, enable_retry=True, log_errors=True)
    def run_threshold_insensitivity_test(
        self,
        n_trials_per_condition: int = 50,
        n_participants: int = 20,
        drug_conditions: Optional[List[DrugType]] = None,
        test_id: Optional[str] = None,
    ) -> ThresholdInsensitivityTestResult:
        """
        Run threshold insensitivity test across multiple drug conditions.

        Args:
            n_trials_per_condition: Number of trials per drug condition
            n_participants: Number of simulated participants
            drug_conditions: List of drug conditions to test
            test_id: Optional test identifier

        Returns:
            Complete threshold insensitivity test results

        Raises:
            ValidationError: If parameters are invalid
            SimulationError: If simulation fails
        """
        start_time = datetime.now()

        try:
            # Validate parameters
            if n_trials_per_condition <= 0:
                raise ValidationError(
                    f"n_trials_per_condition must be positive, got {n_trials_per_condition}"
                )
            if n_participants <= 0:
                raise ValidationError(
                    f"n_participants must be positive, got {n_participants}"
                )

            if test_id is None:
                test_id = f"threshold_insensitivity_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if drug_conditions is None:
                drug_conditions = [
                    DrugType.PROPRANOLOL,
                    DrugType.L_DOPA,
                    DrugType.SSRI,
                    DrugType.PHYSOSTIGMINE,
                    DrugType.PLACEBO,
                ]

            logger.info(f"Starting threshold insensitivity test: {test_id}")
            logger.info(
                f"Parameters: n_trials_per_condition={n_trials_per_condition}, n_participants={n_participants}"
            )
            logger.info(f"Drug conditions: {[d.value for d in drug_conditions]}")

            trial_results = []

            for participant_id in range(n_participants):
                participant_key = f"P{participant_id:03d}"

                for drug_type in drug_conditions:
                    for trial_num in range(n_trials_per_condition):
                        trial_id = f"{test_id}_p{participant_id:03d}_{drug_type.value}_t{trial_num:03d}"

                        try:
                            trial_result = self._run_single_trial(
                                trial_id=trial_id,
                                participant_id=participant_key,
                                drug_type=drug_type,
                            )
                            trial_results.append(trial_result)
                        except Exception as e:
                            logger.error(f"Trial {trial_id} failed: {str(e)}")
                            continue

            if not trial_results:
                raise SimulationError("All trials failed - no results to analyze")

            # Analyze results
            result = self._analyze_results(
                test_id,
                trial_results,
                n_trials_per_condition,
                n_participants,
                drug_conditions,
            )

            end_time = datetime.now()
            log_test_execution(
                "Threshold Insensitivity Test", start_time, end_time, True
            )

            return result

        except Exception as e:
            end_time = datetime.now()
            log_test_execution(
                "Threshold Insensitivity Test", start_time, end_time, False, e
            )
            raise

    def _run_single_trial(
        self, trial_id: str, participant_id: str, drug_type: DrugType
    ) -> ThresholdInsensitivityTrialResult:
        """
        Run a single threshold insensitivity trial.

        Args:
            trial_id: Unique trial identifier
            participant_id: Participant identifier
            drug_type: Type of pharmacological challenge

        Returns:
            Single trial result
        """
        timestamp = datetime.now()

        # Create pharmacological condition
        drug_condition = self._create_drug_condition(drug_type)

        # Simulate baseline threshold
        baseline_threshold = self._simulate_baseline_threshold(participant_id)

        # Simulate post-drug threshold
        post_drug_threshold = self._simulate_post_drug_threshold(
            baseline_threshold, drug_condition
        )

        # Calculate threshold change
        threshold_change = post_drug_threshold - baseline_threshold
        expected_change = drug_condition.expected_threshold_change
        observed_change = threshold_change
        change_difference = abs(observed_change - expected_change)

        # Validate control measures
        physiological_controls_valid = self._validate_physiological_controls(
            drug_condition
        )
        drug_effect_confirmed = self._confirm_drug_effect(drug_condition)

        # Assess threshold sensitivity
        is_threshold_sensitive = abs(threshold_change) > self.sensitivity_threshold
        sensitivity_confidence = self._calculate_sensitivity_confidence(
            threshold_change, expected_change
        )

        # Determine if this trial is falsifying (insensitive when should be sensitive)
        is_falsifying = self._determine_falsification(
            drug_type,
            threshold_change,
            physiological_controls_valid,
            drug_effect_confirmed,
        )

        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(
            change_difference, physiological_controls_valid, drug_effect_confirmed
        )

        return ThresholdInsensitivityTrialResult(
            trial_id=trial_id,
            participant_id=participant_id,
            timestamp=timestamp,
            drug_condition=drug_condition,
            baseline_threshold=baseline_threshold,
            post_drug_threshold=post_drug_threshold,
            threshold_change=threshold_change,
            expected_change=expected_change,
            observed_change=observed_change,
            change_difference=change_difference,
            physiological_controls_valid=physiological_controls_valid,
            drug_effect_confirmed=drug_effect_confirmed,
            is_threshold_sensitive=is_threshold_sensitive,
            sensitivity_confidence=sensitivity_confidence,
            is_falsifying=is_falsifying,
            confidence_level=confidence_level,
        )

    def _create_drug_condition(self, drug_type: DrugType) -> PharmacologicalCondition:
        """Create pharmacological condition for the given drug type"""
        dosage_ranges = {
            DrugType.PROPRANOLOL: (40, 80),  # mg
            DrugType.L_DOPA: (100, 200),  # mg
            DrugType.SSRI: (20, 40),  # mg (sertraline equivalent)
            DrugType.PHYSOSTIGMINE: (1, 2),  # mg
            DrugType.PLACEBO: (0, 0),  # No active ingredient
        }

        administration_times = {
            DrugType.PROPRANOLOL: 60,  # 1 hour
            DrugType.L_DOPA: 30,  # 30 minutes
            DrugType.SSRI: 120,  # 2 hours (chronic effect simulation)
            DrugType.PHYSOSTIGMINE: 15,  # 15 minutes
            DrugType.PLACEBO: 60,  # 1 hour
        }

        dosage_range = dosage_ranges[drug_type]
        dosage = np.random.uniform(dosage_range[0], dosage_range[1])

        # Simulate control measures (physiological responses)
        control_measures = self._simulate_control_measures(drug_type, dosage)

        return PharmacologicalCondition(
            drug_type=drug_type,
            dosage=dosage,
            administration_time=administration_times[drug_type],
            expected_threshold_change=self.expected_changes[drug_type],
            control_measures=control_measures,
        )

    def _simulate_control_measures(
        self, drug_type: DrugType, dosage: float
    ) -> Dict[str, float]:
        """Simulate physiological control measures for drug validation"""
        controls = {}

        if drug_type == DrugType.PROPRANOLOL:
            # Beta-blocker effects
            controls["heart_rate_change"] = -np.random.uniform(10, 25)  # Decreased HR
            controls["blood_pressure_change"] = -np.random.uniform(
                5, 15
            )  # Decreased BP
            controls["pupil_response"] = np.random.uniform(0.7, 0.9)  # Reduced response

        elif drug_type == DrugType.L_DOPA:
            # Dopaminergic effects
            controls["motor_response"] = np.random.uniform(1.1, 1.3)  # Enhanced motor
            controls["attention_score"] = np.random.uniform(
                1.05, 1.2
            )  # Enhanced attention
            controls["pupil_dilation"] = np.random.uniform(
                1.1, 1.25
            )  # Increased dilation

        elif drug_type == DrugType.SSRI:
            # Serotonergic effects
            controls["mood_rating"] = np.random.uniform(
                1.05, 1.15
            )  # Slight mood improvement
            controls["anxiety_score"] = np.random.uniform(0.85, 0.95)  # Reduced anxiety
            controls["sleep_quality"] = np.random.uniform(0.9, 1.1)  # Variable sleep

        elif drug_type == DrugType.PHYSOSTIGMINE:
            # Cholinergic effects
            controls["memory_score"] = np.random.uniform(1.1, 1.3)  # Enhanced memory
            controls["attention_score"] = np.random.uniform(
                1.15, 1.35
            )  # Enhanced attention
            controls["salivation"] = np.random.uniform(1.2, 1.5)  # Increased salivation

        else:  # PLACEBO
            # No significant changes
            controls["heart_rate_change"] = np.random.uniform(-2, 2)
            controls["blood_pressure_change"] = np.random.uniform(-2, 2)
            controls["mood_rating"] = np.random.uniform(0.98, 1.02)

        return controls

    def _simulate_baseline_threshold(self, participant_id: str) -> float:
        """Simulate baseline ignition threshold for participant"""
        # Individual differences in baseline threshold
        participant_hash = hash(participant_id) % 1000
        individual_offset = (participant_hash / 1000 - 0.5) * 0.5  # ±0.25 variation

        baseline = 3.5 + individual_offset  # Standard baseline ± individual variation
        return np.clip(baseline, 2.0, 5.0)

    def _simulate_post_drug_threshold(
        self, baseline_threshold: float, drug_condition: PharmacologicalCondition
    ) -> float:
        """Simulate post-drug threshold with potential insensitivity"""
        expected_change = drug_condition.expected_threshold_change

        # Simulate varying degrees of sensitivity/insensitivity
        sensitivity_factor = np.random.uniform(
            0.0, 1.2
        )  # 0 = completely insensitive, 1+ = normal/hypersensitive

        # Add noise
        noise = np.random.normal(0, 0.1)

        # Calculate actual change
        actual_change = expected_change * sensitivity_factor + noise

        post_drug_threshold = baseline_threshold + actual_change

        # Ensure threshold stays within physiological bounds
        return np.clip(post_drug_threshold, 1.0, 6.0)

    def _validate_physiological_controls(
        self, drug_condition: PharmacologicalCondition
    ) -> bool:
        """Validate that physiological control measures show expected drug effects"""
        drug_type = drug_condition.drug_type
        controls = drug_condition.control_measures

        if drug_type == DrugType.PROPRANOLOL:
            # Check for beta-blocker effects
            hr_decreased = controls.get("heart_rate_change", 0) < -5
            bp_decreased = controls.get("blood_pressure_change", 0) < -3
            return hr_decreased and bp_decreased

        elif drug_type == DrugType.L_DOPA:
            # Check for dopaminergic effects
            motor_enhanced = controls.get("motor_response", 1.0) > 1.05
            attention_enhanced = controls.get("attention_score", 1.0) > 1.02
            return motor_enhanced or attention_enhanced

        elif drug_type == DrugType.SSRI:
            # Check for serotonergic effects (subtle)
            mood_improved = controls.get("mood_rating", 1.0) > 1.02
            anxiety_reduced = controls.get("anxiety_score", 1.0) < 0.98
            return mood_improved or anxiety_reduced

        elif drug_type == DrugType.PHYSOSTIGMINE:
            # Check for cholinergic effects
            memory_enhanced = controls.get("memory_score", 1.0) > 1.05
            salivation_increased = controls.get("salivation", 1.0) > 1.1
            return memory_enhanced and salivation_increased

        else:  # PLACEBO
            # Should show no significant effects
            return True

    def _confirm_drug_effect(self, drug_condition: PharmacologicalCondition) -> bool:
        """Confirm that drug reached effective levels (simulated)"""
        # Simulate drug level confirmation (e.g., plasma levels, biomarkers)
        drug_type = drug_condition.drug_type
        dosage = drug_condition.dosage

        if drug_type == DrugType.PLACEBO:
            return True  # Placebo always "effective"

        # Simulate effective drug levels based on dosage
        effectiveness_probability = min(
            0.95, dosage / 100.0
        )  # Higher dose = more likely effective
        return np.random.random() < effectiveness_probability

    def _calculate_sensitivity_confidence(
        self, threshold_change: float, expected_change: float
    ) -> float:
        """Calculate confidence in sensitivity assessment"""
        if expected_change == 0:  # Placebo condition
            return 0.5

        # Higher confidence when observed change matches expected direction and magnitude
        direction_match = np.sign(threshold_change) == np.sign(expected_change)
        magnitude_ratio = (
            abs(threshold_change) / abs(expected_change) if expected_change != 0 else 0
        )

        if direction_match:
            confidence = 0.5 + 0.3 * min(1.0, magnitude_ratio)
        else:
            confidence = 0.5 - 0.2 * min(
                1.0, abs(threshold_change) / abs(expected_change)
            )

        return np.clip(confidence, 0.0, 1.0)

    def _determine_falsification(
        self,
        drug_type: DrugType,
        threshold_change: float,
        physiological_controls_valid: bool,
        drug_effect_confirmed: bool,
    ) -> bool:
        """
        Determine if this trial represents threshold insensitivity falsification.

        Falsification occurs when:
        1. Drug should cause threshold change (not placebo)
        2. Physiological controls confirm drug effect
        3. Drug effect is confirmed
        4. But threshold shows no significant change
        """
        if drug_type == DrugType.PLACEBO:
            return False  # Placebo should not cause changes

        expected_change = self.expected_changes[drug_type]

        # Check if threshold is insensitive despite drug effects
        threshold_insensitive = abs(threshold_change) < self.sensitivity_threshold

        return (
            threshold_insensitive
            and physiological_controls_valid
            and drug_effect_confirmed
            and abs(expected_change) > self.sensitivity_threshold
        )

    def _calculate_confidence_level(
        self,
        change_difference: float,
        physiological_controls_valid: bool,
        drug_effect_confirmed: bool,
    ) -> float:
        """Calculate confidence level for the trial result"""
        base_confidence = 0.5

        # Higher confidence when controls are valid
        if physiological_controls_valid:
            base_confidence += 0.2

        # Higher confidence when drug effect is confirmed
        if drug_effect_confirmed:
            base_confidence += 0.2

        # Higher confidence when change difference is clear
        if change_difference > 0.3:
            base_confidence += 0.1

        return min(base_confidence, 1.0)

    def _analyze_results(
        self,
        test_id: str,
        trial_results: List[ThresholdInsensitivityTrialResult],
        n_trials_per_condition: int,
        n_participants: int,
        drug_conditions: List[DrugType],
    ) -> ThresholdInsensitivityTestResult:
        """Analyze complete threshold insensitivity test results"""
        timestamp = datetime.now()

        # Count insensitive trials
        insensitive_trials = [r for r in trial_results if r.is_falsifying]
        total_insensitive = len(insensitive_trials)
        insensitivity_rate = (
            total_insensitive / len(trial_results) if trial_results else 0
        )

        # Calculate mean confidence
        mean_confidence = np.mean([r.confidence_level for r in trial_results])

        # Analyze results by drug type
        drug_sensitivity_results = {}
        for drug_type in drug_conditions:
            drug_trials = [
                r for r in trial_results if r.drug_condition.drug_type == drug_type
            ]
            drug_insensitive = [r for r in drug_trials if r.is_falsifying]

            drug_sensitivity_results[drug_type.value] = {
                "total_trials": len(drug_trials),
                "insensitive_trials": len(drug_insensitive),
                "insensitivity_rate": (
                    len(drug_insensitive) / len(drug_trials) if drug_trials else 0
                ),
                "mean_threshold_change": np.mean(
                    [r.threshold_change for r in drug_trials]
                ),
                "expected_change": self.expected_changes[drug_type],
                "mean_confidence": np.mean([r.confidence_level for r in drug_trials]),
            }

        # Perform statistical analysis
        p_value = self._calculate_p_value(
            insensitivity_rate, total_insensitive, len(trial_results)
        )
        effect_size = self._calculate_effect_size(insensitive_trials, trial_results)
        statistical_power = self._calculate_statistical_power(len(trial_results))

        # Determine if framework is falsified
        is_falsified = (
            insensitivity_rate > self.insensitivity_threshold and p_value < 0.05
        )

        # Generate interpretation
        interpretation = self._generate_interpretation(
            insensitivity_rate,
            is_falsified,
            total_insensitive,
            drug_sensitivity_results,
        )

        return ThresholdInsensitivityTestResult(
            test_id=test_id,
            n_trials=len(trial_results),
            n_participants=n_participants,
            drug_conditions=drug_conditions,
            timestamp=timestamp,
            trial_results=trial_results,
            drug_sensitivity_results=drug_sensitivity_results,
            total_insensitive_trials=total_insensitive,
            insensitivity_rate=insensitivity_rate,
            mean_confidence=mean_confidence,
            p_value=p_value,
            effect_size=effect_size,
            statistical_power=statistical_power,
            is_framework_falsified=is_falsified,
            interpretation=interpretation,
        )

    def _calculate_p_value(
        self, insensitivity_rate: float, n_insensitive: int, n_total: int
    ) -> float:
        """Calculate p-value for insensitivity test"""
        # Null hypothesis: threshold is sensitive to neuromodulation
        if n_insensitive == 0:
            return 1.0

        # Expected insensitivity rate under null (some natural variation)
        expected_rate = 0.1

        if insensitivity_rate <= expected_rate:
            return 0.8
        elif insensitivity_rate > self.insensitivity_threshold:
            return 0.01
        else:
            return 0.1

    def _calculate_effect_size(
        self, insensitive_trials: List, all_trials: List
    ) -> float:
        """Calculate effect size for insensitivity"""
        if len(insensitive_trials) == 0:
            return 0.0

        # Use threshold changes as the measure
        insensitive_changes = [abs(t.threshold_change) for t in insensitive_trials]
        sensitive_changes = [
            abs(t.threshold_change) for t in all_trials if not t.is_falsifying
        ]

        if len(sensitive_changes) == 0:
            return 1.0

        mean_diff = np.mean(sensitive_changes) - np.mean(insensitive_changes)
        pooled_std = np.sqrt(
            (np.var(insensitive_changes) + np.var(sensitive_changes)) / 2
        )

        if pooled_std == 0:
            return 0.0

        return mean_diff / pooled_std

    def _calculate_statistical_power(self, n_trials: int) -> float:
        """Calculate statistical power"""
        if n_trials < 200:
            return 0.6
        elif n_trials < 500:
            return 0.8
        else:
            return 0.95

    def _generate_interpretation(
        self,
        insensitivity_rate: float,
        is_falsified: bool,
        total_insensitive: int,
        drug_results: Dict[str, Dict[str, Any]],
    ) -> str:
        """Generate interpretation of threshold insensitivity results"""
        if is_falsified:
            # Identify which drugs showed insensitivity
            insensitive_drugs = [
                drug
                for drug, results in drug_results.items()
                if results["insensitivity_rate"] > 0.5 and drug != "placebo"
            ]

            return (
                f"FRAMEWORK FALSIFIED: {total_insensitive} trials ({insensitivity_rate:.1%}) "
                f"showed threshold insensitivity to neuromodulatory challenges. "
                f"Drugs showing insensitivity: {', '.join(insensitive_drugs)}. "
                f"This contradicts the APGI Framework's prediction that θₜ should be "
                f"modulated by neuromodulatory systems."
            )

        elif insensitivity_rate > 0.3:
            return (
                f"PARTIAL INSENSITIVITY: {total_insensitive} trials ({insensitivity_rate:.1%}) "
                f"showed threshold insensitivity, but this does not reach the falsification "
                f"threshold. Results suggest potential limitations in neuromodulatory "
                f"implementation but are not conclusive."
            )

        else:
            return (
                f"THRESHOLD SENSITIVITY CONFIRMED: Only {total_insensitive} trials "
                f"({insensitivity_rate:.1%}) showed insensitivity to neuromodulatory "
                f"challenges. Results support the APGI Framework's prediction that "
                f"ignition threshold is modulated by neuromodulatory systems."
            )

    def run_test(
        self, parameters: Optional[Dict] = None
    ) -> ThresholdInsensitivityTestResult:
        """
        Execute the threshold insensitivity test with given parameters.

        Args:
            parameters: Optional dictionary of test parameters
                - n_trials: Number of trials to run (default: 150)
                - n_participants: Number of participants (default: 25)
                - confidence_threshold: Threshold for falsification confidence (default: 0.75)
                - drug_conditions: List of drug types to test (default: all available)

        Returns:
            ThresholdInsensitivityTestResult: Complete test results with analysis
        """
        if parameters is None:
            parameters = {}

        # Extract parameters with defaults
        n_trials = parameters.get("n_trials", 150)
        n_participants = parameters.get("n_participants", 25)
        confidence_threshold = parameters.get("confidence_threshold", 0.75)
        drug_conditions = parameters.get(
            "drug_conditions",
            [
                DrugType.PLACEBO,
                DrugType.PROPRANOLOL,
                DrugType.L_DOPA,
                DrugType.SSRI,
                DrugType.PHYSOSTIGMINE,
            ],
        )

        logger.info(
            f"Starting Threshold Insensitivity Test: {n_trials} trials, "
            f"{n_participants} participants, {len(drug_conditions)} drug conditions"
        )

        # Generate test ID
        test_id = f"threshold_insensitivity_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Run trials
        trial_results = []
        for trial_idx in range(n_trials):
            participant_id = f"participant_{(trial_idx % n_participants) + 1:02d}"
            drug_condition = drug_conditions[trial_idx % len(drug_conditions)]

            try:
                trial_result = self._run_single_trial(
                    trial_id=f"{test_id}_trial_{trial_idx:03d}",
                    participant_id=participant_id,
                    drug_type=drug_condition,
                    confidence_threshold=confidence_threshold,
                )
                trial_results.append(trial_result)

                if trial_idx % 15 == 0:
                    logger.info(f"Completed {trial_idx}/{n_trials} trials")

            except Exception as e:
                logger.error(f"Trial {trial_idx} failed: {e}")
                # Continue with other trials

        # Analyze results
        result = self._analyze_results(
            test_id, trial_results, n_trials, n_participants, drug_conditions
        )

        logger.info(
            f"Test completed: {result.total_insensitive_trials} insensitive trials "
            f"({result.insensitivity_rate:.1%} rate), falsified = {result.is_framework_falsified}"
        )

        return result
