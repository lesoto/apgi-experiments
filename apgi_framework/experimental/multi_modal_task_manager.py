"""
Multi-Modal Task Manager for Coordinated Stimulus Presentation

Implements coordinated presentation of visual, auditory, and interoceptive stimuli
for APGI framework experimental paradigms. Manages stimulus timing, synchronization,
and multi-modal integration.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import logging
import time
import threading
from abc import ABC, abstractmethod

# Import stimulus generators
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from adaptive.stimulus_generators import (
    GaborPatchGenerator, GaborParameters,
    ToneGenerator, ToneParameters,
    CO2PuffController, CO2PuffParameters,
    HeartbeatSynchronizer,
    StimulusType
)

logger = logging.getLogger(__name__)


class ModalityType(Enum):
    """Types of sensory modalities."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    INTEROCEPTIVE = "interoceptive"
    MULTIMODAL = "multimodal"


class TaskParadigm(Enum):
    """Experimental task paradigms."""
    DETECTION = "detection"
    ODDBALL = "oddball"
    THRESHOLD_ESTIMATION = "threshold_estimation"
    HEARTBEAT_SYNCHRONY = "heartbeat_synchrony"
    CROSS_MODAL = "cross_modal"


@dataclass
class TrialConfiguration:
    """Configuration for a single experimental trial."""
    trial_id: str
    trial_number: int
    paradigm: TaskParadigm
    modality: ModalityType
    
    # Stimulus parameters
    visual_params: Optional[GaborParameters] = None
    auditory_params: Optional[ToneParameters] = None
    interoceptive_params: Optional[CO2PuffParameters] = None
    
    # Timing parameters
    isi_ms: float = 1000.0  # Inter-stimulus interval
    response_window_ms: float = 2000.0
    
    # Trial metadata
    is_target: bool = False
    is_catch_trial: bool = False
    expected_response: Optional[bool] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate trial configuration."""
        # Check that at least one stimulus is defined
        has_stimulus = any([
            self.visual_params is not None,
            self.auditory_params is not None,
            self.interoceptive_params is not None
        ])
        
        if not has_stimulus:
            logger.error("Trial must have at least one stimulus defined")
            return False
        
        # Validate timing parameters
        if self.isi_ms < 0 or self.response_window_ms < 0:
            logger.error("Timing parameters must be positive")
            return False
        
        # Validate stimulus parameters
        if self.visual_params and not self.visual_params.validate():
            logger.error("Invalid visual stimulus parameters")
            return False
        
        if self.auditory_params and not self.auditory_params.validate():
            logger.error("Invalid auditory stimulus parameters")
            return False
        
        if self.interoceptive_params and not self.interoceptive_params.validate():
            logger.error("Invalid interoceptive stimulus parameters")
            return False
        
        return True


@dataclass
class TrialResult:
    """Results from a completed trial."""
    trial_id: str
    trial_number: int
    paradigm: TaskParadigm
    modality: ModalityType
    
    # Stimulus presentation timing
    stimulus_onset_time: datetime
    stimulus_offset_time: datetime
    actual_duration_ms: float
    
    # Response data
    response_detected: bool
    response_time: Optional[datetime] = None
    reaction_time_ms: Optional[float] = None
    response_value: Any = None
    confidence: Optional[float] = None
    
    # Accuracy
    correct: Optional[bool] = None
    
    # Quality metrics
    timing_error_ms: float = 0.0
    presentation_quality: float = 1.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'trial_id': self.trial_id,
            'trial_number': self.trial_number,
            'paradigm': self.paradigm.value,
            'modality': self.modality.value,
            'stimulus_onset_time': self.stimulus_onset_time.isoformat(),
            'stimulus_offset_time': self.stimulus_offset_time.isoformat(),
            'actual_duration_ms': self.actual_duration_ms,
            'response_detected': self.response_detected,
            'response_time': self.response_time.isoformat() if self.response_time else None,
            'reaction_time_ms': self.reaction_time_ms,
            'response_value': self.response_value,
            'confidence': self.confidence,
            'correct': self.correct,
            'timing_error_ms': self.timing_error_ms,
            'presentation_quality': self.presentation_quality,
            'metadata': self.metadata
        }


class MultiModalTaskManager:
    """
    Manages coordinated multi-modal stimulus presentation.
    
    Coordinates visual, auditory, and interoceptive stimulus generators
    for complex experimental paradigms with precise timing control.
    """
    
    def __init__(self, 
                 manager_id: str = "multimodal_manager",
                 enable_visual: bool = True,
                 enable_auditory: bool = True,
                 enable_interoceptive: bool = False):
        """
        Initialize multi-modal task manager.
        
        Args:
            manager_id: Unique identifier for this manager
            enable_visual: Enable visual stimulus generation
            enable_auditory: Enable auditory stimulus generation
            enable_interoceptive: Enable interoceptive stimulus generation
        """
        self.manager_id = manager_id
        self.is_initialized = False
        
        # Stimulus generators
        self.visual_generator: Optional[GaborPatchGenerator] = None
        self.auditory_generator: Optional[ToneGenerator] = None
        self.interoceptive_generator: Optional[CO2PuffController] = None
        self.heartbeat_synchronizer: Optional[HeartbeatSynchronizer] = None
        
        # Enable flags
        self.enable_visual = enable_visual
        self.enable_auditory = enable_auditory
        self.enable_interoceptive = enable_interoceptive
        
        # Trial management
        self.current_trial: Optional[TrialConfiguration] = None
        self.trial_history: List[TrialResult] = []
        self.trial_count = 0
        
        # Timing control
        self.reference_time: Optional[datetime] = None
        self.timing_errors: List[float] = []
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info(f"Initialized MultiModalTaskManager {manager_id}")
    
    def initialize(self, 
                  screen_width: int = 1920,
                  screen_height: int = 1080,
                  viewing_distance_cm: float = 60.0,
                  sample_rate: int = 44100) -> bool:
        """
        Initialize all enabled stimulus generators.
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            viewing_distance_cm: Viewing distance in centimeters
            sample_rate: Audio sample rate in Hz
            
        Returns:
            True if initialization successful
        """
        try:
            # Initialize visual generator
            if self.enable_visual:
                self.visual_generator = GaborPatchGenerator(
                    generator_id=f"{self.manager_id}_visual",
                    screen_width=screen_width,
                    screen_height=screen_height,
                    viewing_distance_cm=viewing_distance_cm
                )
                if not self.visual_generator.initialize():
                    logger.error("Failed to initialize visual generator")
                    return False
                logger.info("Visual generator initialized")
            
            # Initialize auditory generator
            if self.enable_auditory:
                self.auditory_generator = ToneGenerator(
                    generator_id=f"{self.manager_id}_auditory",
                    sample_rate=sample_rate
                )
                if not self.auditory_generator.initialize():
                    logger.error("Failed to initialize auditory generator")
                    return False
                logger.info("Auditory generator initialized")
            
            # Initialize interoceptive generator
            if self.enable_interoceptive:
                self.interoceptive_generator = CO2PuffController(
                    generator_id=f"{self.manager_id}_interoceptive",
                    safety_enabled=True
                )
                if not self.interoceptive_generator.initialize():
                    logger.error("Failed to initialize interoceptive generator")
                    return False
                logger.info("Interoceptive generator initialized")
            
            # Initialize heartbeat synchronizer
            self.heartbeat_synchronizer = HeartbeatSynchronizer(
                synchronizer_id=f"{self.manager_id}_heartbeat"
            )
            if not self.heartbeat_synchronizer.initialize():
                logger.warning("Heartbeat synchronizer initialization failed (non-critical)")
            else:
                # Connect to auditory generator for cardiac-locked tones
                if self.auditory_generator:
                    self.auditory_generator.set_heartbeat_synchronizer(self.heartbeat_synchronizer)
                logger.info("Heartbeat synchronizer initialized")
            
            self.reference_time = datetime.now()
            self.is_initialized = True
            
            logger.info("MultiModalTaskManager fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MultiModalTaskManager: {e}")
            return False
    
    def present_trial(self, trial_config: TrialConfiguration) -> Optional[TrialResult]:
        """
        Present a complete trial with all configured stimuli.
        
        Args:
            trial_config: Trial configuration
            
        Returns:
            TrialResult if successful, None otherwise
        """
        if not self.is_initialized:
            logger.error("Manager not initialized")
            return None
        
        if not trial_config.validate():
            logger.error("Invalid trial configuration")
            return None
        
        with self.lock:
            self.current_trial = trial_config
            self.trial_count += 1
            
            try:
                # Record trial start
                trial_start_time = datetime.now()
                
                # Present stimuli based on modality
                stimulus_onset = None
                stimulus_offset = None
                timing_error = 0.0
                
                if trial_config.modality == ModalityType.VISUAL:
                    stimulus_onset, stimulus_offset, timing_error = self._present_visual_stimulus(
                        trial_config.visual_params
                    )
                
                elif trial_config.modality == ModalityType.AUDITORY:
                    stimulus_onset, stimulus_offset, timing_error = self._present_auditory_stimulus(
                        trial_config.auditory_params
                    )
                
                elif trial_config.modality == ModalityType.INTEROCEPTIVE:
                    stimulus_onset, stimulus_offset, timing_error = self._present_interoceptive_stimulus(
                        trial_config.interoceptive_params
                    )
                
                elif trial_config.modality == ModalityType.MULTIMODAL:
                    stimulus_onset, stimulus_offset, timing_error = self._present_multimodal_stimuli(
                        trial_config
                    )
                
                if stimulus_onset is None or stimulus_offset is None:
                    logger.error("Stimulus presentation failed")
                    return None
                
                # Calculate actual duration
                actual_duration_ms = (stimulus_offset - stimulus_onset).total_seconds() * 1000
                
                # Collect response (placeholder - would integrate with response collector)
                response_detected, response_time, reaction_time, response_value, confidence = \
                    self._collect_response(stimulus_onset, trial_config.response_window_ms)
                
                # Determine correctness
                correct = None
                if trial_config.expected_response is not None:
                    correct = (response_detected == trial_config.expected_response)
                
                # Create trial result
                result = TrialResult(
                    trial_id=trial_config.trial_id,
                    trial_number=trial_config.trial_number,
                    paradigm=trial_config.paradigm,
                    modality=trial_config.modality,
                    stimulus_onset_time=stimulus_onset,
                    stimulus_offset_time=stimulus_offset,
                    actual_duration_ms=actual_duration_ms,
                    response_detected=response_detected,
                    response_time=response_time,
                    reaction_time_ms=reaction_time,
                    response_value=response_value,
                    confidence=confidence,
                    correct=correct,
                    timing_error_ms=timing_error,
                    presentation_quality=1.0 if abs(timing_error) < 5.0 else 0.8,
                    metadata=trial_config.metadata.copy()
                )
                
                # Store result
                self.trial_history.append(result)
                self.timing_errors.append(timing_error)
                
                # Inter-stimulus interval
                if trial_config.isi_ms > 0:
                    time.sleep(trial_config.isi_ms / 1000.0)
                
                logger.info(f"Trial {trial_config.trial_number} completed: "
                          f"RT={reaction_time:.1f}ms, correct={correct}")
                
                return result
                
            except Exception as e:
                logger.error(f"Error presenting trial: {e}")
                return None
            finally:
                self.current_trial = None
    
    def _present_visual_stimulus(self, 
                                params: Optional[GaborParameters]) -> Tuple[Optional[datetime], Optional[datetime], float]:
        """Present visual stimulus."""
        if params is None or self.visual_generator is None:
            return None, None, 0.0
        
        onset_time = datetime.now()
        success = self.visual_generator.generate_stimulus(params)
        offset_time = datetime.now()
        
        if not success:
            return None, None, 0.0
        
        # Calculate timing error
        expected_duration = params.duration_ms
        actual_duration = (offset_time - onset_time).total_seconds() * 1000
        timing_error = actual_duration - expected_duration
        
        return onset_time, offset_time, timing_error
    
    def _present_auditory_stimulus(self, 
                                  params: Optional[ToneParameters]) -> Tuple[Optional[datetime], Optional[datetime], float]:
        """Present auditory stimulus."""
        if params is None or self.auditory_generator is None:
            return None, None, 0.0
        
        onset_time = datetime.now()
        success = self.auditory_generator.generate_stimulus(params)
        offset_time = datetime.now()
        
        if not success:
            return None, None, 0.0
        
        # Calculate timing error
        expected_duration = params.duration_ms
        actual_duration = (offset_time - onset_time).total_seconds() * 1000
        timing_error = actual_duration - expected_duration
        
        return onset_time, offset_time, timing_error
    
    def _present_interoceptive_stimulus(self, 
                                       params: Optional[CO2PuffParameters]) -> Tuple[Optional[datetime], Optional[datetime], float]:
        """Present interoceptive stimulus."""
        if params is None or self.interoceptive_generator is None:
            return None, None, 0.0
        
        onset_time = datetime.now()
        success = self.interoceptive_generator.generate_stimulus(params)
        offset_time = datetime.now()
        
        if not success:
            return None, None, 0.0
        
        # Calculate timing error
        expected_duration = params.duration_ms
        actual_duration = (offset_time - onset_time).total_seconds() * 1000
        timing_error = actual_duration - expected_duration
        
        return onset_time, offset_time, timing_error
    
    def _present_multimodal_stimuli(self, 
                                   trial_config: TrialConfiguration) -> Tuple[Optional[datetime], Optional[datetime], float]:
        """Present multiple stimuli simultaneously or in sequence."""
        onset_time = datetime.now()
        max_duration = 0.0
        total_timing_error = 0.0
        error_count = 0
        
        # Present visual stimulus
        if trial_config.visual_params and self.visual_generator:
            success = self.visual_generator.generate_stimulus(trial_config.visual_params)
            if success:
                max_duration = max(max_duration, trial_config.visual_params.duration_ms)
        
        # Present auditory stimulus (can be simultaneous)
        if trial_config.auditory_params and self.auditory_generator:
            success = self.auditory_generator.generate_stimulus(trial_config.auditory_params)
            if success:
                max_duration = max(max_duration, trial_config.auditory_params.duration_ms)
        
        # Present interoceptive stimulus (typically sequential for safety)
        if trial_config.interoceptive_params and self.interoceptive_generator:
            success = self.interoceptive_generator.generate_stimulus(trial_config.interoceptive_params)
            if success:
                max_duration = max(max_duration, trial_config.interoceptive_params.duration_ms)
        
        offset_time = datetime.now()
        
        # Calculate timing error
        actual_duration = (offset_time - onset_time).total_seconds() * 1000
        timing_error = actual_duration - max_duration
        
        return onset_time, offset_time, timing_error
    
    def _collect_response(self, 
                         stimulus_onset: datetime,
                         response_window_ms: float) -> Tuple[bool, Optional[datetime], Optional[float], Any, Optional[float]]:
        """
        Collect participant response.
        
        Returns:
            Tuple of (response_detected, response_time, reaction_time_ms, response_value, confidence)
        """
        # Placeholder implementation - would integrate with actual response collector
        # Simulate response collection
        
        start_time = time.time()
        response_detected = False
        response_time = None
        reaction_time_ms = None
        response_value = None
        confidence = None
        
        # Simulate waiting for response
        while (time.time() - start_time) * 1000 < response_window_ms:
            # In real implementation, would check for actual input
            # For now, simulate random response
            if np.random.random() < 0.001:  # Low probability per poll
                response_detected = True
                response_time = datetime.now()
                reaction_time_ms = (response_time - stimulus_onset).total_seconds() * 1000
                response_value = True
                confidence = np.random.uniform(0.5, 1.0)
                break
            
            time.sleep(0.001)  # 1ms polling
        
        return response_detected, response_time, reaction_time_ms, response_value, confidence
    
    def create_detection_trial(self,
                             trial_number: int,
                             modality: ModalityType,
                             intensity: float,
                             is_target: bool = True) -> TrialConfiguration:
        """
        Create a detection task trial configuration.
        
        Args:
            trial_number: Trial number
            modality: Sensory modality
            intensity: Stimulus intensity (0-1)
            is_target: Whether this is a target trial
            
        Returns:
            TrialConfiguration for detection task
        """
        trial_id = f"detection_{modality.value}_{trial_number}"
        
        # Create stimulus parameters based on modality
        visual_params = None
        auditory_params = None
        interoceptive_params = None
        
        if modality == ModalityType.VISUAL:
            visual_params = GaborParameters(
                contrast=intensity,
                spatial_frequency=2.0,
                orientation=0.0,
                size_degrees=2.0,
                duration_ms=100.0
            )
        
        elif modality == ModalityType.AUDITORY:
            auditory_params = ToneParameters(
                frequency_hz=1000.0,
                amplitude=intensity,
                duration_ms=100.0,
                onset_ramp_ms=10.0,
                offset_ramp_ms=10.0
            )
        
        elif modality == ModalityType.INTEROCEPTIVE:
            interoceptive_params = CO2PuffParameters(
                co2_concentration=intensity * 10.0,  # Scale to 0-10%
                flow_rate=2.0,
                duration_ms=200.0
            )
        
        return TrialConfiguration(
            trial_id=trial_id,
            trial_number=trial_number,
            paradigm=TaskParadigm.DETECTION,
            modality=modality,
            visual_params=visual_params,
            auditory_params=auditory_params,
            interoceptive_params=interoceptive_params,
            isi_ms=1500.0,
            response_window_ms=2000.0,
            is_target=is_target,
            expected_response=is_target
        )
    
    def create_oddball_trial(self,
                           trial_number: int,
                           modality: ModalityType,
                           is_oddball: bool,
                           standard_intensity: float = 0.5,
                           oddball_intensity: float = 0.8) -> TrialConfiguration:
        """
        Create an oddball task trial configuration.
        
        Args:
            trial_number: Trial number
            modality: Sensory modality
            is_oddball: Whether this is an oddball trial
            standard_intensity: Standard stimulus intensity
            oddball_intensity: Oddball stimulus intensity
            
        Returns:
            TrialConfiguration for oddball task
        """
        trial_id = f"oddball_{modality.value}_{trial_number}"
        intensity = oddball_intensity if is_oddball else standard_intensity
        
        # Create stimulus parameters
        visual_params = None
        auditory_params = None
        interoceptive_params = None
        
        if modality == ModalityType.VISUAL:
            visual_params = GaborParameters(
                contrast=intensity,
                spatial_frequency=2.0,
                orientation=90.0 if is_oddball else 0.0,  # Different orientation for oddball
                size_degrees=2.0,
                duration_ms=200.0
            )
        
        elif modality == ModalityType.AUDITORY:
            auditory_params = ToneParameters(
                frequency_hz=2000.0 if is_oddball else 1000.0,  # Different frequency for oddball
                amplitude=intensity,
                duration_ms=200.0
            )
        
        elif modality == ModalityType.INTEROCEPTIVE:
            interoceptive_params = CO2PuffParameters(
                co2_concentration=intensity * 10.0,
                flow_rate=3.0 if is_oddball else 2.0,  # Different flow for oddball
                duration_ms=300.0
            )
        
        return TrialConfiguration(
            trial_id=trial_id,
            trial_number=trial_number,
            paradigm=TaskParadigm.ODDBALL,
            modality=modality,
            visual_params=visual_params,
            auditory_params=auditory_params,
            interoceptive_params=interoceptive_params,
            isi_ms=1000.0,
            response_window_ms=1500.0,
            is_target=is_oddball,
            expected_response=is_oddball
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of task performance."""
        if not self.trial_history:
            return {'error': 'No trials completed'}
        
        # Calculate performance metrics
        total_trials = len(self.trial_history)
        responses = [r.response_detected for r in self.trial_history]
        response_rate = np.mean(responses)
        
        # Calculate accuracy for trials with expected responses
        accuracy_trials = [r for r in self.trial_history if r.correct is not None]
        accuracy = np.mean([r.correct for r in accuracy_trials]) if accuracy_trials else None
        
        # Calculate reaction times
        reaction_times = [r.reaction_time_ms for r in self.trial_history if r.reaction_time_ms is not None]
        mean_rt = np.mean(reaction_times) if reaction_times else None
        std_rt = np.std(reaction_times) if reaction_times else None
        
        # Timing quality
        mean_timing_error = np.mean(self.timing_errors) if self.timing_errors else 0.0
        std_timing_error = np.std(self.timing_errors) if self.timing_errors else 0.0
        
        return {
            'total_trials': total_trials,
            'response_rate': response_rate,
            'accuracy': accuracy,
            'mean_reaction_time_ms': mean_rt,
            'std_reaction_time_ms': std_rt,
            'mean_timing_error_ms': mean_timing_error,
            'std_timing_error_ms': std_timing_error,
            'timing_quality': 'good' if abs(mean_timing_error) < 2.0 else 'acceptable'
        }
    
    def cleanup(self) -> None:
        """Clean up all stimulus generators."""
        if self.visual_generator:
            self.visual_generator.cleanup()
        
        if self.auditory_generator:
            self.auditory_generator.cleanup()
        
        if self.interoceptive_generator:
            self.interoceptive_generator.cleanup()
        
        self.is_initialized = False
        logger.info("MultiModalTaskManager cleaned up")
