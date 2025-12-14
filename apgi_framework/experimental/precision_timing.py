"""
Millisecond-Precision Timing Control System

Implements high-resolution stimulus timing, trial sequencing, randomization,
and synchronization markers for neural data integration.
"""

import time
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import logging
import threading
import queue

logger = logging.getLogger(__name__)


class TimingMode(Enum):
    """Timing precision modes."""
    STANDARD = "standard"  # Standard timing (~1ms precision)
    HIGH_PRECISION = "high_precision"  # High precision (<1ms)
    REAL_TIME = "real_time"  # Real-time with busy waiting


class SyncMarkerType(Enum):
    """Types of synchronization markers."""
    TRIAL_START = "trial_start"
    STIMULUS_ONSET = "stimulus_onset"
    STIMULUS_OFFSET = "stimulus_offset"
    RESPONSE = "response"
    TRIAL_END = "trial_end"
    BLOCK_START = "block_start"
    BLOCK_END = "block_end"
    CUSTOM = "custom"


@dataclass
class TimingEvent:
    """High-precision timing event."""
    event_id: str
    event_type: str
    scheduled_time: float  # Time in seconds since session start
    actual_time: Optional[float] = None
    timing_error_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def mark_executed(self, actual_time: float) -> None:
        """Mark event as executed and calculate timing error."""
        self.actual_time = actual_time
        if self.scheduled_time is not None:
            self.timing_error_ms = (actual_time - self.scheduled_time) * 1000


@dataclass
class SyncMarker:
    """Synchronization marker for neural data."""
    marker_id: str
    marker_type: SyncMarkerType
    timestamp: float  # Time in seconds since session start
    trial_number: Optional[int] = None
    stimulus_id: Optional[str] = None
    marker_code: Optional[int] = None  # Numeric code for hardware triggers
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'marker_id': self.marker_id,
            'marker_type': self.marker_type.value,
            'timestamp': self.timestamp,
            'trial_number': self.trial_number,
            'stimulus_id': self.stimulus_id,
            'marker_code': self.marker_code,
            'metadata': self.metadata
        }


@dataclass
class TrialTiming:
    """Timing information for a trial."""
    trial_number: int
    trial_start: float
    stimulus_onset: float
    stimulus_offset: float
    response_time: Optional[float] = None
    trial_end: float = 0.0
    
    # Timing errors
    onset_error_ms: float = 0.0
    offset_error_ms: float = 0.0
    
    # Inter-trial interval
    iti_scheduled: float = 0.0
    iti_actual: float = 0.0
    
    def get_reaction_time_ms(self) -> Optional[float]:
        """Calculate reaction time in milliseconds."""
        if self.response_time is None:
            return None
        return (self.response_time - self.stimulus_onset) * 1000
    
    def get_trial_duration_ms(self) -> float:
        """Calculate total trial duration in milliseconds."""
        return (self.trial_end - self.trial_start) * 1000


class PrecisionTimer:
    """
    High-precision timer for stimulus presentation and event scheduling.
    
    Provides sub-millisecond timing accuracy using performance counters
    and busy-waiting for critical timing sections.
    """
    
    def __init__(self, 
                 timer_id: str = "precision_timer",
                 timing_mode: TimingMode = TimingMode.HIGH_PRECISION):
        """
        Initialize precision timer.
        
        Args:
            timer_id: Unique identifier
            timing_mode: Timing precision mode
        """
        self.timer_id = timer_id
        self.timing_mode = timing_mode
        
        # Session timing
        self.session_start_time: Optional[float] = None
        self.reference_time: Optional[float] = None
        
        # Event tracking
        self.scheduled_events: List[TimingEvent] = []
        self.executed_events: List[TimingEvent] = []
        self.timing_errors: List[float] = []
        
        # Performance monitoring
        self.max_timing_error_ms = 0.0
        self.mean_timing_error_ms = 0.0
        
        logger.info(f"Initialized PrecisionTimer {timer_id} in {timing_mode.value} mode")
    
    def start_session(self) -> None:
        """Start timing session and initialize reference time."""
        self.reference_time = time.perf_counter()
        self.session_start_time = time.time()
        self.scheduled_events.clear()
        self.executed_events.clear()
        self.timing_errors.clear()
        
        logger.info("Precision timing session started")
    
    def get_time(self) -> float:
        """
        Get current time in seconds since session start.
        
        Returns:
            Time in seconds with sub-millisecond precision
        """
        if self.reference_time is None:
            raise RuntimeError("Timer session not started")
        
        return time.perf_counter() - self.reference_time
    
    def get_time_ms(self) -> float:
        """Get current time in milliseconds since session start."""
        return self.get_time() * 1000
    
    def schedule_event(self,
                      event_id: str,
                      event_type: str,
                      delay_ms: float,
                      metadata: Optional[Dict[str, Any]] = None) -> TimingEvent:
        """
        Schedule an event at a specific delay from now.
        
        Args:
            event_id: Unique event identifier
            event_type: Type of event
            delay_ms: Delay in milliseconds from now
            metadata: Optional event metadata
            
        Returns:
            TimingEvent object
        """
        current_time = self.get_time()
        scheduled_time = current_time + (delay_ms / 1000)
        
        event = TimingEvent(
            event_id=event_id,
            event_type=event_type,
            scheduled_time=scheduled_time,
            metadata=metadata or {}
        )
        
        self.scheduled_events.append(event)
        logger.debug(f"Scheduled event {event_id} at +{delay_ms:.3f}ms")
        
        return event
    
    def wait_until(self, target_time: float) -> float:
        """
        Wait until specified time with high precision.
        
        Args:
            target_time: Target time in seconds since session start
            
        Returns:
            Actual timing error in milliseconds
        """
        if self.reference_time is None:
            raise RuntimeError("Timer session not started")
        
        target_absolute = self.reference_time + target_time
        current_time = time.perf_counter()
        
        if current_time >= target_absolute:
            # Already past target time
            error_ms = (current_time - target_absolute) * 1000
            logger.warning(f"Target time already passed by {error_ms:.3f}ms")
            return error_ms
        
        time_remaining = target_absolute - current_time
        
        if self.timing_mode == TimingMode.REAL_TIME:
            # Busy wait for entire duration (highest precision)
            while time.perf_counter() < target_absolute:
                pass
        
        elif self.timing_mode == TimingMode.HIGH_PRECISION:
            # Sleep for most of duration, busy wait for last millisecond
            if time_remaining > 0.002:  # More than 2ms remaining
                time.sleep(time_remaining - 0.001)
            
            # Busy wait for final precision
            while time.perf_counter() < target_absolute:
                pass
        
        else:  # STANDARD mode
            # Use standard sleep
            if time_remaining > 0:
                time.sleep(time_remaining)
        
        # Calculate actual timing error
        actual_time = time.perf_counter()
        error_ms = (actual_time - target_absolute) * 1000
        
        self.timing_errors.append(error_ms)
        self._update_timing_statistics()
        
        return error_ms
    
    def sleep_precise(self, duration_ms: float) -> float:
        """
        Sleep for precise duration.
        
        Args:
            duration_ms: Duration in milliseconds
            
        Returns:
            Actual timing error in milliseconds
        """
        start_time = time.perf_counter()
        target_time = start_time + (duration_ms / 1000)
        
        if self.timing_mode == TimingMode.REAL_TIME:
            # Busy wait
            while time.perf_counter() < target_time:
                pass
        
        elif self.timing_mode == TimingMode.HIGH_PRECISION:
            # Hybrid approach
            if duration_ms > 2.0:
                time.sleep((duration_ms - 1.0) / 1000)
            
            while time.perf_counter() < target_time:
                pass
        
        else:
            # Standard sleep
            time.sleep(duration_ms / 1000)
        
        actual_duration = (time.perf_counter() - start_time) * 1000
        error_ms = actual_duration - duration_ms
        
        self.timing_errors.append(error_ms)
        self._update_timing_statistics()
        
        return error_ms
    
    def mark_event_executed(self, event: TimingEvent) -> None:
        """Mark event as executed and record actual timing."""
        actual_time = self.get_time()
        event.mark_executed(actual_time)
        
        self.executed_events.append(event)
        
        if event.timing_error_ms is not None:
            self.timing_errors.append(event.timing_error_ms)
            self._update_timing_statistics()
            
            logger.debug(f"Event {event.event_id} executed with {event.timing_error_ms:.3f}ms error")
    
    def _update_timing_statistics(self) -> None:
        """Update timing performance statistics."""
        if self.timing_errors:
            self.mean_timing_error_ms = np.mean(np.abs(self.timing_errors))
            self.max_timing_error_ms = np.max(np.abs(self.timing_errors))
    
    def get_timing_statistics(self) -> Dict[str, Any]:
        """Get timing performance statistics."""
        if not self.timing_errors:
            return {'status': 'No timing data available'}
        
        errors = np.array(self.timing_errors)
        abs_errors = np.abs(errors)
        
        return {
            'mean_error_ms': np.mean(errors),
            'mean_abs_error_ms': np.mean(abs_errors),
            'std_error_ms': np.std(errors),
            'max_error_ms': np.max(abs_errors),
            'min_error_ms': np.min(abs_errors),
            'median_error_ms': np.median(errors),
            'errors_over_1ms': np.sum(abs_errors > 1.0),
            'errors_over_5ms': np.sum(abs_errors > 5.0),
            'total_events': len(errors),
            'timing_quality': 'excellent' if np.mean(abs_errors) < 0.5 else 
                            'good' if np.mean(abs_errors) < 1.0 else
                            'acceptable' if np.mean(abs_errors) < 2.0 else 'poor'
        }


class TrialSequencer:
    """
    Manages trial sequencing and randomization.
    
    Provides flexible trial ordering with support for blocks, randomization,
    counterbalancing, and constraints.
    """
    
    def __init__(self, sequencer_id: str = "trial_sequencer"):
        """
        Initialize trial sequencer.
        
        Args:
            sequencer_id: Unique identifier
        """
        self.sequencer_id = sequencer_id
        
        # Trial sequence
        self.trial_sequence: List[Dict[str, Any]] = []
        self.current_trial_index = 0
        
        # Randomization
        self.random_seed: Optional[int] = None
        self.rng: Optional[np.random.Generator] = None
        
        logger.info(f"Initialized TrialSequencer {sequencer_id}")
    
    def create_sequence(self,
                       trial_types: List[str],
                       n_repetitions: int = 1,
                       randomize: bool = True,
                       random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Create trial sequence with optional randomization.
        
        Args:
            trial_types: List of trial type identifiers
            n_repetitions: Number of repetitions of each trial type
            randomize: Whether to randomize trial order
            random_seed: Random seed for reproducibility
            
        Returns:
            List of trial specifications
        """
        # Create base sequence
        sequence = []
        for rep in range(n_repetitions):
            for trial_type in trial_types:
                trial = {
                    'trial_type': trial_type,
                    'repetition': rep,
                    'trial_number': len(sequence)
                }
                sequence.append(trial)
        
        # Randomize if requested
        if randomize:
            if random_seed is not None:
                self.random_seed = random_seed
                self.rng = np.random.default_rng(random_seed)
            else:
                self.rng = np.random.default_rng()
            
            self.rng.shuffle(sequence)
            
            # Update trial numbers after shuffling
            for i, trial in enumerate(sequence):
                trial['trial_number'] = i
        
        self.trial_sequence = sequence
        self.current_trial_index = 0
        
        logger.info(f"Created sequence with {len(sequence)} trials (randomized={randomize})")
        return sequence
    
    def create_blocked_sequence(self,
                               block_structure: List[List[str]],
                               randomize_within_blocks: bool = True,
                               randomize_blocks: bool = False,
                               random_seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Create blocked trial sequence.
        
        Args:
            block_structure: List of blocks, each containing trial types
            randomize_within_blocks: Randomize trials within each block
            randomize_blocks: Randomize block order
            random_seed: Random seed for reproducibility
            
        Returns:
            List of trial specifications with block information
        """
        if random_seed is not None:
            self.random_seed = random_seed
            self.rng = np.random.default_rng(random_seed)
        else:
            self.rng = np.random.default_rng()
        
        # Randomize block order if requested
        if randomize_blocks:
            block_indices = list(range(len(block_structure)))
            self.rng.shuffle(block_indices)
            block_structure = [block_structure[i] for i in block_indices]
        
        # Create sequence
        sequence = []
        for block_num, block_trials in enumerate(block_structure):
            # Create trials for this block
            block_sequence = []
            for trial_type in block_trials:
                trial = {
                    'trial_type': trial_type,
                    'block_number': block_num,
                    'trial_number': len(sequence) + len(block_sequence)
                }
                block_sequence.append(trial)
            
            # Randomize within block if requested
            if randomize_within_blocks:
                self.rng.shuffle(block_sequence)
            
            sequence.extend(block_sequence)
        
        # Update trial numbers
        for i, trial in enumerate(sequence):
            trial['trial_number'] = i
        
        self.trial_sequence = sequence
        self.current_trial_index = 0
        
        logger.info(f"Created blocked sequence with {len(block_structure)} blocks, "
                   f"{len(sequence)} total trials")
        return sequence
    
    def get_next_trial(self) -> Optional[Dict[str, Any]]:
        """Get next trial in sequence."""
        if self.current_trial_index >= len(self.trial_sequence):
            return None
        
        trial = self.trial_sequence[self.current_trial_index]
        self.current_trial_index += 1
        
        return trial
    
    def has_more_trials(self) -> bool:
        """Check if more trials remain in sequence."""
        return self.current_trial_index < len(self.trial_sequence)
    
    def get_progress(self) -> Tuple[int, int]:
        """Get current progress through sequence."""
        return self.current_trial_index, len(self.trial_sequence)
    
    def reset(self) -> None:
        """Reset sequencer to beginning."""
        self.current_trial_index = 0
        logger.info("Trial sequencer reset")


class SynchronizationManager:
    """
    Manages synchronization markers for neural data integration.
    
    Provides hardware triggers and software markers for synchronizing
    stimulus presentation with EEG/MEG/fMRI data acquisition.
    """
    
    def __init__(self, 
                 manager_id: str = "sync_manager",
                 enable_hardware_triggers: bool = False):
        """
        Initialize synchronization manager.
        
        Args:
            manager_id: Unique identifier
            enable_hardware_triggers: Enable hardware trigger output
        """
        self.manager_id = manager_id
        self.enable_hardware_triggers = enable_hardware_triggers
        
        # Marker tracking
        self.markers: List[SyncMarker] = []
        self.marker_codes: Dict[SyncMarkerType, int] = self._initialize_marker_codes()
        
        # Hardware interface
        self.trigger_port = None
        if enable_hardware_triggers:
            self._initialize_hardware()
        
        # Timing reference
        self.timer: Optional[PrecisionTimer] = None
        
        logger.info(f"Initialized SynchronizationManager {manager_id}")
    
    def _initialize_marker_codes(self) -> Dict[SyncMarkerType, int]:
        """Initialize default marker codes for each marker type."""
        return {
            SyncMarkerType.TRIAL_START: 1,
            SyncMarkerType.STIMULUS_ONSET: 10,
            SyncMarkerType.STIMULUS_OFFSET: 11,
            SyncMarkerType.RESPONSE: 20,
            SyncMarkerType.TRIAL_END: 2,
            SyncMarkerType.BLOCK_START: 100,
            SyncMarkerType.BLOCK_END: 101,
            SyncMarkerType.CUSTOM: 200
        }
    
    def _initialize_hardware(self) -> None:
        """Initialize hardware trigger interface."""
        # Placeholder for hardware initialization
        # Would interface with parallel port, USB trigger box, etc.
        logger.info("Hardware trigger interface initialized (simulated)")
    
    def set_timer(self, timer: PrecisionTimer) -> None:
        """Set precision timer for timestamp reference."""
        self.timer = timer
        logger.info("Precision timer connected to synchronization manager")
    
    def send_marker(self,
                   marker_type: SyncMarkerType,
                   trial_number: Optional[int] = None,
                   stimulus_id: Optional[str] = None,
                   custom_code: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> SyncMarker:
        """
        Send synchronization marker.
        
        Args:
            marker_type: Type of marker
            trial_number: Trial number (if applicable)
            stimulus_id: Stimulus identifier (if applicable)
            custom_code: Custom marker code (overrides default)
            metadata: Optional metadata
            
        Returns:
            SyncMarker object
        """
        # Get timestamp
        if self.timer:
            timestamp = self.timer.get_time()
        else:
            timestamp = time.perf_counter()
        
        # Determine marker code
        if custom_code is not None:
            marker_code = custom_code
        else:
            marker_code = self.marker_codes.get(marker_type, 0)
        
        # Create marker
        marker = SyncMarker(
            marker_id=f"marker_{len(self.markers)}",
            marker_type=marker_type,
            timestamp=timestamp,
            trial_number=trial_number,
            stimulus_id=stimulus_id,
            marker_code=marker_code,
            metadata=metadata or {}
        )
        
        # Send hardware trigger if enabled
        if self.enable_hardware_triggers and self.trigger_port:
            self._send_hardware_trigger(marker_code)
        
        # Store marker
        self.markers.append(marker)
        
        logger.debug(f"Sent marker: {marker_type.value} (code={marker_code}) at t={timestamp:.6f}s")
        
        return marker
    
    def _send_hardware_trigger(self, code: int) -> None:
        """Send hardware trigger pulse."""
        # Placeholder for hardware trigger
        # Would write to parallel port, USB device, etc.
        pass
    
    def get_markers_for_trial(self, trial_number: int) -> List[SyncMarker]:
        """Get all markers for a specific trial."""
        return [m for m in self.markers if m.trial_number == trial_number]
    
    def get_markers_by_type(self, marker_type: SyncMarkerType) -> List[SyncMarker]:
        """Get all markers of a specific type."""
        return [m for m in self.markers if m.marker_type == marker_type]
    
    def export_markers(self) -> List[Dict[str, Any]]:
        """Export all markers as list of dictionaries."""
        return [marker.to_dict() for marker in self.markers]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of synchronization markers."""
        marker_counts = {}
        for marker_type in SyncMarkerType:
            count = len(self.get_markers_by_type(marker_type))
            if count > 0:
                marker_counts[marker_type.value] = count
        
        return {
            'total_markers': len(self.markers),
            'marker_counts': marker_counts,
            'hardware_triggers_enabled': self.enable_hardware_triggers,
            'timing_reference': 'precision_timer' if self.timer else 'system_clock'
        }


class TimingController:
    """
    Integrated timing control system.
    
    Combines precision timing, trial sequencing, and synchronization
    for complete experimental timing control.
    """
    
    def __init__(self, 
                 controller_id: str = "timing_controller",
                 timing_mode: TimingMode = TimingMode.HIGH_PRECISION,
                 enable_hardware_sync: bool = False):
        """
        Initialize timing controller.
        
        Args:
            controller_id: Unique identifier
            timing_mode: Timing precision mode
            enable_hardware_sync: Enable hardware synchronization
        """
        self.controller_id = controller_id
        
        # Components
        self.timer = PrecisionTimer(f"{controller_id}_timer", timing_mode)
        self.sequencer = TrialSequencer(f"{controller_id}_sequencer")
        self.sync_manager = SynchronizationManager(
            f"{controller_id}_sync",
            enable_hardware_triggers=enable_hardware_sync
        )
        
        # Connect components
        self.sync_manager.set_timer(self.timer)
        
        # Trial timing history
        self.trial_timings: List[TrialTiming] = []
        
        logger.info(f"Initialized TimingController {controller_id}")
    
    def start_session(self) -> None:
        """Start timing session."""
        self.timer.start_session()
        self.trial_timings.clear()
        logger.info("Timing session started")
    
    def start_trial(self, trial_number: int) -> float:
        """
        Start a trial and send synchronization marker.
        
        Args:
            trial_number: Trial number
            
        Returns:
            Trial start time
        """
        trial_start = self.timer.get_time()
        self.sync_manager.send_marker(
            SyncMarkerType.TRIAL_START,
            trial_number=trial_number
        )
        
        return trial_start
    
    def mark_stimulus_onset(self, 
                           trial_number: int,
                           stimulus_id: str) -> float:
        """
        Mark stimulus onset and send synchronization marker.
        
        Args:
            trial_number: Trial number
            stimulus_id: Stimulus identifier
            
        Returns:
            Stimulus onset time
        """
        onset_time = self.timer.get_time()
        self.sync_manager.send_marker(
            SyncMarkerType.STIMULUS_ONSET,
            trial_number=trial_number,
            stimulus_id=stimulus_id
        )
        
        return onset_time
    
    def mark_stimulus_offset(self,
                            trial_number: int,
                            stimulus_id: str) -> float:
        """
        Mark stimulus offset and send synchronization marker.
        
        Args:
            trial_number: Trial number
            stimulus_id: Stimulus identifier
            
        Returns:
            Stimulus offset time
        """
        offset_time = self.timer.get_time()
        self.sync_manager.send_marker(
            SyncMarkerType.STIMULUS_OFFSET,
            trial_number=trial_number,
            stimulus_id=stimulus_id
        )
        
        return offset_time
    
    def mark_response(self, trial_number: int) -> float:
        """
        Mark participant response and send synchronization marker.
        
        Args:
            trial_number: Trial number
            
        Returns:
            Response time
        """
        response_time = self.timer.get_time()
        self.sync_manager.send_marker(
            SyncMarkerType.RESPONSE,
            trial_number=trial_number
        )
        
        return response_time
    
    def end_trial(self, trial_number: int) -> float:
        """
        End trial and send synchronization marker.
        
        Args:
            trial_number: Trial number
            
        Returns:
            Trial end time
        """
        trial_end = self.timer.get_time()
        self.sync_manager.send_marker(
            SyncMarkerType.TRIAL_END,
            trial_number=trial_number
        )
        
        return trial_end
    
    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """Get comprehensive timing and synchronization summary."""
        return {
            'timing_statistics': self.timer.get_timing_statistics(),
            'synchronization_summary': self.sync_manager.get_summary(),
            'trial_count': len(self.trial_timings),
            'sequence_progress': self.sequencer.get_progress()
        }
