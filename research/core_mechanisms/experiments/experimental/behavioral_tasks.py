"""
Core behavioral task classes for parameter estimation.

Implements the three core behavioral tasks for extracting APGI parameters:
1. Detection Task - for θ₀ (baseline ignition threshold) estimation
2. Heartbeat Detection Task - for Πᵢ (interoceptive precision) estimation
3. Dual-Modality Oddball Task - for β (somatic bias) estimation
"""

import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
import logging
from abc import ABC, abstractmethod

from ..adaptive.quest_plus_staircase import QuestPlusStaircase, QuestPlusParameters
from ..adaptive.stimulus_generators import (
    GaborPatchGenerator, ToneGenerator, CO2PuffController, HeartbeatSynchronizer,
    GaborParameters, ToneParameters, CO2PuffParameters, StimulusType
)
from ..adaptive.task_control import (
    PrecisionTimer, ResponseCollector, TaskStateMachine, SessionManager,
    TaskState, ResponseType, ResponseData
)
from ..data.parameter_estimation_models import (
    DetectionTrialResult, HeartbeatTrialResult, OddballTrialResult,
    BehavioralResponse, QualityMetrics, TaskType, StimulusModality
)
from ..data.parameter_estimation_dao import ParameterEstimationDAO

logger = logging.getLogger(__name__)


class BehavioralThresholdCalculator:
    """
    Calculates behavioral threshold (50% detection point) from staircase data.
    
    Estimates the stimulus intensity yielding 50% "seen" responses using
    psychometric function fitting.
    """
    
    def __init__(self):
        self.threshold_estimate = None
        self.threshold_std = None
        self.psychometric_curve = None
    
    def calculate_threshold(self, 
                          intensities: List[float], 
                          responses: List[bool]) -> Tuple[float, float]:
        """
        Calculate 50% detection threshold from trial data.
        
        Args:
            intensities: List of stimulus intensities presented
            responses: List of detection responses (True = detected)
            
        Returns:
            Tuple of (threshold_estimate, threshold_std)
        """
        if len(intensities) < 10:
            logger.warning("Insufficient trials for reliable threshold estimation")
            return 0.5, 0.2
        
        # Simple method: find intensity where hit rate crosses 50%
        # Sort by intensity
        sorted_data = sorted(zip(intensities, responses))
        
        # Calculate running hit rate
        window_size = 10
        thresholds = []
        
        for i in range(len(sorted_data) - window_size):
            window = sorted_data[i:i+window_size]
            window_intensities = [x[0] for x in window]
            window_responses = [x[1] for x in window]
            
            hit_rate = np.mean(window_responses)
            mean_intensity = np.mean(window_intensities)
            
            # Find where hit rate is closest to 50%
            if 0.4 <= hit_rate <= 0.6:
                thresholds.append(mean_intensity)
        
        if thresholds:
            self.threshold_estimate = np.mean(thresholds)
            self.threshold_std = np.std(thresholds) if len(thresholds) > 1 else 0.1
        else:
            # Fallback: use median intensity
            self.threshold_estimate = np.median(intensities)
            self.threshold_std = np.std(intensities) / np.sqrt(len(intensities))
        
        logger.info(f"Behavioral threshold: {self.threshold_estimate:.4f} ± {self.threshold_std:.4f}")
        return self.threshold_estimate, self.threshold_std
    
    def get_psychometric_curve(self, 
                              intensities: np.ndarray) -> np.ndarray:
        """
        Get estimated psychometric curve.
        
        Args:
            intensities: Intensities to evaluate
            
        Returns:
            Detection probabilities for each intensity
        """
        if self.threshold_estimate is None:
            return np.ones_like(intensities) * 0.5
        
        # Simple logistic function
        slope = 5.0  # Steepness parameter
        detection_probs = 1.0 / (1.0 + np.exp(-slope * (intensities - self.threshold_estimate)))
        
        return detection_probs


class P3bCorrelationValidator:
    """
    Validates threshold estimates by correlating with P3b amplitude.
    
    Lower θ₀ should correlate with higher resting P3b amplitude to
    suprathreshold standards (target correlation r > 0.5).
    """
    
    def __init__(self, target_correlation: float = 0.5):
        self.target_correlation = target_correlation
        self.correlation = None
        self.p_value = None
    
    def validate_threshold(self,
                          threshold_estimates: List[float],
                          p3b_amplitudes: List[float]) -> Dict[str, Any]:
        """
        Validate threshold estimates against P3b amplitudes.
        
        Args:
            threshold_estimates: List of threshold estimates
            p3b_amplitudes: List of P3b amplitudes (μV)
            
        Returns:
            Dictionary with validation results
        """
        if len(threshold_estimates) != len(p3b_amplitudes):
            logger.error("Mismatched data lengths for validation")
            return {'valid': False, 'error': 'Mismatched data lengths'}
        
        if len(threshold_estimates) < 10:
            logger.warning("Insufficient data for reliable correlation")
            return {'valid': False, 'error': 'Insufficient data'}
        
        # Calculate Pearson correlation
        self.correlation = np.corrcoef(threshold_estimates, p3b_amplitudes)[0, 1]
        
        # Simple p-value estimation (would use scipy.stats in production)
        n = len(threshold_estimates)
        t_stat = self.correlation * np.sqrt(n - 2) / np.sqrt(1 - self.correlation**2)
        # Approximate p-value
        self.p_value = 2 * (1 - 0.5 * (1 + np.tanh(t_stat / np.sqrt(2))))
        
        is_valid = abs(self.correlation) >= self.target_correlation and self.p_value < 0.05
        
        result = {
            'valid': is_valid,
            'correlation': self.correlation,
            'p_value': self.p_value,
            'target_correlation': self.target_correlation,
            'n_samples': n
        }
        
        logger.info(f"P3b correlation validation: r={self.correlation:.3f}, p={self.p_value:.4f}, valid={is_valid}")
        return result


class DetectionTask:
    """
    Detection task for θ₀ (baseline ignition threshold) estimation.
    
    Presents Gabor patches or tones at varying intensities using adaptive
    staircase procedure. Estimates the stimulus intensity yielding 50%
    detection rate and validates against P3b amplitude.
    """
    
    def __init__(self,
                 task_id: str = "detection_task",
                 modality: str = "visual",
                 n_trials: int = 200,
                 duration_minutes: float = 10.0,
                 participant_id: str = "",
                 session_id: str = "",
                 dao: Optional[ParameterEstimationDAO] = None):
        """
        Initialize detection task.
        
        Args:
            task_id: Unique task identifier
            modality: Stimulus modality ('visual' or 'auditory')
            n_trials: Number of trials to run
            duration_minutes: Target task duration
            participant_id: Participant identifier
            session_id: Session identifier
            dao: Data access object for persistence
        """
        self.task_id = task_id
        self.modality = modality
        self.n_trials = n_trials
        self.duration_minutes = duration_minutes
        self.participant_id = participant_id
        self.session_id = session_id
        self.dao = dao
        
        # Components
        self.staircase = QuestPlusStaircase(
            parameters=QuestPlusParameters(
                stimulus_min=0.01,
                stimulus_max=1.0,
                stimulus_steps=50,
                max_trials=n_trials
            ),
            participant_id=participant_id,
            task_id=task_id
        )
        
        # Stimulus generators
        if modality == "visual":
            self.stimulus_generator = GaborPatchGenerator(f"{task_id}_gabor")
        elif modality == "auditory":
            self.stimulus_generator = ToneGenerator(f"{task_id}_tone")
        else:
            raise ValueError(f"Invalid modality: {modality}")
        
        # Task control
        self.timer = PrecisionTimer(f"{task_id}_timer")
        self.response_collector = ResponseCollector(f"{task_id}_responses")
        self.state_machine = TaskStateMachine(f"{task_id}_state")
        
        # Analysis components
        self.threshold_calculator = BehavioralThresholdCalculator()
        self.p3b_validator = P3bCorrelationValidator()
        
        # Trial data
        self.trials: List[DetectionTrialResult] = []
        self.current_trial = 0
        
        # Results
        self.threshold_estimate = None
        self.threshold_std = None
        self.validation_results = None
        
        logger.info(f"Initialized DetectionTask: {modality} modality, {n_trials} trials")
    
    def initialize(self) -> bool:
        """Initialize task components."""
        try:
            self.state_machine.transition_to(TaskState.INITIALIZING, "Initializing detection task")
            
            # Initialize stimulus generator
            if not self.stimulus_generator.initialize():
                logger.error("Failed to initialize stimulus generator")
                return False
            
            # Initialize staircase
            self.staircase._initialize_parameter_spaces()
            self.staircase._initialize_prior()
            
            # Initialize timer
            self.timer.start_session()
            
            self.state_machine.transition_to(TaskState.READY, "Detection task ready")
            logger.info("Detection task initialized successfully")
            return True
            
        except Exception as e:
            self.state_machine.set_error(f"Initialization failed: {e}")
            logger.error(f"Failed to initialize detection task: {e}")
            return False
    
    def run_trial(self, trial_number: int) -> Optional[DetectionTrialResult]:
        """
        Run a single detection trial.
        
        Args:
            trial_number: Trial number
            
        Returns:
            DetectionTrialResult or None if trial failed
        """
        try:
            # Get stimulus intensity from staircase
            intensity = self.staircase.get_next_intensity()
            
            # Create stimulus parameters
            if self.modality == "visual":
                stimulus_params = GaborParameters(
                    intensity=intensity,
                    contrast=intensity,
                    duration_ms=500.0,
                    spatial_frequency=2.0,
                    orientation=np.random.choice([0, 45, 90, 135]),
                    size_degrees=2.0
                )
            else:  # auditory
                stimulus_params = ToneParameters(
                    intensity=intensity,
                    amplitude=intensity,
                    frequency_hz=1000.0,
                    duration_ms=500.0
                )
            
            # Present stimulus
            stimulus_onset = datetime.now()
            success = self.stimulus_generator.generate_stimulus(stimulus_params)
            
            if not success:
                logger.error(f"Failed to present stimulus for trial {trial_number}")
                return None
            
            # Collect response
            self.response_collector.start_collection(
                stimulus_onset_time=stimulus_onset,
                response_window_ms=2000.0
            )
            
            response = self.response_collector.wait_for_response(timeout_ms=2000.0)
            
            # Handle no response
            if response is None:
                detected = False
                reaction_time = 2000.0
                confidence = None
            else:
                detected = response.response_value
                reaction_time = response.reaction_time_ms
                confidence = response.confidence
            
            # Update staircase
            self.staircase.update(intensity, detected)
            
            # Create behavioral response
            behavioral_response = BehavioralResponse(
                response_time=reaction_time,
                detected=detected,
                confidence=confidence,
                reaction_time_valid=reaction_time < 2000.0
            )
            
            # Create trial result
            trial_result = DetectionTrialResult(
                participant_id=self.participant_id,
                session_id=self.session_id,
                trial_number=trial_number,
                timestamp=stimulus_onset,
                stimulus_parameters=stimulus_params.__dict__,
                stimulus_modality=StimulusModality.VISUAL if self.modality == "visual" else StimulusModality.AUDITORY,
                stimulus_intensity=intensity,
                behavioral_response=behavioral_response,
                contrast_level=intensity,
                staircase_intensity=intensity,
                staircase_reversals=self.staircase.state.reversals
            )
            
            # Add modality-specific data
            if self.modality == "visual":
                trial_result.gabor_orientation = stimulus_params.orientation
            else:
                trial_result.tone_frequency = stimulus_params.frequency_hz
            
            # Save to database if DAO available
            if self.dao:
                try:
                    self.dao.create_trial(trial_result)
                except Exception as e:
                    logger.warning(f"Failed to save trial to database: {e}")
            
            self.trials.append(trial_result)
            
            logger.debug(f"Trial {trial_number}: intensity={intensity:.4f}, detected={detected}, RT={reaction_time:.1f}ms")
            return trial_result
            
        except Exception as e:
            logger.error(f"Error in trial {trial_number}: {e}")
            return None
    
    def run(self) -> bool:
        """
        Run the complete detection task.
        
        Returns:
            True if task completed successfully
        """
        if not self.state_machine.transition_to(TaskState.RUNNING, "Starting detection task"):
            return False
        
        try:
            logger.info(f"Starting detection task: {self.n_trials} trials")
            
            for trial_num in range(1, self.n_trials + 1):
                # Check if staircase has converged
                if self.staircase.is_converged():
                    logger.info(f"Staircase converged at trial {trial_num}")
                    break
                
                # Run trial
                trial_result = self.run_trial(trial_num)
                
                if trial_result is None:
                    logger.warning(f"Trial {trial_num} failed, continuing...")
                    continue
                
                self.current_trial = trial_num
                
                # Progress update every 20 trials
                if trial_num % 20 == 0:
                    progress = (trial_num / self.n_trials) * 100
                    logger.info(f"Progress: {trial_num}/{self.n_trials} ({progress:.1f}%)")
            
            # Calculate threshold
            self._calculate_threshold()
            
            # Transition to completed
            self.state_machine.transition_to(TaskState.COMPLETED, "Detection task completed")
            logger.info(f"Detection task completed: {len(self.trials)} trials")
            return True
            
        except Exception as e:
            self.state_machine.set_error(f"Task execution failed: {e}")
            logger.error(f"Detection task failed: {e}")
            return False
    
    def _calculate_threshold(self) -> None:
        """Calculate behavioral threshold from trial data."""
        if not self.trials:
            logger.warning("No trials available for threshold calculation")
            return
        
        # Extract intensities and responses
        intensities = [trial.stimulus_intensity for trial in self.trials]
        responses = [trial.behavioral_response.detected for trial in self.trials 
                    if trial.behavioral_response]
        
        # Calculate threshold
        self.threshold_estimate, self.threshold_std = self.threshold_calculator.calculate_threshold(
            intensities, responses
        )
        
        # Also get staircase estimate
        staircase_threshold, staircase_std = self.staircase.get_threshold_estimate()
        
        logger.info(f"Threshold estimates - Behavioral: {self.threshold_estimate:.4f} ± {self.threshold_std:.4f}, "
                   f"Staircase: {staircase_threshold:.4f} ± {staircase_std:.4f}")
    
    def validate_with_p3b(self, p3b_amplitudes: List[float]) -> Dict[str, Any]:
        """
        Validate threshold estimates with P3b amplitudes.
        
        Args:
            p3b_amplitudes: List of P3b amplitudes for each trial
            
        Returns:
            Validation results dictionary
        """
        if len(p3b_amplitudes) != len(self.trials):
            logger.error("P3b amplitude count mismatch")
            return {'valid': False, 'error': 'Data length mismatch'}
        
        # Update trial results with P3b data
        for trial, p3b_amp in zip(self.trials, p3b_amplitudes):
            trial.p3b_amplitude = p3b_amp
        
        # Extract threshold estimates (one per trial based on staircase state)
        threshold_estimates = [trial.staircase_intensity for trial in self.trials]
        
        # Validate
        self.validation_results = self.p3b_validator.validate_threshold(
            threshold_estimates, p3b_amplitudes
        )
        
        return self.validation_results
    
    def get_results(self) -> Dict[str, Any]:
        """Get task results summary."""
        if not self.trials:
            return {'error': 'No trials completed'}
        
        # Calculate performance metrics
        hit_rate = np.mean([trial.behavioral_response.detected for trial in self.trials 
                           if trial.behavioral_response])
        
        reaction_times = [trial.behavioral_response.response_time for trial in self.trials 
                         if trial.behavioral_response and trial.behavioral_response.reaction_time_valid]
        mean_rt = np.mean(reaction_times) if reaction_times else 0.0
        
        return {
            'task_id': self.task_id,
            'modality': self.modality,
            'n_trials_completed': len(self.trials),
            'threshold_estimate': self.threshold_estimate,
            'threshold_std': self.threshold_std,
            'hit_rate': hit_rate,
            'mean_reaction_time_ms': mean_rt,
            'staircase_converged': self.staircase.is_converged(),
            'staircase_reversals': self.staircase.state.reversals,
            'validation_results': self.validation_results
        }
    
    def cleanup(self) -> None:
        """Clean up task resources."""
        self.stimulus_generator.cleanup()
        self.response_collector.stop_collection()
        logger.info("Detection task cleaned up")



class DPrimeCalculator:
    """
    Calculates d' (d-prime) for heartbeat detection accuracy.
    
    d' is a measure of sensitivity that accounts for both hits and false alarms.
    """
    
    def __init__(self):
        self.d_prime = None
        self.criterion = None
        self.hit_rate = None
        self.false_alarm_rate = None
    
    def calculate_d_prime(self,
                         synchronous_trials: List[bool],
                         synchronous_responses: List[bool],
                         asynchronous_trials: List[bool],
                         asynchronous_responses: List[bool]) -> float:
        """
        Calculate d' for heartbeat detection.
        
        Args:
            synchronous_trials: Indices of synchronous trials
            synchronous_responses: Responses for synchronous trials (True = detected as sync)
            asynchronous_trials: Indices of asynchronous trials
            asynchronous_responses: Responses for asynchronous trials
            
        Returns:
            d' value
        """
        # Calculate hit rate (correct detection of synchronous)
        hits = sum(synchronous_responses)
        n_sync = len(synchronous_responses)
        self.hit_rate = hits / n_sync if n_sync > 0 else 0.5
        
        # Calculate false alarm rate (incorrect detection of asynchronous as synchronous)
        false_alarms = sum(asynchronous_responses)
        n_async = len(asynchronous_responses)
        self.false_alarm_rate = false_alarms / n_async if n_async > 0 else 0.5
        
        # Adjust for extreme values (0 or 1)
        self.hit_rate = np.clip(self.hit_rate, 0.01, 0.99)
        self.false_alarm_rate = np.clip(self.false_alarm_rate, 0.01, 0.99)
        
        # Calculate d' using inverse normal CDF
        from scipy.stats import norm
        self.d_prime = norm.ppf(self.hit_rate) - norm.ppf(self.false_alarm_rate)
        
        # Calculate criterion (response bias)
        self.criterion = -0.5 * (norm.ppf(self.hit_rate) + norm.ppf(self.false_alarm_rate))
        
        logger.info(f"d' = {self.d_prime:.3f}, criterion = {self.criterion:.3f}, "
                   f"hit rate = {self.hit_rate:.3f}, FA rate = {self.false_alarm_rate:.3f}")
        
        return self.d_prime


class ConfidenceAnalyzer:
    """
    Analyzes confidence ratings for metacognitive assessment.
    
    Examines the relationship between confidence and accuracy to assess
    metacognitive awareness of interoceptive signals.
    """
    
    def __init__(self):
        self.confidence_accuracy_correlation = None
        self.mean_confidence_correct = None
        self.mean_confidence_incorrect = None
    
    def analyze_confidence(self,
                          accuracies: List[bool],
                          confidences: List[float]) -> Dict[str, Any]:
        """
        Analyze confidence ratings.
        
        Args:
            accuracies: List of trial accuracies (True = correct)
            confidences: List of confidence ratings (0-1)
            
        Returns:
            Dictionary with confidence analysis results
        """
        if len(accuracies) != len(confidences):
            logger.error("Mismatched data lengths")
            return {'error': 'Mismatched data lengths'}
        
        # Calculate correlation between confidence and accuracy
        self.confidence_accuracy_correlation = np.corrcoef(accuracies, confidences)[0, 1]
        
        # Calculate mean confidence for correct vs incorrect trials
        correct_confidences = [conf for acc, conf in zip(accuracies, confidences) if acc]
        incorrect_confidences = [conf for acc, conf in zip(accuracies, confidences) if not acc]
        
        self.mean_confidence_correct = np.mean(correct_confidences) if correct_confidences else 0.0
        self.mean_confidence_incorrect = np.mean(incorrect_confidences) if incorrect_confidences else 0.0
        
        # Calculate metacognitive sensitivity (difference in confidence)
        metacognitive_sensitivity = self.mean_confidence_correct - self.mean_confidence_incorrect
        
        result = {
            'confidence_accuracy_correlation': self.confidence_accuracy_correlation,
            'mean_confidence_correct': self.mean_confidence_correct,
            'mean_confidence_incorrect': self.mean_confidence_incorrect,
            'metacognitive_sensitivity': metacognitive_sensitivity,
            'n_trials': len(accuracies)
        }
        
        logger.info(f"Confidence analysis: r={self.confidence_accuracy_correlation:.3f}, "
                   f"metacognitive sensitivity={metacognitive_sensitivity:.3f}")
        
        return result


class AdaptiveAsynchronyAdjuster:
    """
    Adjusts asynchrony window for poor performers (d' < 0.5).
    
    Increases the temporal offset between heartbeat and tone to make
    the task easier for participants with low interoceptive sensitivity.
    """
    
    def __init__(self, 
                 initial_asynchrony_ms: float = 300.0,
                 min_asynchrony_ms: float = 200.0,
                 max_asynchrony_ms: float = 600.0,
                 adjustment_step_ms: float = 50.0):
        """
        Initialize adaptive asynchrony adjuster.
        
        Args:
            initial_asynchrony_ms: Initial asynchrony window
            min_asynchrony_ms: Minimum asynchrony
            max_asynchrony_ms: Maximum asynchrony
            adjustment_step_ms: Step size for adjustments
        """
        self.current_asynchrony_ms = initial_asynchrony_ms
        self.min_asynchrony_ms = min_asynchrony_ms
        self.max_asynchrony_ms = max_asynchrony_ms
        self.adjustment_step_ms = adjustment_step_ms
        
        self.adjustment_history: List[Tuple[float, float]] = []  # (d_prime, asynchrony)
    
    def adjust_asynchrony(self, current_d_prime: float) -> float:
        """
        Adjust asynchrony based on current performance.
        
        Args:
            current_d_prime: Current d' value
            
        Returns:
            New asynchrony value in milliseconds
        """
        # Record current state
        self.adjustment_history.append((current_d_prime, self.current_asynchrony_ms))
        
        # Adjust based on performance
        if current_d_prime < 0.5:
            # Poor performance: increase asynchrony (make easier)
            self.current_asynchrony_ms = min(
                self.current_asynchrony_ms + self.adjustment_step_ms,
                self.max_asynchrony_ms
            )
            logger.info(f"Increasing asynchrony to {self.current_asynchrony_ms:.1f}ms (d'={current_d_prime:.3f})")
        elif current_d_prime > 1.5:
            # Good performance: decrease asynchrony (make harder)
            self.current_asynchrony_ms = max(
                self.current_asynchrony_ms - self.adjustment_step_ms,
                self.min_asynchrony_ms
            )
            logger.info(f"Decreasing asynchrony to {self.current_asynchrony_ms:.1f}ms (d'={current_d_prime:.3f})")
        
        return self.current_asynchrony_ms
    
    def get_asynchrony(self) -> float:
        """Get current asynchrony value."""
        return self.current_asynchrony_ms


class HeartbeatDetectionTask:
    """
    Heartbeat detection task for Πᵢ (interoceptive precision) estimation.
    
    Presents auditory tones that are either synchronous or asynchronous with
    heartbeat. Participants judge synchronization and provide confidence ratings.
    Integrates pupillometry and HEP extraction for neural priors.
    """
    
    def __init__(self,
                 task_id: str = "heartbeat_detection_task",
                 n_trials: int = 60,
                 duration_minutes: float = 8.0,
                 participant_id: str = "",
                 session_id: str = "",
                 dao: Optional[ParameterEstimationDAO] = None):
        """
        Initialize heartbeat detection task.
        
        Args:
            task_id: Unique task identifier
            n_trials: Number of trials to run
            duration_minutes: Target task duration
            participant_id: Participant identifier
            session_id: Session identifier
            dao: Data access object for persistence
        """
        self.task_id = task_id
        self.n_trials = n_trials
        self.duration_minutes = duration_minutes
        self.participant_id = participant_id
        self.session_id = session_id
        self.dao = dao
        
        # Components
        self.heartbeat_synchronizer = HeartbeatSynchronizer(f"{task_id}_sync")
        self.tone_generator = ToneGenerator(f"{task_id}_tone")
        
        # Task control
        self.timer = PrecisionTimer(f"{task_id}_timer")
        self.response_collector = ResponseCollector(f"{task_id}_responses")
        self.state_machine = TaskStateMachine(f"{task_id}_state")
        
        # Analysis components
        self.d_prime_calculator = DPrimeCalculator()
        self.confidence_analyzer = ConfidenceAnalyzer()
        self.asynchrony_adjuster = AdaptiveAsynchronyAdjuster()
        
        # Trial data
        self.trials: List[HeartbeatTrialResult] = []
        self.current_trial = 0
        
        # Results
        self.d_prime = None
        self.confidence_analysis = None
        
        logger.info(f"Initialized HeartbeatDetectionTask: {n_trials} trials")
    
    def initialize(self) -> bool:
        """Initialize task components."""
        try:
            self.state_machine.transition_to(TaskState.INITIALIZING, "Initializing heartbeat detection task")
            
            # Initialize heartbeat synchronizer
            if not self.heartbeat_synchronizer.initialize():
                logger.error("Failed to initialize heartbeat synchronizer")
                return False
            
            # Initialize tone generator
            if not self.tone_generator.initialize():
                logger.error("Failed to initialize tone generator")
                return False
            
            # Connect synchronizer to tone generator
            self.tone_generator.set_heartbeat_synchronizer(self.heartbeat_synchronizer)
            
            # Initialize timer
            self.timer.start_session()
            
            self.state_machine.transition_to(TaskState.READY, "Heartbeat detection task ready")
            logger.info("Heartbeat detection task initialized successfully")
            return True
            
        except Exception as e:
            self.state_machine.set_error(f"Initialization failed: {e}")
            logger.error(f"Failed to initialize heartbeat detection task: {e}")
            return False
    
    def run_trial(self, trial_number: int) -> Optional[HeartbeatTrialResult]:
        """
        Run a single heartbeat detection trial.
        
        Args:
            trial_number: Trial number
            
        Returns:
            HeartbeatTrialResult or None if trial failed
        """
        try:
            # Determine if trial is synchronous or asynchronous
            is_synchronous = np.random.choice([True, False])
            
            # Get current asynchrony setting
            asynchrony_ms = self.asynchrony_adjuster.get_asynchrony()
            
            # Wait for R-peak
            r_peak_time = self.heartbeat_synchronizer.wait_for_r_peak(timeout_ms=3000.0)
            
            if r_peak_time is None:
                logger.error(f"Failed to detect R-peak for trial {trial_number}")
                return None
            
            # Calculate tone delay
            if is_synchronous:
                tone_delay_ms = 0.0
            else:
                # Random delay within asynchrony window
                tone_delay_ms = np.random.uniform(asynchrony_ms - 50, asynchrony_ms + 50)
            
            # Create tone parameters
            tone_params = ToneParameters(
                frequency_hz=1000.0,
                amplitude=0.7,
                duration_ms=50.0,
                sync_to_heartbeat=True,
                heartbeat_delay_ms=tone_delay_ms
            )
            
            # Present tone
            stimulus_onset = datetime.now()
            success = self.tone_generator.generate_stimulus(tone_params)
            
            if not success:
                logger.error(f"Failed to present tone for trial {trial_number}")
                return None
            
            # Collect response
            self.response_collector.start_collection(
                stimulus_onset_time=stimulus_onset,
                response_window_ms=3000.0
            )
            
            response = self.response_collector.wait_for_response(timeout_ms=3000.0)
            
            # Handle no response
            if response is None:
                detected_as_sync = False
                reaction_time = 3000.0
                confidence = None
            else:
                detected_as_sync = response.response_value
                reaction_time = response.reaction_time_ms
                confidence = response.confidence
            
            # Collect confidence rating if not already provided
            if confidence is None:
                confidence = self.response_collector.collect_confidence_rating(
                    prompt="How confident are you?",
                    scale_min=0.0,
                    scale_max=1.0
                )
            
            # Get cardiac measurements
            heart_rate = self.heartbeat_synchronizer.get_heart_rate()
            rr_interval = self.heartbeat_synchronizer.get_rr_interval()
            
            # Create behavioral response
            behavioral_response = BehavioralResponse(
                response_time=reaction_time,
                detected=detected_as_sync,
                confidence=confidence,
                reaction_time_valid=reaction_time < 3000.0
            )
            
            # Create trial result
            trial_result = HeartbeatTrialResult(
                participant_id=self.participant_id,
                session_id=self.session_id,
                trial_number=trial_number,
                timestamp=stimulus_onset,
                stimulus_parameters=tone_params.__dict__,
                stimulus_modality=StimulusModality.AUDITORY,
                stimulus_intensity=tone_params.amplitude,
                behavioral_response=behavioral_response,
                is_synchronous=is_synchronous,
                tone_delay_ms=tone_delay_ms,
                r_peak_timestamp=r_peak_time,
                heart_rate=heart_rate or 0.0,
                rr_interval=rr_interval or 0.0
            )
            
            # Save to database if DAO available
            if self.dao:
                try:
                    self.dao.create_trial(trial_result)
                except Exception as e:
                    logger.warning(f"Failed to save trial to database: {e}")
            
            self.trials.append(trial_result)
            
            logger.debug(f"Trial {trial_number}: sync={is_synchronous}, response={detected_as_sync}, "
                        f"confidence={confidence:.2f if confidence else 0}, RT={reaction_time:.1f}ms")
            return trial_result
            
        except Exception as e:
            logger.error(f"Error in trial {trial_number}: {e}")
            return None
    
    def run(self) -> bool:
        """
        Run the complete heartbeat detection task.
        
        Returns:
            True if task completed successfully
        """
        if not self.state_machine.transition_to(TaskState.RUNNING, "Starting heartbeat detection task"):
            return False
        
        try:
            logger.info(f"Starting heartbeat detection task: {self.n_trials} trials")
            
            for trial_num in range(1, self.n_trials + 1):
                # Run trial
                trial_result = self.run_trial(trial_num)
                
                if trial_result is None:
                    logger.warning(f"Trial {trial_num} failed, continuing...")
                    continue
                
                self.current_trial = trial_num
                
                # Adaptive adjustment every 10 trials
                if trial_num % 10 == 0 and trial_num >= 20:
                    self._update_adaptive_parameters()
                
                # Progress update every 10 trials
                if trial_num % 10 == 0:
                    progress = (trial_num / self.n_trials) * 100
                    logger.info(f"Progress: {trial_num}/{self.n_trials} ({progress:.1f}%)")
            
            # Calculate final metrics
            self._calculate_metrics()
            
            # Transition to completed
            self.state_machine.transition_to(TaskState.COMPLETED, "Heartbeat detection task completed")
            logger.info(f"Heartbeat detection task completed: {len(self.trials)} trials")
            return True
            
        except Exception as e:
            self.state_machine.set_error(f"Task execution failed: {e}")
            logger.error(f"Heartbeat detection task failed: {e}")
            return False
    
    def _update_adaptive_parameters(self) -> None:
        """Update adaptive parameters based on recent performance."""
        # Calculate d' from recent trials
        recent_trials = self.trials[-20:]  # Last 20 trials
        
        sync_responses = [trial.behavioral_response.detected for trial in recent_trials 
                         if trial.is_synchronous and trial.behavioral_response]
        async_responses = [trial.behavioral_response.detected for trial in recent_trials 
                          if not trial.is_synchronous and trial.behavioral_response]
        
        if len(sync_responses) >= 5 and len(async_responses) >= 5:
            d_prime = self.d_prime_calculator.calculate_d_prime(
                [True] * len(sync_responses), sync_responses,
                [False] * len(async_responses), async_responses
            )
            
            # Adjust asynchrony if needed
            self.asynchrony_adjuster.adjust_asynchrony(d_prime)
    
    def _calculate_metrics(self) -> None:
        """Calculate final performance metrics."""
        if not self.trials:
            logger.warning("No trials available for metric calculation")
            return
        
        # Separate synchronous and asynchronous trials
        sync_trials = [trial for trial in self.trials if trial.is_synchronous]
        async_trials = [trial for trial in self.trials if not trial.is_synchronous]
        
        sync_responses = [trial.behavioral_response.detected for trial in sync_trials 
                         if trial.behavioral_response]
        async_responses = [trial.behavioral_response.detected for trial in async_trials 
                          if trial.behavioral_response]
        
        # Calculate d'
        if sync_responses and async_responses:
            self.d_prime = self.d_prime_calculator.calculate_d_prime(
                [True] * len(sync_responses), sync_responses,
                [False] * len(async_responses), async_responses
            )
        
        # Analyze confidence
        accuracies = []
        confidences = []
        
        for trial in self.trials:
            if trial.behavioral_response and trial.behavioral_response.confidence is not None:
                # Accuracy: correct identification of synchrony
                correct = (trial.is_synchronous == trial.behavioral_response.detected)
                accuracies.append(correct)
                confidences.append(trial.behavioral_response.confidence)
        
        if accuracies and confidences:
            self.confidence_analysis = self.confidence_analyzer.analyze_confidence(
                accuracies, confidences
            )
    
    def integrate_pupillometry(self, pupil_data: List[Dict[str, float]]) -> None:
        """
        Integrate pupillometry data with trial results.
        
        Args:
            pupil_data: List of pupil measurements for each trial
        """
        if len(pupil_data) != len(self.trials):
            logger.error("Pupil data count mismatch")
            return
        
        for trial, pupil in zip(self.trials, pupil_data):
            trial.pupil_baseline = pupil.get('baseline', None)
            trial.pupil_dilation_peak = pupil.get('peak', None)
            trial.pupil_time_to_peak = pupil.get('time_to_peak', None)
        
        logger.info("Pupillometry data integrated")
    
    def integrate_hep(self, hep_amplitudes: List[float]) -> None:
        """
        Integrate HEP (heartbeat-evoked potential) data.
        
        Args:
            hep_amplitudes: List of HEP amplitudes for each trial
        """
        if len(hep_amplitudes) != len(self.trials):
            logger.error("HEP data count mismatch")
            return
        
        for trial, hep_amp in zip(self.trials, hep_amplitudes):
            trial.hep_amplitude = hep_amp
        
        logger.info("HEP data integrated")
    
    def get_results(self) -> Dict[str, Any]:
        """Get task results summary."""
        if not self.trials:
            return {'error': 'No trials completed'}
        
        # Calculate accuracy
        correct_trials = sum(1 for trial in self.trials 
                           if trial.behavioral_response and 
                           trial.is_synchronous == trial.behavioral_response.detected)
        accuracy = correct_trials / len(self.trials)
        
        # Calculate mean reaction time
        reaction_times = [trial.behavioral_response.response_time for trial in self.trials 
                         if trial.behavioral_response and trial.behavioral_response.reaction_time_valid]
        mean_rt = np.mean(reaction_times) if reaction_times else 0.0
        
        return {
            'task_id': self.task_id,
            'n_trials_completed': len(self.trials),
            'd_prime': self.d_prime,
            'accuracy': accuracy,
            'mean_reaction_time_ms': mean_rt,
            'confidence_analysis': self.confidence_analysis,
            'final_asynchrony_ms': self.asynchrony_adjuster.get_asynchrony()
        }
    
    def cleanup(self) -> None:
        """Clean up task resources."""
        self.heartbeat_synchronizer.cleanup()
        self.tone_generator.cleanup()
        self.response_collector.stop_collection()
        logger.info("Heartbeat detection task cleaned up")



class StimulusCalibrator:
    """
    Calibrates stimuli to ensure Πₑ ≈ Πᵢ through separate staircase procedures.
    
    Runs brief staircase procedures for both interoceptive and exteroceptive
    stimuli to match their detection precision.
    """
    
    def __init__(self):
        self.interoceptive_threshold = None
        self.exteroceptive_threshold = None
        self.calibration_complete = False
    
    def calibrate_interoceptive(self,
                                stimulus_generator,
                                n_trials: int = 30) -> float:
        """
        Calibrate interoceptive stimulus intensity.
        
        Args:
            stimulus_generator: Interoceptive stimulus generator (CO2 or heartbeat flash)
            n_trials: Number of calibration trials
            
        Returns:
            Calibrated threshold intensity
        """
        logger.info("Calibrating interoceptive stimulus...")
        
        # Create staircase for calibration
        staircase = QuestPlusStaircase(
            parameters=QuestPlusParameters(
                stimulus_min=0.01,
                stimulus_max=1.0,
                max_trials=n_trials
            ),
            task_id="intero_calibration"
        )
        
        # Run calibration trials (simplified - would need actual implementation)
        for trial in range(n_trials):
            intensity = staircase.get_next_intensity()
            
            # Simulate response (would be actual participant response)
            detected = np.random.random() < (intensity * 0.8 + 0.1)
            
            staircase.update(intensity, detected)
            
            if staircase.is_converged():
                break
        
        self.interoceptive_threshold, _ = staircase.get_threshold_estimate()
        logger.info(f"Interoceptive threshold: {self.interoceptive_threshold:.4f}")
        
        return self.interoceptive_threshold
    
    def calibrate_exteroceptive(self,
                                stimulus_generator,
                                n_trials: int = 30) -> float:
        """
        Calibrate exteroceptive stimulus intensity.
        
        Args:
            stimulus_generator: Exteroceptive stimulus generator (Gabor or tone)
            n_trials: Number of calibration trials
            
        Returns:
            Calibrated threshold intensity
        """
        logger.info("Calibrating exteroceptive stimulus...")
        
        # Create staircase for calibration
        staircase = QuestPlusStaircase(
            parameters=QuestPlusParameters(
                stimulus_min=0.01,
                stimulus_max=1.0,
                max_trials=n_trials
            ),
            task_id="extero_calibration"
        )
        
        # Run calibration trials (simplified - would need actual implementation)
        for trial in range(n_trials):
            intensity = staircase.get_next_intensity()
            
            # Simulate response (would be actual participant response)
            detected = np.random.random() < (intensity * 0.8 + 0.1)
            
            staircase.update(intensity, detected)
            
            if staircase.is_converged():
                break
        
        self.exteroceptive_threshold, _ = staircase.get_threshold_estimate()
        logger.info(f"Exteroceptive threshold: {self.exteroceptive_threshold:.4f}")
        
        return self.exteroceptive_threshold
    
    def run_calibration(self,
                       intero_generator,
                       extero_generator,
                       n_trials_per_modality: int = 30) -> Tuple[float, float]:
        """
        Run complete calibration for both modalities.
        
        Args:
            intero_generator: Interoceptive stimulus generator
            extero_generator: Exteroceptive stimulus generator
            n_trials_per_modality: Trials per modality
            
        Returns:
            Tuple of (interoceptive_threshold, exteroceptive_threshold)
        """
        self.interoceptive_threshold = self.calibrate_interoceptive(
            intero_generator, n_trials_per_modality
        )
        
        self.exteroceptive_threshold = self.calibrate_exteroceptive(
            extero_generator, n_trials_per_modality
        )
        
        self.calibration_complete = True
        
        logger.info(f"Calibration complete: Πᵢ threshold={self.interoceptive_threshold:.4f}, "
                   f"Πₑ threshold={self.exteroceptive_threshold:.4f}")
        
        return self.interoceptive_threshold, self.exteroceptive_threshold


class InteroceptiveDeviantGenerator:
    """
    Generates interoceptive deviant stimuli using CO2 puffs or heartbeat flashes.
    """
    
    def __init__(self, 
                 generator_type: str = "co2",
                 intensity: float = 0.5):
        """
        Initialize interoceptive deviant generator.
        
        Args:
            generator_type: Type of generator ('co2' or 'heartbeat_flash')
            intensity: Stimulus intensity
        """
        self.generator_type = generator_type
        self.intensity = intensity
        
        if generator_type == "co2":
            self.generator = CO2PuffController("intero_deviant_co2")
        else:
            # Heartbeat flash would use visual generator with cardiac sync
            self.generator = GaborPatchGenerator("intero_deviant_flash")
        
        logger.info(f"Initialized InteroceptiveDeviantGenerator: {generator_type}")
    
    def initialize(self) -> bool:
        """Initialize the generator."""
        return self.generator.initialize()
    
    def generate_deviant(self, intensity: Optional[float] = None) -> bool:
        """
        Generate interoceptive deviant stimulus.
        
        Args:
            intensity: Override intensity (uses default if None)
            
        Returns:
            True if stimulus generated successfully
        """
        stim_intensity = intensity if intensity is not None else self.intensity
        
        if self.generator_type == "co2":
            params = CO2PuffParameters(
                intensity=stim_intensity,
                co2_concentration=10.0,
                duration_ms=300.0,
                flow_rate=2.0
            )
        else:
            # Heartbeat flash parameters
            params = GaborParameters(
                intensity=stim_intensity,
                contrast=stim_intensity,
                duration_ms=100.0,
                size_degrees=3.0
            )
        
        return self.generator.generate_stimulus(params)
    
    def cleanup(self) -> None:
        """Clean up generator resources."""
        self.generator.cleanup()


class ExteroceptiveDeviantGenerator:
    """
    Generates exteroceptive deviant stimuli using Gabor patches or tones.
    """
    
    def __init__(self,
                 generator_type: str = "visual",
                 intensity: float = 0.5):
        """
        Initialize exteroceptive deviant generator.
        
        Args:
            generator_type: Type of generator ('visual' or 'auditory')
            intensity: Stimulus intensity
        """
        self.generator_type = generator_type
        self.intensity = intensity
        
        if generator_type == "visual":
            self.generator = GaborPatchGenerator("extero_deviant_gabor")
            self.standard_orientation = 0.0
            self.deviant_orientation = 45.0
        else:
            self.generator = ToneGenerator("extero_deviant_tone")
            self.standard_frequency = 1000.0
            self.deviant_frequency = 1200.0
        
        logger.info(f"Initialized ExteroceptiveDeviantGenerator: {generator_type}")
    
    def initialize(self) -> bool:
        """Initialize the generator."""
        return self.generator.initialize()
    
    def generate_standard(self, intensity: Optional[float] = None) -> bool:
        """
        Generate standard (non-deviant) stimulus.
        
        Args:
            intensity: Override intensity (uses default if None)
            
        Returns:
            True if stimulus generated successfully
        """
        stim_intensity = intensity if intensity is not None else self.intensity
        
        if self.generator_type == "visual":
            params = GaborParameters(
                intensity=stim_intensity,
                contrast=stim_intensity,
                orientation=self.standard_orientation,
                duration_ms=500.0,
                size_degrees=2.0
            )
        else:
            params = ToneParameters(
                intensity=stim_intensity,
                amplitude=stim_intensity,
                frequency_hz=self.standard_frequency,
                duration_ms=500.0
            )
        
        return self.generator.generate_stimulus(params)
    
    def generate_deviant(self, intensity: Optional[float] = None) -> bool:
        """
        Generate deviant stimulus.
        
        Args:
            intensity: Override intensity (uses default if None)
            
        Returns:
            True if stimulus generated successfully
        """
        stim_intensity = intensity if intensity is not None else self.intensity
        
        if self.generator_type == "visual":
            params = GaborParameters(
                intensity=stim_intensity,
                contrast=stim_intensity,
                orientation=self.deviant_orientation,
                duration_ms=500.0,
                size_degrees=2.0
            )
        else:
            params = ToneParameters(
                intensity=stim_intensity,
                amplitude=stim_intensity,
                frequency_hz=self.deviant_frequency,
                duration_ms=500.0
            )
        
        return self.generator.generate_stimulus(params)
    
    def cleanup(self) -> None:
        """Clean up generator resources."""
        self.generator.cleanup()


class P3bRatioCalculator:
    """
    Calculates P3b ratio (interoceptive/exteroceptive) for β estimation.
    
    Computes the ratio of P3b amplitudes to interoceptive vs exteroceptive
    deviants under neutral context.
    """
    
    def __init__(self):
        self.interoceptive_p3b_mean = None
        self.exteroceptive_p3b_mean = None
        self.p3b_ratio = None
    
    def calculate_ratio(self,
                       interoceptive_p3b: List[float],
                       exteroceptive_p3b: List[float]) -> float:
        """
        Calculate P3b ratio.
        
        Args:
            interoceptive_p3b: List of P3b amplitudes to interoceptive deviants
            exteroceptive_p3b: List of P3b amplitudes to exteroceptive deviants
            
        Returns:
            P3b ratio (interoceptive/exteroceptive)
        """
        if not interoceptive_p3b or not exteroceptive_p3b:
            logger.error("Insufficient P3b data for ratio calculation")
            return 1.0
        
        self.interoceptive_p3b_mean = np.mean(interoceptive_p3b)
        self.exteroceptive_p3b_mean = np.mean(exteroceptive_p3b)
        
        # Avoid division by zero
        if self.exteroceptive_p3b_mean == 0:
            logger.warning("Exteroceptive P3b mean is zero, using ratio of 1.0")
            self.p3b_ratio = 1.0
        else:
            self.p3b_ratio = self.interoceptive_p3b_mean / self.exteroceptive_p3b_mean
        
        logger.info(f"P3b ratio: {self.p3b_ratio:.3f} "
                   f"(intero={self.interoceptive_p3b_mean:.2f}μV, "
                   f"extero={self.exteroceptive_p3b_mean:.2f}μV)")
        
        return self.p3b_ratio
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed P3b statistics."""
        return {
            'interoceptive_p3b_mean': self.interoceptive_p3b_mean,
            'exteroceptive_p3b_mean': self.exteroceptive_p3b_mean,
            'p3b_ratio': self.p3b_ratio
        }


class DualModalityOddballTask:
    """
    Dual-modality oddball task for β (somatic bias) estimation.
    
    Presents precision-matched interoceptive and exteroceptive deviants
    among standard stimuli. Calculates β from the ratio of P3b amplitudes
    to interoceptive vs exteroceptive deviants.
    """
    
    def __init__(self,
                 task_id: str = "oddball_task",
                 n_trials: int = 120,
                 duration_minutes: float = 12.0,
                 deviant_probability: float = 0.2,
                 participant_id: str = "",
                 session_id: str = "",
                 dao: Optional[ParameterEstimationDAO] = None):
        """
        Initialize dual-modality oddball task.
        
        Args:
            task_id: Unique task identifier
            n_trials: Number of trials to run
            duration_minutes: Target task duration
            deviant_probability: Probability of deviant trials
            participant_id: Participant identifier
            session_id: Session identifier
            dao: Data access object for persistence
        """
        self.task_id = task_id
        self.n_trials = n_trials
        self.duration_minutes = duration_minutes
        self.deviant_probability = deviant_probability
        self.participant_id = participant_id
        self.session_id = session_id
        self.dao = dao
        
        # Components
        self.intero_generator = InteroceptiveDeviantGenerator("co2")
        self.extero_generator = ExteroceptiveDeviantGenerator("visual")
        self.calibrator = StimulusCalibrator()
        
        # Task control
        self.timer = PrecisionTimer(f"{task_id}_timer")
        self.response_collector = ResponseCollector(f"{task_id}_responses")
        self.state_machine = TaskStateMachine(f"{task_id}_state")
        
        # Analysis components
        self.p3b_calculator = P3bRatioCalculator()
        
        # Trial data
        self.trials: List[OddballTrialResult] = []
        self.current_trial = 0
        
        # Calibration results
        self.intero_threshold = None
        self.extero_threshold = None
        
        # Results
        self.p3b_ratio = None
        
        logger.info(f"Initialized DualModalityOddballTask: {n_trials} trials")
    
    def initialize(self) -> bool:
        """Initialize task components."""
        try:
            self.state_machine.transition_to(TaskState.INITIALIZING, "Initializing oddball task")
            
            # Initialize generators
            if not self.intero_generator.initialize():
                logger.error("Failed to initialize interoceptive generator")
                return False
            
            if not self.extero_generator.initialize():
                logger.error("Failed to initialize exteroceptive generator")
                return False
            
            # Run calibration
            logger.info("Running stimulus calibration...")
            self.intero_threshold, self.extero_threshold = self.calibrator.run_calibration(
                self.intero_generator,
                self.extero_generator,
                n_trials_per_modality=30
            )
            
            # Update generator intensities
            self.intero_generator.intensity = self.intero_threshold
            self.extero_generator.intensity = self.extero_threshold
            
            # Initialize timer
            self.timer.start_session()
            
            self.state_machine.transition_to(TaskState.READY, "Oddball task ready")
            logger.info("Oddball task initialized successfully")
            return True
            
        except Exception as e:
            self.state_machine.set_error(f"Initialization failed: {e}")
            logger.error(f"Failed to initialize oddball task: {e}")
            return False
    
    def run_trial(self, trial_number: int) -> Optional[OddballTrialResult]:
        """
        Run a single oddball trial.
        
        Args:
            trial_number: Trial number
            
        Returns:
            OddballTrialResult or None if trial failed
        """
        try:
            # Determine trial type
            is_deviant = np.random.random() < self.deviant_probability
            
            if is_deviant:
                # Equal probability of interoceptive or exteroceptive deviant
                deviant_type = np.random.choice(['interoceptive', 'exteroceptive'])
            else:
                deviant_type = None
            
            # Present stimulus
            stimulus_onset = datetime.now()
            
            if deviant_type == 'interoceptive':
                success = self.intero_generator.generate_deviant()
            elif deviant_type == 'exteroceptive':
                success = self.extero_generator.generate_deviant()
            else:
                # Standard stimulus (exteroceptive)
                success = self.extero_generator.generate_standard()
            
            if not success:
                logger.error(f"Failed to present stimulus for trial {trial_number}")
                return None
            
            # Collect response
            self.response_collector.start_collection(
                stimulus_onset_time=stimulus_onset,
                response_window_ms=1500.0
            )
            
            response = self.response_collector.wait_for_response(timeout_ms=1500.0)
            
            # Handle no response
            if response is None:
                detected = False
                reaction_time = 1500.0
            else:
                detected = response.response_value
                reaction_time = response.reaction_time_ms
            
            # Create behavioral response
            behavioral_response = BehavioralResponse(
                response_time=reaction_time,
                detected=detected,
                reaction_time_valid=reaction_time < 1500.0
            )
            
            # Create trial result
            trial_result = OddballTrialResult(
                participant_id=self.participant_id,
                session_id=self.session_id,
                trial_number=trial_number,
                timestamp=stimulus_onset,
                stimulus_parameters={},
                stimulus_modality=StimulusModality.INTEROCEPTIVE if deviant_type == 'interoceptive' 
                                 else StimulusModality.EXTEROCEPTIVE,
                stimulus_intensity=self.intero_threshold if deviant_type == 'interoceptive' 
                                 else self.extero_threshold,
                behavioral_response=behavioral_response,
                is_deviant=is_deviant,
                deviant_type=deviant_type,
                interoceptive_precision=self.intero_threshold,
                exteroceptive_precision=self.extero_threshold
            )
            
            # Add modality-specific parameters
            if deviant_type == 'interoceptive':
                trial_result.co2_puff_duration = 300.0
                trial_result.co2_concentration = 10.0
            elif deviant_type == 'exteroceptive':
                trial_result.gabor_orientation_deviation = 45.0
            
            # Save to database if DAO available
            if self.dao:
                try:
                    self.dao.create_trial(trial_result)
                except Exception as e:
                    logger.warning(f"Failed to save trial to database: {e}")
            
            self.trials.append(trial_result)
            
            logger.debug(f"Trial {trial_number}: deviant={is_deviant}, type={deviant_type}, "
                        f"detected={detected}, RT={reaction_time:.1f}ms")
            return trial_result
            
        except Exception as e:
            logger.error(f"Error in trial {trial_number}: {e}")
            return None
    
    def run(self) -> bool:
        """
        Run the complete oddball task.
        
        Returns:
            True if task completed successfully
        """
        if not self.state_machine.transition_to(TaskState.RUNNING, "Starting oddball task"):
            return False
        
        try:
            logger.info(f"Starting oddball task: {self.n_trials} trials")
            
            for trial_num in range(1, self.n_trials + 1):
                # Run trial
                trial_result = self.run_trial(trial_num)
                
                if trial_result is None:
                    logger.warning(f"Trial {trial_num} failed, continuing...")
                    continue
                
                self.current_trial = trial_num
                
                # Progress update every 20 trials
                if trial_num % 20 == 0:
                    progress = (trial_num / self.n_trials) * 100
                    logger.info(f"Progress: {trial_num}/{self.n_trials} ({progress:.1f}%)")
            
            # Transition to completed
            self.state_machine.transition_to(TaskState.COMPLETED, "Oddball task completed")
            logger.info(f"Oddball task completed: {len(self.trials)} trials")
            return True
            
        except Exception as e:
            self.state_machine.set_error(f"Task execution failed: {e}")
            logger.error(f"Oddball task failed: {e}")
            return False
    
    def integrate_eeg_p3b(self, p3b_data: List[Dict[str, float]]) -> None:
        """
        Integrate EEG P3b data with trial results.
        
        Args:
            p3b_data: List of P3b measurements for each trial
        """
        if len(p3b_data) != len(self.trials):
            logger.error("P3b data count mismatch")
            return
        
        for trial, p3b in zip(self.trials, p3b_data):
            if trial.deviant_type == 'interoceptive':
                trial.interoceptive_p3b = p3b.get('amplitude', None)
            elif trial.deviant_type == 'exteroceptive':
                trial.exteroceptive_p3b = p3b.get('amplitude', None)
        
        # Calculate P3b ratio
        self._calculate_p3b_ratio()
        
        logger.info("EEG P3b data integrated")
    
    def _calculate_p3b_ratio(self) -> None:
        """Calculate P3b ratio from trial data."""
        # Extract P3b amplitudes
        intero_p3b = [trial.interoceptive_p3b for trial in self.trials 
                     if trial.deviant_type == 'interoceptive' and trial.interoceptive_p3b is not None]
        
        extero_p3b = [trial.exteroceptive_p3b for trial in self.trials 
                     if trial.deviant_type == 'exteroceptive' and trial.exteroceptive_p3b is not None]
        
        if intero_p3b and extero_p3b:
            self.p3b_ratio = self.p3b_calculator.calculate_ratio(intero_p3b, extero_p3b)
            
            # Update trial results with ratio
            for trial in self.trials:
                if trial.is_deviant:
                    trial.p3b_ratio = self.p3b_ratio
    
    def get_results(self) -> Dict[str, Any]:
        """Get task results summary."""
        if not self.trials:
            return {'error': 'No trials completed'}
        
        # Calculate detection rates
        intero_deviants = [trial for trial in self.trials if trial.deviant_type == 'interoceptive']
        extero_deviants = [trial for trial in self.trials if trial.deviant_type == 'exteroceptive']
        
        intero_detection_rate = np.mean([trial.behavioral_response.detected for trial in intero_deviants 
                                        if trial.behavioral_response]) if intero_deviants else 0.0
        
        extero_detection_rate = np.mean([trial.behavioral_response.detected for trial in extero_deviants 
                                        if trial.behavioral_response]) if extero_deviants else 0.0
        
        # Calculate mean reaction times
        reaction_times = [trial.behavioral_response.response_time for trial in self.trials 
                         if trial.behavioral_response and trial.behavioral_response.reaction_time_valid]
        mean_rt = np.mean(reaction_times) if reaction_times else 0.0
        
        return {
            'task_id': self.task_id,
            'n_trials_completed': len(self.trials),
            'n_interoceptive_deviants': len(intero_deviants),
            'n_exteroceptive_deviants': len(extero_deviants),
            'interoceptive_detection_rate': intero_detection_rate,
            'exteroceptive_detection_rate': extero_detection_rate,
            'mean_reaction_time_ms': mean_rt,
            'p3b_ratio': self.p3b_ratio,
            'intero_threshold': self.intero_threshold,
            'extero_threshold': self.extero_threshold,
            'p3b_statistics': self.p3b_calculator.get_statistics() if self.p3b_ratio else None
        }
    
    def cleanup(self) -> None:
        """Clean up task resources."""
        self.intero_generator.cleanup()
        self.extero_generator.cleanup()
        self.response_collector.stop_collection()
        logger.info("Oddball task cleaned up")
