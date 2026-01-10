"""
Neural Validation Pipeline for Threshold Estimation

Integrates EEG recording with threshold procedures to validate neural signatures
of ignition events. Detects P3b stochastic appearance on threshold trials and
analyzes gamma-band activity correlation.

Requirements: 2.5, 3.1, 3.3
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
import json
from pathlib import Path

# Import neural analysis modules
import sys

sys.path.append(str(Path(__file__).parent.parent))

from neural.eeg_interface import EEGInterface, EEGConfig, ChannelInfo, ChannelType
from neural.erp_analysis import ERPAnalysis, ERPComponents, P3bMetrics
from neural.gamma_synchrony import GammaSynchronyAnalysis, CoherenceMetrics

# Import threshold estimation
from .threshold_estimation_system import (
    ThresholdEstimationProtocol,
    ModalityThresholdConfig,
    ThresholdEstimationResult,
    ThresholdType,
)
from .multi_modal_task_manager import TrialResult, ModalityType

logger = logging.getLogger(__name__)


@dataclass
class NeuralThresholdTrial:
    """Neural data for a single threshold trial."""

    trial_id: str
    trial_number: int

    # Stimulus parameters
    intensity: float
    modality: ModalityType

    # Behavioral response
    detected: bool
    conscious_aware: bool
    reaction_time_ms: Optional[float] = None

    # Neural data
    eeg_data: Optional[np.ndarray] = None  # channels x time
    eeg_timestamps: Optional[np.ndarray] = None
    stimulus_onset_sample: Optional[int] = None

    # ERP components
    erp_components: Optional[ERPComponents] = None
    p3b_metrics: Optional[P3bMetrics] = None

    # Gamma activity
    gamma_power: Optional[float] = None
    gamma_coherence: Optional[float] = None

    # Quality metrics
    artifact_detected: bool = False
    signal_quality: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trial_id": self.trial_id,
            "trial_number": self.trial_number,
            "intensity": self.intensity,
            "modality": self.modality.value,
            "detected": self.detected,
            "conscious_aware": self.conscious_aware,
            "reaction_time_ms": self.reaction_time_ms,
            "p3b_amplitude": self.p3b_metrics.amplitude if self.p3b_metrics else None,
            "p3b_latency": self.p3b_metrics.latency if self.p3b_metrics else None,
            "gamma_power": self.gamma_power,
            "gamma_coherence": self.gamma_coherence,
            "artifact_detected": self.artifact_detected,
            "signal_quality": self.signal_quality,
        }


@dataclass
class NeuralValidationResult:
    """Results from neural validation of threshold estimation."""

    participant_id: str
    session_id: str
    modality: ModalityType

    # Threshold estimates
    behavioral_threshold: float
    neural_threshold: Optional[float] = None

    # P3b stochastic appearance
    p3b_detection_rate_near_threshold: float = 0.0
    p3b_amplitude_threshold_correlation: float = 0.0
    p3b_stochastic_appearance_detected: bool = False

    # Gamma activity
    gamma_power_threshold_correlation: float = 0.0
    gamma_coherence_threshold_correlation: float = 0.0

    # Neural-behavioral correspondence
    p3b_predicts_detection: float = 0.0  # Correlation
    gamma_predicts_detection: float = 0.0

    # Trial data
    trials: List[NeuralThresholdTrial] = field(default_factory=list)
    n_trials_analyzed: int = 0
    n_trials_rejected: int = 0

    # Quality metrics
    overall_signal_quality: float = 1.0
    validation_confidence: float = 0.0

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "participant_id": self.participant_id,
            "session_id": self.session_id,
            "modality": self.modality.value,
            "behavioral_threshold": self.behavioral_threshold,
            "neural_threshold": self.neural_threshold,
            "p3b_detection_rate_near_threshold": self.p3b_detection_rate_near_threshold,
            "p3b_amplitude_threshold_correlation": self.p3b_amplitude_threshold_correlation,
            "p3b_stochastic_appearance_detected": self.p3b_stochastic_appearance_detected,
            "gamma_power_threshold_correlation": self.gamma_power_threshold_correlation,
            "gamma_coherence_threshold_correlation": self.gamma_coherence_threshold_correlation,
            "p3b_predicts_detection": self.p3b_predicts_detection,
            "gamma_predicts_detection": self.gamma_predicts_detection,
            "n_trials_analyzed": self.n_trials_analyzed,
            "n_trials_rejected": self.n_trials_rejected,
            "overall_signal_quality": self.overall_signal_quality,
            "validation_confidence": self.validation_confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class NeuralThresholdValidationPipeline:
    """
    Neural validation pipeline for threshold estimation.

    Integrates EEG recording with psychophysical threshold procedures to validate
    neural signatures of ignition. Detects P3b stochastic appearance on threshold
    trials and analyzes gamma-band activity correlation.

    Requirements: 2.5, 3.1, 3.3
    """

    def __init__(
        self,
        participant_id: str,
        session_id: str,
        pipeline_id: str = "neural_threshold_validation",
    ):
        """
        Initialize neural validation pipeline.

        Args:
            participant_id: Unique participant identifier
            session_id: Unique session identifier
            pipeline_id: Pipeline identifier
        """
        self.participant_id = participant_id
        self.session_id = session_id
        self.pipeline_id = pipeline_id

        # EEG interface
        self.eeg_interface: Optional[EEGInterface] = None

        # Analysis modules
        self.erp_analyzer: Optional[ERPAnalysis] = None
        self.gamma_analyzer: Optional[GammaSynchronyAnalysis] = None

        # Threshold estimation protocol
        self.threshold_protocol: Optional[ThresholdEstimationProtocol] = None

        # Trial storage
        self.neural_trials: List[NeuralThresholdTrial] = []

        # Results
        self.validation_results: Dict[ModalityType, NeuralValidationResult] = {}

        # Configuration
        self.sampling_rate = 1000.0  # Hz
        self.epoch_window = (-200, 800)  # ms relative to stimulus
        self.p3b_channel = "Pz"  # Primary P3b channel
        self.frontal_channels = ["Fz", "F3", "F4"]
        self.posterior_channels = ["Pz", "P3", "P4", "Oz"]

        self.is_initialized = False

        logger.info(
            f"Initialized NeuralThresholdValidationPipeline for participant {participant_id}"
        )

    def initialize(
        self,
        eeg_config: Optional[EEGConfig] = None,
        screen_width: int = 1920,
        screen_height: int = 1080,
    ) -> bool:
        """
        Initialize the pipeline with EEG and threshold estimation systems.

        Args:
            eeg_config: EEG configuration (uses default if None)
            screen_width: Screen width for visual stimuli
            screen_height: Screen height for visual stimuli

        Returns:
            True if initialization successful
        """
        try:
            # Initialize EEG interface
            if eeg_config is None:
                eeg_config = self._create_default_eeg_config()

            self.eeg_interface = EEGInterface(eeg_config)
            self.sampling_rate = eeg_config.sampling_rate

            # Initialize analysis modules
            self.erp_analyzer = ERPAnalysis(sampling_rate=self.sampling_rate)
            self.gamma_analyzer = GammaSynchronyAnalysis(
                sampling_rate=self.sampling_rate
            )

            # Initialize threshold estimation protocol
            self.threshold_protocol = ThresholdEstimationProtocol(
                participant_id=self.participant_id,
                session_id=self.session_id,
                protocol_id=f"{self.pipeline_id}_threshold",
            )

            if not self.threshold_protocol.initialize(
                screen_width=screen_width, screen_height=screen_height
            ):
                logger.error("Failed to initialize threshold protocol")
                return False

            # Register EEG callback for real-time processing
            self.eeg_interface.register_callback(self._process_eeg_data)

            self.is_initialized = True
            logger.info("NeuralThresholdValidationPipeline initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            return False

    def _create_default_eeg_config(self) -> EEGConfig:
        """Create default EEG configuration."""
        # Standard 10-20 system channels
        channels = [
            ChannelInfo("Fz", ChannelType.EEG),
            ChannelInfo("F3", ChannelType.EEG),
            ChannelInfo("F4", ChannelType.EEG),
            ChannelInfo("Cz", ChannelType.EEG),
            ChannelInfo("C3", ChannelType.EEG),
            ChannelInfo("C4", ChannelType.EEG),
            ChannelInfo("Pz", ChannelType.EEG),
            ChannelInfo("P3", ChannelType.EEG),
            ChannelInfo("P4", ChannelType.EEG),
            ChannelInfo("Oz", ChannelType.EEG),
            ChannelInfo("O1", ChannelType.EEG),
            ChannelInfo("O2", ChannelType.EEG),
        ]

        return EEGConfig(
            sampling_rate=1000.0,
            buffer_size=10000,
            channels=channels,
            reference_type="average",
            highpass_freq=0.1,
            lowpass_freq=100.0,
            notch_freq=60.0,
            artifact_threshold=100.0,
            enable_realtime_filtering=True,
        )

    def run_neural_threshold_estimation(
        self, config: ModalityThresholdConfig
    ) -> Optional[NeuralValidationResult]:
        """
        Run threshold estimation with concurrent neural recording.

        Implements integrated psychophysical threshold estimation with EEG recording
        to validate neural signatures of ignition events.

        Args:
            config: Modality threshold configuration

        Returns:
            NeuralValidationResult if successful
        """
        if not self.is_initialized:
            logger.error("Pipeline not initialized")
            return None

        logger.info(f"Starting neural threshold estimation for {config.modality.value}")

        # Start EEG streaming
        self.eeg_interface.start_streaming()

        try:
            # Run threshold estimation protocol
            threshold_result = self.threshold_protocol.run_threshold_estimation(config)

            if threshold_result is None:
                logger.error("Threshold estimation failed")
                return None

            # Stop EEG streaming
            self.eeg_interface.stop_streaming()

            # Process neural data for all trials
            self._process_all_trials(config.modality)

            # Analyze neural-behavioral correspondence
            validation_result = self._analyze_neural_validation(
                config.modality, threshold_result
            )

            # Store result
            self.validation_results[config.modality] = validation_result

            logger.info(
                f"Neural threshold validation completed: "
                f"P3b correlation = {validation_result.p3b_amplitude_threshold_correlation:.3f}, "
                f"Gamma correlation = {validation_result.gamma_power_threshold_correlation:.3f}"
            )

            return validation_result

        except Exception as e:
            logger.error(f"Error during neural threshold estimation: {e}")
            self.eeg_interface.stop_streaming()
            return None

    def _process_eeg_data(
        self, data: np.ndarray, timestamp: float, artifacts: Dict
    ) -> None:
        """
        Real-time EEG data processing callback.

        Args:
            data: EEG data chunk (channels x samples)
            timestamp: Timestamp
            artifacts: Artifact detection results
        """
        # Store data in buffer for later epoch extraction
        # In real implementation, would synchronize with stimulus presentation
        pass

    def _process_all_trials(self, modality: ModalityType) -> None:
        """
        Process neural data for all completed trials.

        Args:
            modality: Modality being tested
        """
        logger.info("Processing neural data for all trials")

        # Get trial history from threshold protocol
        trial_results = self.threshold_protocol.trial_history

        for trial_result in trial_results:
            if trial_result.modality != modality:
                continue

            # Extract epoch around stimulus onset
            neural_trial = self._extract_trial_epoch(trial_result)

            if neural_trial is None:
                continue

            # Analyze ERP components
            self._analyze_trial_erp(neural_trial)

            # Analyze gamma activity
            self._analyze_trial_gamma(neural_trial)

            # Store trial
            self.neural_trials.append(neural_trial)

    def _extract_trial_epoch(
        self, trial_result: TrialResult
    ) -> Optional[NeuralThresholdTrial]:
        """
        Extract EEG epoch for a trial.

        Args:
            trial_result: Trial result from threshold protocol

        Returns:
            NeuralThresholdTrial with EEG data
        """
        # Get EEG data from buffer
        # In real implementation, would use precise timing synchronization
        eeg_data, timestamps = self.eeg_interface.get_buffer_data(n_samples=1000)

        if eeg_data.size == 0:
            logger.warning(f"No EEG data for trial {trial_result.trial_id}")
            return None

        # Find stimulus onset in EEG data
        # Simplified - would use hardware triggers in real implementation
        stimulus_onset_sample = len(timestamps) // 2  # Placeholder

        # Extract epoch
        epoch_start = int(
            stimulus_onset_sample + self.epoch_window[0] * self.sampling_rate / 1000
        )
        epoch_end = int(
            stimulus_onset_sample + self.epoch_window[1] * self.sampling_rate / 1000
        )

        epoch_start = max(0, epoch_start)
        epoch_end = min(eeg_data.shape[1], epoch_end)

        epoch_data = eeg_data[:, epoch_start:epoch_end]
        epoch_timestamps = timestamps[epoch_start:epoch_end]

        # Check for artifacts
        artifacts = self.eeg_interface.artifact_detector.detect_all(epoch_data)
        artifact_detected = np.any(artifacts["any"])

        # Calculate signal quality
        signal_quality = 1.0 if not artifact_detected else 0.5

        # Create neural trial
        neural_trial = NeuralThresholdTrial(
            trial_id=trial_result.trial_id,
            trial_number=trial_result.trial_number,
            intensity=trial_result.metadata.get("intensity", 0.0),
            modality=trial_result.modality,
            detected=trial_result.response_detected,
            conscious_aware=trial_result.response_detected,  # Simplified
            reaction_time_ms=trial_result.reaction_time_ms,
            eeg_data=epoch_data,
            eeg_timestamps=epoch_timestamps,
            stimulus_onset_sample=stimulus_onset_sample - epoch_start,
            artifact_detected=artifact_detected,
            signal_quality=signal_quality,
        )

        return neural_trial

    def _analyze_trial_erp(self, neural_trial: NeuralThresholdTrial) -> None:
        """
        Analyze ERP components for a trial.

        Args:
            neural_trial: Neural trial data
        """
        if neural_trial.eeg_data is None:
            return

        # Get Pz channel (primary P3b channel)
        pz_idx = self._get_channel_index(self.p3b_channel)
        if pz_idx is None:
            logger.warning(f"Channel {self.p3b_channel} not found")
            return

        pz_data = neural_trial.eeg_data[pz_idx, :]

        # Baseline correct
        pz_data = self.erp_analyzer.baseline_correct(
            pz_data[np.newaxis, :], baseline_window=(-200, 0)
        )[0]

        # Filter for ERP analysis
        pz_data = self.erp_analyzer.apply_filter(pz_data, lowpass=30.0, highpass=0.1)

        # Extract all ERP components
        erp_components = self.erp_analyzer.extract_all_components(
            pz_data,
            time_zero_idx=neural_trial.stimulus_onset_sample,
            channel=self.p3b_channel,
        )

        # Extract detailed P3b metrics
        p3b_metrics = self.erp_analyzer.extract_p3b(
            pz_data,
            time_zero_idx=neural_trial.stimulus_onset_sample,
            search_window=(300, 600),
        )

        # Store results
        neural_trial.erp_components = erp_components
        neural_trial.p3b_metrics = p3b_metrics

    def _analyze_trial_gamma(self, neural_trial: NeuralThresholdTrial) -> None:
        """
        Analyze gamma-band activity for a trial.

        Args:
            neural_trial: Neural trial data
        """
        if neural_trial.eeg_data is None:
            return

        # Extract gamma band
        gamma_data = self.gamma_analyzer.extract_gamma_band(neural_trial.eeg_data)

        # Compute gamma power in post-stimulus window (0-500ms)
        post_stim_start = neural_trial.stimulus_onset_sample
        post_stim_end = int(post_stim_start + 500 * self.sampling_rate / 1000)

        post_stim_gamma = gamma_data[:, post_stim_start:post_stim_end]

        # Compute amplitude envelope
        amplitude, _ = self.gamma_analyzer.compute_hilbert_transform(post_stim_gamma)

        # Mean gamma power across channels
        gamma_power = np.mean(amplitude)
        neural_trial.gamma_power = float(gamma_power)

        # Compute frontal-posterior coherence
        frontal_idx = [self._get_channel_index(ch) for ch in self.frontal_channels]
        posterior_idx = [self._get_channel_index(ch) for ch in self.posterior_channels]

        frontal_idx = [i for i in frontal_idx if i is not None]
        posterior_idx = [i for i in posterior_idx if i is not None]

        if frontal_idx and posterior_idx:
            fp_coherence = self.gamma_analyzer.compute_frontal_posterior_coherence(
                post_stim_gamma, frontal_idx, posterior_idx
            )
            neural_trial.gamma_coherence = fp_coherence

    def _get_channel_index(self, channel_name: str) -> Optional[int]:
        """Get index of channel by name."""
        if self.eeg_interface is None:
            return None

        try:
            return self.eeg_interface.active_channels.index(channel_name)
        except ValueError:
            return None

    def _analyze_neural_validation(
        self, modality: ModalityType, threshold_result: ThresholdEstimationResult
    ) -> NeuralValidationResult:
        """
        Analyze neural-behavioral correspondence for validation.

        Requirements: 2.5, 3.1, 3.3

        Args:
            modality: Modality tested
            threshold_result: Behavioral threshold result

        Returns:
            NeuralValidationResult
        """
        # Filter trials for this modality
        modality_trials = [t for t in self.neural_trials if t.modality == modality]

        # Filter out artifact trials
        clean_trials = [t for t in modality_trials if not t.artifact_detected]

        n_analyzed = len(clean_trials)
        n_rejected = len(modality_trials) - n_analyzed

        if n_analyzed < 10:
            logger.warning(f"Too few clean trials for analysis: {n_analyzed}")

        # Extract data for correlation analysis
        intensities = np.array([t.intensity for t in clean_trials])
        p3b_amplitudes = np.array(
            [t.p3b_metrics.amplitude if t.p3b_metrics else 0.0 for t in clean_trials]
        )
        gamma_powers = np.array(
            [t.gamma_power if t.gamma_power else 0.0 for t in clean_trials]
        )
        detected = np.array([t.detected for t in clean_trials])

        # P3b stochastic appearance near threshold
        threshold = (
            threshold_result.conscious_threshold.threshold
            if threshold_result.conscious_threshold
            else 0.5
        )
        near_threshold_mask = np.abs(intensities - threshold) < 0.1

        if np.any(near_threshold_mask):
            near_threshold_trials = [
                t for t, mask in zip(clean_trials, near_threshold_mask) if mask
            ]
            p3b_detection_rate = np.mean(
                [
                    1.0 if t.p3b_metrics and t.p3b_metrics.amplitude > 5.0 else 0.0
                    for t in near_threshold_trials
                ]
            )

            # Check for stochastic appearance (variability in P3b presence)
            p3b_present = [
                t.p3b_metrics and t.p3b_metrics.amplitude > 5.0
                for t in near_threshold_trials
            ]
            p3b_variability = np.std(p3b_present) if len(p3b_present) > 1 else 0.0
            stochastic_appearance = p3b_variability > 0.3  # Threshold for variability
        else:
            p3b_detection_rate = 0.0
            stochastic_appearance = False

        # Correlations with intensity
        from scipy.stats import pearsonr

        if len(intensities) > 3:
            p3b_corr, _ = pearsonr(intensities, p3b_amplitudes)
            gamma_corr, _ = pearsonr(intensities, gamma_powers)
        else:
            p3b_corr = 0.0
            gamma_corr = 0.0

        # Neural prediction of detection
        if len(detected) > 3:
            p3b_pred, _ = pearsonr(p3b_amplitudes, detected.astype(float))
            gamma_pred, _ = pearsonr(gamma_powers, detected.astype(float))
        else:
            p3b_pred = 0.0
            gamma_pred = 0.0

        # Overall signal quality
        overall_quality = (
            np.mean([t.signal_quality for t in clean_trials]) if clean_trials else 0.0
        )

        # Validation confidence based on correlations and sample size
        validation_confidence = min(
            1.0, (abs(p3b_corr) + abs(gamma_corr)) / 2.0 * (n_analyzed / 50.0)
        )

        # Create result
        result = NeuralValidationResult(
            participant_id=self.participant_id,
            session_id=self.session_id,
            modality=modality,
            behavioral_threshold=threshold,
            neural_threshold=None,  # Would estimate from neural data
            p3b_detection_rate_near_threshold=p3b_detection_rate,
            p3b_amplitude_threshold_correlation=p3b_corr,
            p3b_stochastic_appearance_detected=stochastic_appearance,
            gamma_power_threshold_correlation=gamma_corr,
            gamma_coherence_threshold_correlation=0.0,  # Would compute if coherence data available
            p3b_predicts_detection=p3b_pred,
            gamma_predicts_detection=gamma_pred,
            trials=clean_trials,
            n_trials_analyzed=n_analyzed,
            n_trials_rejected=n_rejected,
            overall_signal_quality=overall_quality,
            validation_confidence=validation_confidence,
        )

        return result

    def save_results(self, output_dir: str) -> bool:
        """Save neural validation results to file."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Save results for each modality
            for modality, result in self.validation_results.items():
                filename = f"neural_validation_{self.participant_id}_{self.session_id}_{modality.value}.json"
                filepath = output_path / filename

                with open(filepath, "w") as f:
                    json.dump(result.to_dict(), f, indent=2)

                logger.info(f"Saved neural validation results to {filepath}")

            # Save trial-level data
            trial_data = [trial.to_dict() for trial in self.neural_trials]
            trial_file = (
                output_path
                / f"neural_trials_{self.participant_id}_{self.session_id}.json"
            )
            with open(trial_file, "w") as f:
                json.dump(trial_data, f, indent=2)

            logger.info(f"Saved trial data to {trial_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return False

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.eeg_interface:
            self.eeg_interface.stop_streaming()

        if self.threshold_protocol:
            self.threshold_protocol.cleanup()

        self.is_initialized = False
        logger.info("NeuralThresholdValidationPipeline cleaned up")


def validate_neural_predictions(result: NeuralValidationResult) -> Dict[str, bool]:
    """
    Validate neural predictions against APGI framework requirements.

    Requirements: 3.1, 3.3

    Args:
        result: Neural validation result

    Returns:
        Dictionary of validation checks
    """
    validations = {}

    # Requirement 3.3: Lower θₜ predicts higher P3b amplitude (r > 0.5)
    validations["p3b_threshold_correlation"] = (
        abs(result.p3b_amplitude_threshold_correlation) > 0.5
    )

    # Requirement 3.3: Lower θₜ predicts higher gamma power (r > 0.4)
    validations["gamma_threshold_correlation"] = (
        abs(result.gamma_power_threshold_correlation) > 0.4
    )

    # Requirement 2.5: P3b stochastic appearance on threshold trials
    validations["p3b_stochastic_appearance"] = result.p3b_stochastic_appearance_detected

    # Overall validation
    validations["overall_validation"] = all(
        [
            validations["p3b_threshold_correlation"],
            validations["gamma_threshold_correlation"],
            validations["p3b_stochastic_appearance"],
        ]
    )

    return validations
