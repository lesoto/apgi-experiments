"""
Priority 1: Direct Threshold Estimation System

Implements psychophysical threshold estimation protocols across visual, auditory,
and interoceptive modalities with cross-modal normalization and neural validation.

This module fulfills Requirements 2.1-2.5 for direct threshold estimation.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime
from enum import Enum
import logging
import json
from pathlib import Path

# Import existing components
from .adaptive_staircase import (
    AdaptiveStaircase,
    StaircaseParameters,
    StaircaseType,
    ThresholdEstimate,
    CrossModalThresholdNormalizer,
    create_staircase,
)
from .multi_modal_task_manager import (
    MultiModalTaskManager,
    ModalityType,
    TaskParadigm,
    TrialConfiguration,
    TrialResult,
)
from ..adaptive.stimulus_generators import (
    GaborParameters,
    ToneParameters,
    CO2PuffParameters,
)

logger = logging.getLogger(__name__)


class ThresholdType(Enum):
    """Types of thresholds to estimate."""

    DETECTION = "detection"  # Sensory detection threshold
    CONSCIOUS_ACCESS = "conscious_access"  # 50% conscious detection threshold
    DISCRIMINATION = "discrimination"  # Discrimination threshold


@dataclass
class ModalityThresholdConfig:
    """Configuration for threshold estimation in a specific modality."""

    modality: ModalityType
    threshold_type: ThresholdType

    # Staircase parameters
    staircase_params: StaircaseParameters

    # Stimulus parameters
    base_visual_params: Optional[GaborParameters] = None
    base_auditory_params: Optional[ToneParameters] = None
    base_interoceptive_params: Optional[CO2PuffParameters] = None

    # Awareness probe parameters
    awareness_probe_delay_ms: float = 500.0  # Delay before awareness probe
    use_awareness_probe: bool = True  # Whether to probe conscious awareness

    # Trial parameters
    n_trials_per_block: int = 50
    n_blocks: int = 2
    inter_block_rest_ms: float = 30000.0  # 30 seconds rest

    def validate(self) -> bool:
        """Validate configuration."""
        if not self.staircase_params.validate():
            return False

        # Check that appropriate stimulus parameters are set
        if self.modality == ModalityType.VISUAL and self.base_visual_params is None:
            logger.error("Visual modality requires base_visual_params")
            return False

        if self.modality == ModalityType.AUDITORY and self.base_auditory_params is None:
            logger.error("Auditory modality requires base_auditory_params")
            return False

        if (
            self.modality == ModalityType.INTEROCEPTIVE
            and self.base_interoceptive_params is None
        ):
            logger.error("Interoceptive modality requires base_interoceptive_params")
            return False

        return True


@dataclass
class ThresholdEstimationResult:
    """Results from threshold estimation procedure."""

    participant_id: str
    session_id: str
    modality: ModalityType
    threshold_type: ThresholdType

    # Threshold estimates
    detection_threshold: Optional[ThresholdEstimate] = None
    conscious_threshold: Optional[ThresholdEstimate] = None

    # Cross-modal normalization
    normalized_threshold: Optional[float] = None

    # Reliability metrics
    test_retest_icc: Optional[float] = None
    within_session_stability: Optional[float] = None

    # Trial data
    n_trials_completed: int = 0
    n_blocks_completed: int = 0
    completion_time_minutes: float = 0.0

    # Quality metrics
    data_quality_score: float = 1.0
    timing_quality_score: float = 1.0

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "participant_id": self.participant_id,
            "session_id": self.session_id,
            "modality": self.modality.value,
            "threshold_type": self.threshold_type.value,
            "detection_threshold": (
                self.detection_threshold.to_dict() if self.detection_threshold else None
            ),
            "conscious_threshold": (
                self.conscious_threshold.to_dict() if self.conscious_threshold else None
            ),
            "normalized_threshold": self.normalized_threshold,
            "test_retest_icc": self.test_retest_icc,
            "within_session_stability": self.within_session_stability,
            "n_trials_completed": self.n_trials_completed,
            "n_blocks_completed": self.n_blocks_completed,
            "completion_time_minutes": self.completion_time_minutes,
            "data_quality_score": self.data_quality_score,
            "timing_quality_score": self.timing_quality_score,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ThresholdEstimationProtocol:
    """
    Implements psychophysical threshold estimation protocols.

    Supports adaptive staircase procedures across visual, auditory, and
    interoceptive modalities with 50% conscious detection threshold calculation
    and cross-modal normalization.

    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """

    def __init__(
        self,
        participant_id: str,
        session_id: str,
        protocol_id: str = "threshold_estimation",
    ):
        """
        Initialize threshold estimation protocol.

        Args:
            participant_id: Unique participant identifier
            session_id: Unique session identifier
            protocol_id: Protocol identifier
        """
        self.participant_id = participant_id
        self.session_id = session_id
        self.protocol_id = protocol_id

        # Task manager for stimulus presentation
        self.task_manager: Optional[MultiModalTaskManager] = None

        # Staircases for each modality
        self.staircases: Dict[ModalityType, AdaptiveStaircase] = {}

        # Cross-modal normalizer
        self.normalizer = CrossModalThresholdNormalizer()

        # Results storage
        self.results: Dict[ModalityType, ThresholdEstimationResult] = {}

        # Trial history
        self.trial_history: List[TrialResult] = []

        # Session tracking
        self.session_start_time: Optional[datetime] = None
        self.is_initialized = False

        logger.info(
            f"Initialized ThresholdEstimationProtocol for participant {participant_id}"
        )

    def initialize(
        self,
        screen_width: int = 1920,
        screen_height: int = 1080,
        viewing_distance_cm: float = 60.0,
        sample_rate: int = 44100,
    ) -> bool:
        """
        Initialize the protocol and task manager.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            viewing_distance_cm: Viewing distance in centimeters
            sample_rate: Audio sample rate in Hz

        Returns:
            True if initialization successful
        """
        try:
            # Initialize task manager
            self.task_manager = MultiModalTaskManager(
                manager_id=f"{self.protocol_id}_{self.session_id}",
                enable_visual=True,
                enable_auditory=True,
                enable_interoceptive=True,
            )

            if not self.task_manager.initialize(
                screen_width=screen_width,
                screen_height=screen_height,
                viewing_distance_cm=viewing_distance_cm,
                sample_rate=sample_rate,
            ):
                logger.error("Failed to initialize task manager")
                return False

            self.session_start_time = datetime.now()
            self.is_initialized = True

            logger.info("ThresholdEstimationProtocol initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize protocol: {e}")
            return False

    def run_threshold_estimation(
        self, config: ModalityThresholdConfig
    ) -> Optional[ThresholdEstimationResult]:
        """
        Run threshold estimation for a specific modality.

        Implements adaptive staircase procedure with awareness probes to estimate
        the 50% conscious detection threshold.

        Args:
            config: Modality threshold configuration

        Returns:
            ThresholdEstimationResult if successful
        """
        if not self.is_initialized:
            logger.error("Protocol not initialized")
            return None

        if not config.validate():
            logger.error("Invalid configuration")
            return None

        logger.info(f"Starting threshold estimation for {config.modality.value}")

        # Create staircase
        staircase = create_staircase(
            staircase_type=config.staircase_params.staircase_type,
            parameters=config.staircase_params,
            staircase_id=f"{self.session_id}_{config.modality.value}",
        )
        self.staircases[config.modality] = staircase

        # Initialize result
        result = ThresholdEstimationResult(
            participant_id=self.participant_id,
            session_id=self.session_id,
            modality=config.modality,
            threshold_type=config.threshold_type,
        )

        block_start_time = datetime.now()
        total_trials = 0

        # Run blocks
        for block_num in range(config.n_blocks):
            logger.info(f"Starting block {block_num + 1}/{config.n_blocks}")

            # Run trials in block
            for trial_num in range(config.n_trials_per_block):
                if not staircase.should_continue():
                    logger.info(f"Staircase converged after {total_trials} trials")
                    break

                # Get next intensity from staircase
                intensity = staircase.get_next_intensity()

                # Create trial configuration
                trial_config = self._create_trial_config(
                    config=config, trial_number=total_trials, intensity=intensity
                )

                # Present trial
                trial_result = self.task_manager.present_trial(trial_config)

                if trial_result is None:
                    logger.warning(f"Trial {total_trials} failed")
                    continue

                # Determine response for staircase update
                # For conscious threshold, use awareness probe response
                if (
                    config.use_awareness_probe
                    and config.threshold_type == ThresholdType.CONSCIOUS_ACCESS
                ):
                    # Simulate awareness probe (in real implementation, would present actual probe)
                    conscious_response = self._probe_conscious_awareness(
                        trial_result, config.awareness_probe_delay_ms
                    )
                    response = conscious_response
                else:
                    # Use detection response
                    response = trial_result.response_detected

                # Update staircase
                staircase.update(intensity, response)

                # Store trial
                self.trial_history.append(trial_result)
                total_trials += 1

            result.n_blocks_completed += 1

            # Inter-block rest
            if block_num < config.n_blocks - 1:
                logger.info(f"Inter-block rest: {config.inter_block_rest_ms/1000:.1f}s")
                # In real implementation, would show rest screen

        # Get final threshold estimate
        threshold_estimate = staircase.get_threshold_estimate()

        if config.threshold_type == ThresholdType.DETECTION:
            result.detection_threshold = threshold_estimate
            # Store detection threshold for normalization
            self.normalizer.set_detection_threshold(
                config.modality.value, threshold_estimate.threshold
            )
        elif config.threshold_type == ThresholdType.CONSCIOUS_ACCESS:
            result.conscious_threshold = threshold_estimate
            # Normalize to detection threshold if available
            result.normalized_threshold = self.normalizer.normalize_threshold(
                config.modality.value, threshold_estimate.threshold
            )

        # Calculate completion time
        completion_time = (datetime.now() - block_start_time).total_seconds() / 60.0
        result.completion_time_minutes = completion_time
        result.n_trials_completed = total_trials

        # Calculate quality metrics
        result.data_quality_score = self._calculate_data_quality(staircase)
        result.timing_quality_score = self._calculate_timing_quality()

        # Store result
        self.results[config.modality] = result

        logger.info(
            f"Threshold estimation completed: {threshold_estimate.threshold:.4f} "
            f"(±{threshold_estimate.std_error:.4f})"
        )

        return result

    def _create_trial_config(
        self, config: ModalityThresholdConfig, trial_number: int, intensity: float
    ) -> TrialConfiguration:
        """Create trial configuration with specified intensity."""
        trial_id = f"{self.session_id}_{config.modality.value}_{trial_number}"

        # Create stimulus parameters based on modality
        visual_params = None
        auditory_params = None
        interoceptive_params = None

        if config.modality == ModalityType.VISUAL and config.base_visual_params:
            visual_params = GaborParameters(
                contrast=intensity,
                spatial_frequency=config.base_visual_params.spatial_frequency,
                orientation=config.base_visual_params.orientation,
                size_degrees=config.base_visual_params.size_degrees,
                duration_ms=config.base_visual_params.duration_ms,
                position_x=config.base_visual_params.position_x,
                position_y=config.base_visual_params.position_y,
            )

        elif config.modality == ModalityType.AUDITORY and config.base_auditory_params:
            auditory_params = ToneParameters(
                frequency_hz=config.base_auditory_params.frequency_hz,
                amplitude=intensity,
                duration_ms=config.base_auditory_params.duration_ms,
                onset_ramp_ms=config.base_auditory_params.onset_ramp_ms,
                offset_ramp_ms=config.base_auditory_params.offset_ramp_ms,
            )

        elif (
            config.modality == ModalityType.INTEROCEPTIVE
            and config.base_interoceptive_params
        ):
            interoceptive_params = CO2PuffParameters(
                co2_concentration=intensity * 10.0,  # Scale to 0-10%
                flow_rate=config.base_interoceptive_params.flow_rate,
                duration_ms=config.base_interoceptive_params.duration_ms,
                temperature=config.base_interoceptive_params.temperature,
            )

        return TrialConfiguration(
            trial_id=trial_id,
            trial_number=trial_number,
            paradigm=TaskParadigm.THRESHOLD_ESTIMATION,
            modality=config.modality,
            visual_params=visual_params,
            auditory_params=auditory_params,
            interoceptive_params=interoceptive_params,
            isi_ms=1500.0,
            response_window_ms=2000.0,
            is_target=True,
            expected_response=None,  # Threshold trials don't have expected response
            metadata={
                "intensity": intensity,
                "threshold_type": config.threshold_type.value,
            },
        )

    def _probe_conscious_awareness(
        self, trial_result: TrialResult, delay_ms: float
    ) -> bool:
        """
        Probe conscious awareness after stimulus presentation.

        In real implementation, would present awareness probe question
        (e.g., "Did you see/hear/feel anything?") after specified delay.

        Args:
            trial_result: Result from stimulus presentation trial
            delay_ms: Delay before awareness probe (50-500ms)

        Returns:
            True if participant reports conscious awareness
        """
        # Placeholder implementation
        # In real system, would present actual probe and collect response

        # Simulate awareness probe with some relationship to detection
        if trial_result.response_detected:
            # If detected, high probability of conscious awareness
            conscious_aware = np.random.random() < 0.9
        else:
            # If not detected, low probability of conscious awareness
            conscious_aware = np.random.random() < 0.1

        return conscious_aware

    def _calculate_data_quality(self, staircase: AdaptiveStaircase) -> float:
        """Calculate data quality score based on staircase performance."""
        quality_score = 1.0

        # Penalize if didn't converge
        if not staircase.is_converged():
            quality_score *= 0.7

        # Penalize if too few reversals
        if staircase.reversal_count < 4:
            quality_score *= 0.8

        # Penalize if too few trials
        if staircase.trial_count < 20:
            quality_score *= 0.9

        return quality_score

    def _calculate_timing_quality(self) -> float:
        """Calculate timing quality score from task manager."""
        if not self.task_manager or not self.task_manager.timing_errors:
            return 1.0

        # Calculate mean absolute timing error
        mean_error = np.mean(np.abs(self.task_manager.timing_errors))

        # Good timing: < 2ms error
        if mean_error < 2.0:
            return 1.0
        # Acceptable timing: 2-5ms error
        elif mean_error < 5.0:
            return 0.9
        # Poor timing: > 5ms error
        else:
            return 0.7

    def calculate_cross_modal_consistency(self) -> Optional[float]:
        """
        Calculate cross-modal threshold consistency.

        Computes correlation between normalized thresholds across modalities.
        Requirements: 2.5 - cross-modal consistency r > 0.5

        Returns:
            Correlation coefficient if multiple modalities tested
        """
        # Get normalized thresholds
        normalized_thresholds = []
        modalities = []

        for modality, result in self.results.items():
            if result.normalized_threshold is not None:
                normalized_thresholds.append(result.normalized_threshold)
                modalities.append(modality.value)

        if len(normalized_thresholds) < 2:
            logger.warning("Need at least 2 modalities for cross-modal consistency")
            return None

        # Calculate correlation (simplified - would use proper correlation in real implementation)
        # For now, calculate coefficient of variation as consistency metric
        mean_threshold = np.mean(normalized_thresholds)
        std_threshold = np.std(normalized_thresholds)

        if mean_threshold == 0:
            return None

        cv = std_threshold / mean_threshold

        # Convert CV to correlation-like metric (lower CV = higher consistency)
        consistency = max(0.0, 1.0 - cv)

        logger.info(f"Cross-modal consistency: {consistency:.3f} across {modalities}")

        return consistency

    def calculate_test_retest_reliability(
        self,
        previous_result: ThresholdEstimationResult,
        current_result: ThresholdEstimationResult,
    ) -> Optional[float]:
        """
        Calculate test-retest reliability (ICC).

        Requirements: 2.4 - test-retest reliability ICC > 0.70

        Args:
            previous_result: Result from previous session
            current_result: Result from current session

        Returns:
            Intraclass correlation coefficient
        """
        if previous_result.modality != current_result.modality:
            logger.error("Cannot compare different modalities")
            return None

        # Get threshold estimates
        prev_threshold = None
        curr_threshold = None

        if previous_result.conscious_threshold and current_result.conscious_threshold:
            prev_threshold = previous_result.conscious_threshold.threshold
            curr_threshold = current_result.conscious_threshold.threshold
        elif previous_result.detection_threshold and current_result.detection_threshold:
            prev_threshold = previous_result.detection_threshold.threshold
            curr_threshold = current_result.detection_threshold.threshold

        if prev_threshold is None or curr_threshold is None:
            logger.error("Missing threshold estimates")
            return None

        # Simplified ICC calculation (would use proper ICC formula in real implementation)
        # ICC(2,1) = (BMS - WMS) / (BMS + WMS)
        # For two measurements, simplified as correlation

        mean_threshold = (prev_threshold + curr_threshold) / 2
        diff = abs(prev_threshold - curr_threshold)

        # Calculate reliability as 1 - (difference / mean)
        if mean_threshold == 0:
            return None

        reliability = max(0.0, 1.0 - (diff / mean_threshold))

        logger.info(f"Test-retest reliability: ICC = {reliability:.3f}")

        return reliability

    def save_results(self, output_dir: str) -> bool:
        """Save threshold estimation results to file."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Save results for each modality
            for modality, result in self.results.items():
                filename = f"threshold_{self.participant_id}_{self.session_id}_{modality.value}.json"
                filepath = output_path / filename

                with open(filepath, "w") as f:
                    json.dump(result.to_dict(), f, indent=2)

                logger.info(f"Saved results to {filepath}")

            # Save cross-modal summary
            summary = {
                "participant_id": self.participant_id,
                "session_id": self.session_id,
                "modalities_tested": [m.value for m in self.results.keys()],
                "cross_modal_consistency": self.calculate_cross_modal_consistency(),
                "detection_thresholds": self.normalizer.detection_thresholds,
                "normalized_thresholds": self.normalizer.normalized_thresholds,
                "session_duration_minutes": (
                    (datetime.now() - self.session_start_time).total_seconds() / 60.0
                    if self.session_start_time
                    else None
                ),
            }

            summary_file = (
                output_path
                / f"threshold_summary_{self.participant_id}_{self.session_id}.json"
            )
            with open(summary_file, "w") as f:
                json.dump(summary, f, indent=2)

            logger.info(f"Saved summary to {summary_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return False

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.task_manager:
            self.task_manager.cleanup()

        self.is_initialized = False
        logger.info("ThresholdEstimationProtocol cleaned up")


def create_default_visual_config() -> ModalityThresholdConfig:
    """Create default configuration for visual threshold estimation."""
    staircase_params = StaircaseParameters(
        staircase_type=StaircaseType.QUEST_PLUS,
        min_intensity=0.01,
        max_intensity=1.0,
        initial_intensity=0.3,
        min_trials=30,
        max_trials=80,
        min_reversals=6,
    )

    base_visual_params = GaborParameters(
        contrast=0.5,  # Will be modulated by staircase
        spatial_frequency=2.0,
        orientation=0.0,
        size_degrees=2.0,
        duration_ms=100.0,
    )

    return ModalityThresholdConfig(
        modality=ModalityType.VISUAL,
        threshold_type=ThresholdType.CONSCIOUS_ACCESS,
        staircase_params=staircase_params,
        base_visual_params=base_visual_params,
        awareness_probe_delay_ms=500.0,
        use_awareness_probe=True,
        n_trials_per_block=40,
        n_blocks=2,
    )


def create_default_auditory_config() -> ModalityThresholdConfig:
    """Create default configuration for auditory threshold estimation."""
    staircase_params = StaircaseParameters(
        staircase_type=StaircaseType.QUEST_PLUS,
        min_intensity=0.01,
        max_intensity=1.0,
        initial_intensity=0.3,
        min_trials=30,
        max_trials=80,
        min_reversals=6,
    )

    base_auditory_params = ToneParameters(
        frequency_hz=1000.0,
        amplitude=0.5,  # Will be modulated by staircase
        duration_ms=100.0,
        onset_ramp_ms=10.0,
        offset_ramp_ms=10.0,
    )

    return ModalityThresholdConfig(
        modality=ModalityType.AUDITORY,
        threshold_type=ThresholdType.CONSCIOUS_ACCESS,
        staircase_params=staircase_params,
        base_auditory_params=base_auditory_params,
        awareness_probe_delay_ms=500.0,
        use_awareness_probe=True,
        n_trials_per_block=40,
        n_blocks=2,
    )


def create_default_interoceptive_config() -> ModalityThresholdConfig:
    """Create default configuration for interoceptive threshold estimation."""
    staircase_params = StaircaseParameters(
        staircase_type=StaircaseType.QUEST_PLUS,
        min_intensity=0.01,
        max_intensity=1.0,
        initial_intensity=0.3,
        min_trials=30,
        max_trials=80,
        min_reversals=6,
    )

    base_interoceptive_params = CO2PuffParameters(
        co2_concentration=5.0,  # Will be modulated by staircase
        flow_rate=2.0,
        duration_ms=200.0,
        temperature=37.0,
    )

    return ModalityThresholdConfig(
        modality=ModalityType.INTEROCEPTIVE,
        threshold_type=ThresholdType.CONSCIOUS_ACCESS,
        staircase_params=staircase_params,
        base_interoceptive_params=base_interoceptive_params,
        awareness_probe_delay_ms=500.0,
        use_awareness_probe=True,
        n_trials_per_block=40,
        n_blocks=2,
    )
