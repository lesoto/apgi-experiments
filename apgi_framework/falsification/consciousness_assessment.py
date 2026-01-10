"""
Consciousness Assessment System for APGI Framework Falsification Testing

This module implements the consciousness assessment system that evaluates conscious access
through multiple converging measures including subjective reports, forced-choice tasks,
confidence ratings, and wagering behavior.

Key components:
- ConsciousnessAssessment data model
- Subjective report validation
- Forced-choice task simulation
- Confidence rating and wagering behavior modeling
- Metacognitive sensitivity assessment
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import numpy as np
import random
from datetime import datetime

from ..exceptions import ValidationError


class ResponseType(Enum):
    """Types of consciousness assessment responses"""

    SUBJECTIVE_REPORT = "subjective_report"
    FORCED_CHOICE = "forced_choice"
    CONFIDENCE_RATING = "confidence_rating"
    WAGERING = "wagering"


class ConsciousnessLevel(Enum):
    """Levels of consciousness for assessment"""

    CONSCIOUS = "conscious"
    UNCONSCIOUS = "unconscious"
    THRESHOLD = "threshold"


@dataclass
class ConsciousnessAssessment:
    """
    Data model for consciousness assessment results.

    Based on the design document requirements for comprehensive consciousness
    evaluation using multiple converging measures.
    """

    subjective_report: bool  # "Did you see/hear X?" - True if reported as seen
    forced_choice_accuracy: float  # Objective forced-choice performance (0.0-1.0)
    confidence_rating: float  # Confidence in response (0.0-1.0)
    wagering_behavior: float  # Willingness to wager on response (0.0-1.0)
    metacognitive_sensitivity: float  # Confidence-accuracy correspondence

    # Additional assessment details
    response_time: Optional[float] = None  # Response time in milliseconds
    trial_id: Optional[str] = None
    timestamp: Optional[datetime] = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate assessment parameters"""
        self._validate_parameters()

    def _validate_parameters(self):
        """Validate that all parameters are within expected ranges"""
        if not 0.0 <= self.forced_choice_accuracy <= 1.0:
            raise ValidationError(
                f"Forced choice accuracy must be between 0.0 and 1.0, got {self.forced_choice_accuracy}"
            )

        if not 0.0 <= self.confidence_rating <= 1.0:
            raise ValidationError(
                f"Confidence rating must be between 0.0 and 1.0, got {self.confidence_rating}"
            )

        if not 0.0 <= self.wagering_behavior <= 1.0:
            raise ValidationError(
                f"Wagering behavior must be between 0.0 and 1.0, got {self.wagering_behavior}"
            )

        if not 0.0 <= self.metacognitive_sensitivity <= 1.0:
            raise ValidationError(
                f"Metacognitive sensitivity must be between 0.0 and 1.0, got {self.metacognitive_sensitivity}"
            )

    def is_conscious_by_subjective_report(self) -> bool:
        """Check if stimulus was reported as consciously perceived"""
        return self.subjective_report

    def is_conscious_by_forced_choice(
        self, chance_level: float = 0.5, threshold: float = 0.1
    ) -> bool:
        """
        Check if forced-choice performance indicates consciousness.

        Args:
            chance_level: Expected chance performance level (default 0.5 for 2AFC)
            threshold: Minimum above-chance performance to indicate consciousness

        Returns:
            True if performance significantly above chance
        """
        return self.forced_choice_accuracy > (chance_level + threshold)

    def has_metacognitive_awareness(self, threshold: float = 0.3) -> bool:
        """
        Check if participant shows metacognitive awareness.

        Args:
            threshold: Minimum metacognitive sensitivity for awareness

        Returns:
            True if metacognitive sensitivity above threshold
        """
        return self.metacognitive_sensitivity > threshold

    def get_consciousness_classification(self) -> ConsciousnessLevel:
        """
        Classify consciousness level based on multiple measures.

        Returns:
            ConsciousnessLevel classification
        """
        subjective_conscious = self.is_conscious_by_subjective_report()
        objective_conscious = self.is_conscious_by_forced_choice()
        has_metacognition = self.has_metacognitive_awareness()

        # Full consciousness: all measures agree
        if subjective_conscious and objective_conscious and has_metacognition:
            return ConsciousnessLevel.CONSCIOUS

        # Clear unconsciousness: no measures indicate consciousness
        if (
            not subjective_conscious
            and not objective_conscious
            and not has_metacognition
        ):
            return ConsciousnessLevel.UNCONSCIOUS

        # Threshold/ambiguous cases
        return ConsciousnessLevel.THRESHOLD


class ConsciousnessAssessmentSimulator:
    """
    Simulator for consciousness assessment responses.

    Generates realistic consciousness assessment data for testing
    falsification scenarios.
    """

    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize the consciousness assessment simulator.

        Args:
            random_seed: Random seed for reproducible simulations
        """
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)

        # Default parameters for simulation
        self.default_params = {
            "conscious_subjective_prob": 0.85,  # Probability of reporting conscious when conscious
            "unconscious_subjective_prob": 0.15,  # Probability of reporting conscious when unconscious
            "conscious_accuracy_mean": 0.75,  # Mean forced-choice accuracy when conscious
            "unconscious_accuracy_mean": 0.52,  # Mean forced-choice accuracy when unconscious
            "accuracy_std": 0.1,  # Standard deviation for accuracy
            "confidence_correlation": 0.6,  # Correlation between accuracy and confidence
            "wagering_correlation": 0.7,  # Correlation between confidence and wagering
            "metacognitive_noise": 0.2,  # Noise in metacognitive sensitivity
        }

    def simulate_assessment(
        self,
        true_consciousness_level: ConsciousnessLevel,
        trial_id: Optional[str] = None,
        custom_params: Optional[Dict[str, float]] = None,
    ) -> ConsciousnessAssessment:
        """
        Simulate a consciousness assessment for a given true consciousness level.

        Args:
            true_consciousness_level: The actual consciousness level
            trial_id: Optional trial identifier
            custom_params: Optional custom simulation parameters

        Returns:
            ConsciousnessAssessment with simulated responses
        """
        params = self.default_params.copy()
        if custom_params:
            params.update(custom_params)

        # Simulate subjective report
        if true_consciousness_level == ConsciousnessLevel.CONSCIOUS:
            subjective_report = random.random() < params["conscious_subjective_prob"]
            accuracy_mean = params["conscious_accuracy_mean"]
        else:
            subjective_report = random.random() < params["unconscious_subjective_prob"]
            accuracy_mean = params["unconscious_accuracy_mean"]

        # Simulate forced-choice accuracy
        forced_choice_accuracy = np.clip(
            np.random.normal(accuracy_mean, params["accuracy_std"]), 0.0, 1.0
        )

        # Simulate confidence rating (correlated with accuracy)
        confidence_base = forced_choice_accuracy * params["confidence_correlation"]
        confidence_noise = np.random.normal(0, 0.2)
        confidence_rating = np.clip(confidence_base + confidence_noise, 0.0, 1.0)

        # Simulate wagering behavior (correlated with confidence)
        wagering_base = confidence_rating * params["wagering_correlation"]
        wagering_noise = np.random.normal(0, 0.15)
        wagering_behavior = np.clip(wagering_base + wagering_noise, 0.0, 1.0)

        # Calculate metacognitive sensitivity (confidence-accuracy correspondence)
        metacognitive_sensitivity = self._calculate_metacognitive_sensitivity(
            forced_choice_accuracy, confidence_rating, params["metacognitive_noise"]
        )

        # Simulate response time (conscious responses typically faster)
        if true_consciousness_level == ConsciousnessLevel.CONSCIOUS:
            response_time = np.random.gamma(2, 200)  # Faster responses
        else:
            response_time = np.random.gamma(3, 300)  # Slower responses

        return ConsciousnessAssessment(
            subjective_report=subjective_report,
            forced_choice_accuracy=forced_choice_accuracy,
            confidence_rating=confidence_rating,
            wagering_behavior=wagering_behavior,
            metacognitive_sensitivity=metacognitive_sensitivity,
            response_time=response_time,
            trial_id=trial_id,
            metadata={"true_consciousness_level": true_consciousness_level.value},
        )

    def _calculate_metacognitive_sensitivity(
        self, accuracy: float, confidence: float, noise_level: float
    ) -> float:
        """
        Calculate metacognitive sensitivity as confidence-accuracy correspondence.

        Args:
            accuracy: Forced-choice accuracy
            confidence: Confidence rating
            noise_level: Amount of noise to add

        Returns:
            Metacognitive sensitivity value
        """
        # Base sensitivity on how well confidence matches accuracy
        base_sensitivity = 1.0 - abs(accuracy - confidence)

        # Add noise
        noise = np.random.normal(0, noise_level)
        sensitivity = np.clip(base_sensitivity + noise, 0.0, 1.0)

        return sensitivity

    def simulate_batch_assessments(
        self,
        consciousness_levels: List[ConsciousnessLevel],
        trial_ids: Optional[List[str]] = None,
    ) -> List[ConsciousnessAssessment]:
        """
        Simulate a batch of consciousness assessments.

        Args:
            consciousness_levels: List of true consciousness levels
            trial_ids: Optional list of trial identifiers

        Returns:
            List of ConsciousnessAssessment objects
        """
        if trial_ids is None:
            trial_ids = [f"trial_{i}" for i in range(len(consciousness_levels))]

        if len(trial_ids) != len(consciousness_levels):
            raise ValidationError(
                "Number of trial IDs must match number of consciousness levels"
            )

        assessments = []
        for level, trial_id in zip(consciousness_levels, trial_ids):
            assessment = self.simulate_assessment(level, trial_id)
            assessments.append(assessment)

        return assessments

    def simulate_conscious_trial(
        self,
        trial_id: Optional[str] = None,
        custom_params: Optional[Dict[str, float]] = None,
    ) -> ConsciousnessAssessment:
        return self.simulate_assessment(
            ConsciousnessLevel.CONSCIOUS, trial_id, custom_params
        )


class ConsciousnessValidator:
    """
    Validator for consciousness assessment results.

    Implements validation logic for falsification testing scenarios.
    """

    def __init__(self):
        """Initialize the consciousness validator"""
        self.validation_thresholds = {
            "chance_level": 0.5,  # Expected chance performance
            "above_chance_threshold": 0.1,  # Minimum above-chance for consciousness
            "metacognitive_threshold": 0.3,  # Minimum metacognitive sensitivity
            "confidence_threshold": 0.6,  # Minimum confidence for conscious reports
            "wagering_threshold": 0.5,  # Minimum wagering for conscious reports
        }

    def validate_consciousness_absence(
        self, assessment: ConsciousnessAssessment
    ) -> bool:
        """
        Validate that consciousness is absent according to falsification criteria.

        For primary falsification testing, consciousness must be absent despite
        full ignition signatures being present.

        Args:
            assessment: ConsciousnessAssessment to validate

        Returns:
            True if consciousness is validly absent
        """
        # Subjective report must be negative
        subjective_absent = not assessment.subjective_report

        # Forced-choice must be at chance level
        at_chance = not assessment.is_conscious_by_forced_choice(
            self.validation_thresholds["chance_level"],
            self.validation_thresholds["above_chance_threshold"],
        )

        # No evidence of metacognitive access
        no_metacognition = not assessment.has_metacognitive_awareness(
            self.validation_thresholds["metacognitive_threshold"]
        )

        # Low confidence and wagering
        low_confidence = (
            assessment.confidence_rating
            < self.validation_thresholds["confidence_threshold"]
        )
        low_wagering = (
            assessment.wagering_behavior
            < self.validation_thresholds["wagering_threshold"]
        )

        return (
            subjective_absent
            and at_chance
            and no_metacognition
            and low_confidence
            and low_wagering
        )

    def validate_consciousness_presence(
        self, assessment: ConsciousnessAssessment
    ) -> bool:
        """
        Validate that consciousness is present.

        Args:
            assessment: ConsciousnessAssessment to validate

        Returns:
            True if consciousness is validly present
        """
        # Subjective report must be positive
        subjective_present = assessment.subjective_report

        # Forced-choice must be above chance
        above_chance = assessment.is_conscious_by_forced_choice(
            self.validation_thresholds["chance_level"],
            self.validation_thresholds["above_chance_threshold"],
        )

        # Evidence of metacognitive access
        has_metacognition = assessment.has_metacognitive_awareness(
            self.validation_thresholds["metacognitive_threshold"]
        )

        return subjective_present and above_chance and has_metacognition

    def calculate_consciousness_score(
        self, assessment: ConsciousnessAssessment
    ) -> float:
        """
        Calculate a composite consciousness score from multiple measures.

        Args:
            assessment: ConsciousnessAssessment to score

        Returns:
            Consciousness score between 0.0 (unconscious) and 1.0 (conscious)
        """
        # Weight different measures
        weights = {
            "subjective": 0.25,
            "objective": 0.30,
            "confidence": 0.20,
            "wagering": 0.15,
            "metacognitive": 0.10,
        }

        # Calculate weighted score
        score = 0.0
        score += weights["subjective"] * (1.0 if assessment.subjective_report else 0.0)
        score += weights["objective"] * assessment.forced_choice_accuracy
        score += weights["confidence"] * assessment.confidence_rating
        score += weights["wagering"] * assessment.wagering_behavior
        score += weights["metacognitive"] * assessment.metacognitive_sensitivity

        return np.clip(score, 0.0, 1.0)

    def validate_batch_assessments(
        self,
        assessments: List[ConsciousnessAssessment],
        expected_consciousness: List[bool],
    ) -> Dict[str, Any]:
        """
        Validate a batch of consciousness assessments.

        Args:
            assessments: List of ConsciousnessAssessment objects
            expected_consciousness: List of expected consciousness states

        Returns:
            Dictionary with validation results and statistics
        """
        if len(assessments) != len(expected_consciousness):
            raise ValidationError(
                "Number of assessments must match expected consciousness states"
            )

        results = {
            "total_trials": len(assessments),
            "correct_classifications": 0,
            "false_positives": 0,  # Reported conscious when unconscious
            "false_negatives": 0,  # Reported unconscious when conscious
            "consciousness_scores": [],
            "validation_details": [],
        }

        for assessment, expected in zip(assessments, expected_consciousness):
            is_conscious = self.validate_consciousness_presence(assessment)
            consciousness_score = self.calculate_consciousness_score(assessment)

            results["consciousness_scores"].append(consciousness_score)

            # Classification accuracy
            if is_conscious == expected:
                results["correct_classifications"] += 1
            elif is_conscious and not expected:
                results["false_positives"] += 1
            elif not is_conscious and expected:
                results["false_negatives"] += 1

            results["validation_details"].append(
                {
                    "assessment": assessment,
                    "expected_conscious": expected,
                    "classified_conscious": is_conscious,
                    "consciousness_score": consciousness_score,
                }
            )

        # Calculate summary statistics
        results["accuracy"] = (
            results["correct_classifications"] / results["total_trials"]
        )
        results["false_positive_rate"] = (
            results["false_positives"] / results["total_trials"]
        )
        results["false_negative_rate"] = (
            results["false_negatives"] / results["total_trials"]
        )
        results["mean_consciousness_score"] = np.mean(results["consciousness_scores"])
        results["std_consciousness_score"] = np.std(results["consciousness_scores"])

        return results
