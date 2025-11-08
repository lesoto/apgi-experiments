"""
Adaptive Staircase Procedures for Threshold Estimation

Implements multiple adaptive algorithms including QUEST, PEST, and simple staircases
with real-time threshold estimation and cross-modal normalization.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime
from enum import Enum
import logging
from scipy.stats import norm
from abc import ABC, abstractmethod

# Import QUEST+ implementation
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from adaptive.quest_plus_staircase import QuestPlusStaircase, QuestPlusParameters

logger = logging.getLogger(__name__)


class StaircaseType(Enum):
    """Types of adaptive staircase algorithms."""
    SIMPLE = "simple"  # Simple up-down staircase
    WEIGHTED = "weighted"  # Weighted up-down
    PEST = "pest"  # Parameter Estimation by Sequential Testing
    QUEST = "quest"  # Quick Estimation by Sequential Testing
    QUEST_PLUS = "quest_plus"  # QUEST+ with Bayesian optimization
    TRANSFORMED = "transformed"  # Transformed up-down


class ConvergenceRule(Enum):
    """Rules for determining staircase convergence."""
    REVERSALS = "reversals"  # Based on number of reversals
    TRIALS = "trials"  # Based on number of trials
    STABILITY = "stability"  # Based on threshold stability
    COMBINED = "combined"  # Combined criteria


@dataclass
class StaircaseParameters:
    """Parameters for adaptive staircase configuration."""
    staircase_type: StaircaseType = StaircaseType.QUEST_PLUS
    
    # Stimulus range
    min_intensity: float = 0.01
    max_intensity: float = 1.0
    initial_intensity: float = 0.5
    
    # Step sizes
    initial_step_size: float = 0.1
    min_step_size: float = 0.01
    step_size_reduction: float = 0.5  # Factor to reduce step size after reversals
    
    # Simple staircase parameters
    up_rule: int = 1  # Number of incorrect responses to increase intensity
    down_rule: int = 1  # Number of correct responses to decrease intensity
    
    # PEST parameters
    pest_initial_step: float = 0.2
    pest_min_step: float = 0.01
    pest_target_probability: float = 0.75
    
    # Convergence criteria
    convergence_rule: ConvergenceRule = ConvergenceRule.COMBINED
    min_reversals: int = 6
    min_trials: int = 20
    max_trials: int = 100
    stability_window: int = 10
    stability_threshold: float = 0.05
    
    # Cross-modal normalization
    normalize_to_detection_threshold: bool = True
    detection_threshold: Optional[float] = None
    
    def validate(self) -> bool:
        """Validate staircase parameters."""
        if self.min_intensity >= self.max_intensity:
            logger.error("min_intensity must be less than max_intensity")
            return False
        
        if not (self.min_intensity <= self.initial_intensity <= self.max_intensity):
            logger.error("initial_intensity must be within intensity range")
            return False
        
        if self.min_step_size <= 0 or self.initial_step_size <= 0:
            logger.error("Step sizes must be positive")
            return False
        
        if self.up_rule <= 0 or self.down_rule <= 0:
            logger.error("Up/down rules must be positive integers")
            return False
        
        return True


@dataclass
class ThresholdEstimate:
    """Threshold estimate with uncertainty."""
    threshold: float
    std_error: float
    confidence_interval: Tuple[float, float]
    n_trials: int
    n_reversals: int
    converged: bool
    convergence_trial: Optional[int] = None
    
    # Cross-modal normalization
    normalized_threshold: Optional[float] = None
    detection_threshold: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'threshold': self.threshold,
            'std_error': self.std_error,
            'confidence_interval': list(self.confidence_interval),
            'n_trials': self.n_trials,
            'n_reversals': self.n_reversals,
            'converged': self.converged,
            'convergence_trial': self.convergence_trial,
            'normalized_threshold': self.normalized_threshold,
            'detection_threshold': self.detection_threshold
        }


class AdaptiveStaircase(ABC):
    """
    Abstract base class for adaptive staircase procedures.
    
    Provides common interface for different adaptive algorithms.
    """
    
    def __init__(self, 
                 parameters: StaircaseParameters,
                 staircase_id: str = ""):
        """
        Initialize adaptive staircase.
        
        Args:
            parameters: Staircase parameters
            staircase_id: Unique identifier
        """
        self.parameters = parameters
        self.staircase_id = staircase_id
        
        # Trial history
        self.intensities: List[float] = []
        self.responses: List[bool] = []
        self.timestamps: List[datetime] = []
        
        # Current state
        self.current_intensity = parameters.initial_intensity
        self.trial_count = 0
        self.reversal_count = 0
        self.converged = False
        self.convergence_trial: Optional[int] = None
        
        # Tracking
        self.last_direction: Optional[int] = None  # 1 for up, -1 for down
        self.consecutive_correct = 0
        self.consecutive_incorrect = 0
        
        logger.info(f"Initialized {self.__class__.__name__} staircase {staircase_id}")
    
    @abstractmethod
    def get_next_intensity(self) -> float:
        """Get the next stimulus intensity to present."""
        pass
    
    @abstractmethod
    def update(self, intensity: float, response: bool) -> None:
        """Update staircase with trial response."""
        pass
    
    @abstractmethod
    def get_threshold_estimate(self) -> ThresholdEstimate:
        """Get current threshold estimate."""
        pass
    
    def is_converged(self) -> bool:
        """Check if staircase has converged."""
        return self.converged
    
    def should_continue(self) -> bool:
        """Check if staircase should continue."""
        return not self.converged and self.trial_count < self.parameters.max_trials
    
    def _check_reversal(self, response: bool) -> bool:
        """Check if a reversal occurred."""
        # Determine current direction
        current_direction = None
        if response:
            current_direction = -1  # Correct response -> decrease intensity
        else:
            current_direction = 1  # Incorrect response -> increase intensity
        
        # Check for reversal
        if self.last_direction is not None and current_direction != self.last_direction:
            self.reversal_count += 1
            logger.debug(f"Reversal {self.reversal_count} at trial {self.trial_count}")
            self.last_direction = current_direction
            return True
        
        self.last_direction = current_direction
        return False
    
    def _check_convergence(self) -> None:
        """Check convergence based on configured rules."""
        if self.converged:
            return
        
        rule = self.parameters.convergence_rule
        
        # Check minimum trials
        if self.trial_count < self.parameters.min_trials:
            return
        
        converged = False
        
        if rule == ConvergenceRule.REVERSALS:
            converged = self.reversal_count >= self.parameters.min_reversals
        
        elif rule == ConvergenceRule.TRIALS:
            converged = self.trial_count >= self.parameters.max_trials
        
        elif rule == ConvergenceRule.STABILITY:
            converged = self._check_stability()
        
        elif rule == ConvergenceRule.COMBINED:
            # Require both reversals and stability
            has_reversals = self.reversal_count >= self.parameters.min_reversals
            is_stable = self._check_stability()
            converged = has_reversals and is_stable
        
        if converged:
            self.converged = True
            self.convergence_trial = self.trial_count
            logger.info(f"Staircase converged at trial {self.trial_count}")
    
    def _check_stability(self) -> bool:
        """Check if threshold estimate is stable."""
        window = self.parameters.stability_window
        
        if len(self.intensities) < window:
            return False
        
        # Calculate threshold estimates for recent windows
        recent_intensities = self.intensities[-window:]
        recent_responses = self.responses[-window:]
        
        # Simple threshold estimate: midpoint between hits and misses
        hits = [i for i, r in zip(recent_intensities, recent_responses) if r]
        misses = [i for i, r in zip(recent_intensities, recent_responses) if not r]
        
        if not hits or not misses:
            return False
        
        threshold_estimate = (max(misses) + min(hits)) / 2
        
        # Check stability over multiple windows
        if len(self.intensities) >= window * 2:
            prev_intensities = self.intensities[-window*2:-window]
            prev_responses = self.responses[-window*2:-window]
            
            prev_hits = [i for i, r in zip(prev_intensities, prev_responses) if r]
            prev_misses = [i for i, r in zip(prev_intensities, prev_responses) if not r]
            
            if prev_hits and prev_misses:
                prev_threshold = (max(prev_misses) + min(prev_hits)) / 2
                change = abs(threshold_estimate - prev_threshold)
                
                return change < self.parameters.stability_threshold
        
        return False
    
    def _normalize_threshold(self, threshold: float) -> Optional[float]:
        """Normalize threshold to detection threshold."""
        if not self.parameters.normalize_to_detection_threshold:
            return None
        
        if self.parameters.detection_threshold is None:
            logger.warning("Detection threshold not set for normalization")
            return None
        
        # Normalize as ratio to detection threshold
        normalized = threshold / self.parameters.detection_threshold
        return normalized


class SimpleStaircase(AdaptiveStaircase):
    """
    Simple up-down staircase procedure.
    
    Implements basic N-up M-down staircase with configurable step sizes.
    """
    
    def __init__(self, parameters: StaircaseParameters, staircase_id: str = ""):
        super().__init__(parameters, staircase_id)
        self.current_step_size = parameters.initial_step_size
    
    def get_next_intensity(self) -> float:
        """Get next intensity based on simple up-down rule."""
        return self.current_intensity
    
    def update(self, intensity: float, response: bool) -> None:
        """Update staircase with response."""
        # Record trial
        self.intensities.append(intensity)
        self.responses.append(response)
        self.timestamps.append(datetime.now())
        self.trial_count += 1
        
        # Update consecutive counters
        if response:
            self.consecutive_correct += 1
            self.consecutive_incorrect = 0
        else:
            self.consecutive_incorrect += 1
            self.consecutive_correct = 0
        
        # Check for reversal before updating intensity
        self._check_reversal(response)
        
        # Update intensity based on up-down rule
        if self.consecutive_correct >= self.parameters.down_rule:
            # Decrease intensity (make task harder)
            self.current_intensity -= self.current_step_size
            self.consecutive_correct = 0
        
        elif self.consecutive_incorrect >= self.parameters.up_rule:
            # Increase intensity (make task easier)
            self.current_intensity += self.current_step_size
            self.consecutive_incorrect = 0
        
        # Clamp to valid range
        self.current_intensity = np.clip(
            self.current_intensity,
            self.parameters.min_intensity,
            self.parameters.max_intensity
        )
        
        # Reduce step size after reversals
        if self.reversal_count > 0 and self.reversal_count % 2 == 0:
            self.current_step_size = max(
                self.current_step_size * self.parameters.step_size_reduction,
                self.parameters.min_step_size
            )
        
        # Check convergence
        self._check_convergence()
    
    def get_threshold_estimate(self) -> ThresholdEstimate:
        """Get threshold estimate from reversal points."""
        if self.reversal_count < 2:
            # Not enough data
            threshold = self.current_intensity
            std_error = (self.parameters.max_intensity - self.parameters.min_intensity) / 4
        else:
            # Calculate threshold from reversal points
            reversal_intensities = []
            for i in range(1, len(self.intensities)):
                if self._was_reversal(i):
                    reversal_intensities.append(self.intensities[i])
            
            # Use last half of reversals for threshold estimate
            n_reversals = len(reversal_intensities)
            if n_reversals >= 4:
                reversal_intensities = reversal_intensities[n_reversals//2:]
            
            threshold = np.mean(reversal_intensities) if reversal_intensities else self.current_intensity
            std_error = np.std(reversal_intensities) if len(reversal_intensities) > 1 else 0.1
        
        # Calculate confidence interval
        ci_lower = threshold - 1.96 * std_error
        ci_upper = threshold + 1.96 * std_error
        
        # Normalize if requested
        normalized = self._normalize_threshold(threshold)
        
        return ThresholdEstimate(
            threshold=threshold,
            std_error=std_error,
            confidence_interval=(ci_lower, ci_upper),
            n_trials=self.trial_count,
            n_reversals=self.reversal_count,
            converged=self.converged,
            convergence_trial=self.convergence_trial,
            normalized_threshold=normalized,
            detection_threshold=self.parameters.detection_threshold
        )
    
    def _was_reversal(self, trial_index: int) -> bool:
        """Check if trial was a reversal point."""
        if trial_index < 1 or trial_index >= len(self.intensities):
            return False
        
        prev_intensity = self.intensities[trial_index - 1]
        curr_intensity = self.intensities[trial_index]
        
        if trial_index < len(self.intensities) - 1:
            next_intensity = self.intensities[trial_index + 1]
            
            # Check if direction changed
            prev_direction = np.sign(curr_intensity - prev_intensity)
            next_direction = np.sign(next_intensity - curr_intensity)
            
            return prev_direction != 0 and next_direction != 0 and prev_direction != next_direction
        
        return False


class PESTStaircase(AdaptiveStaircase):
    """
    Parameter Estimation by Sequential Testing (PEST) staircase.
    
    Implements PEST algorithm with adaptive step size adjustment.
    """
    
    def __init__(self, parameters: StaircaseParameters, staircase_id: str = ""):
        super().__init__(parameters, staircase_id)
        self.current_step_size = parameters.pest_initial_step
        self.target_probability = parameters.pest_target_probability
    
    def get_next_intensity(self) -> float:
        """Get next intensity based on PEST algorithm."""
        return self.current_intensity
    
    def update(self, intensity: float, response: bool) -> None:
        """Update staircase with PEST algorithm."""
        # Record trial
        self.intensities.append(intensity)
        self.responses.append(response)
        self.timestamps.append(datetime.now())
        self.trial_count += 1
        
        # Check for reversal
        was_reversal = self._check_reversal(response)
        
        # Estimate current performance level
        if len(self.responses) >= 5:
            recent_performance = np.mean(self.responses[-5:])
        else:
            recent_performance = np.mean(self.responses)
        
        # Adjust intensity based on performance relative to target
        if recent_performance > self.target_probability:
            # Performance too high, decrease intensity (make harder)
            self.current_intensity -= self.current_step_size
        else:
            # Performance too low, increase intensity (make easier)
            self.current_intensity += self.current_step_size
        
        # Clamp to valid range
        self.current_intensity = np.clip(
            self.current_intensity,
            self.parameters.min_intensity,
            self.parameters.max_intensity
        )
        
        # Adjust step size based on reversals
        if was_reversal:
            self.current_step_size = max(
                self.current_step_size / 2,
                self.parameters.pest_min_step
            )
        
        # Check convergence
        self._check_convergence()
    
    def get_threshold_estimate(self) -> ThresholdEstimate:
        """Get threshold estimate from PEST procedure."""
        # Threshold is intensity corresponding to target probability
        # Use weighted average of recent intensities
        if len(self.intensities) >= 10:
            recent_intensities = self.intensities[-10:]
            threshold = np.mean(recent_intensities)
            std_error = np.std(recent_intensities)
        else:
            threshold = self.current_intensity
            std_error = self.current_step_size
        
        ci_lower = threshold - 1.96 * std_error
        ci_upper = threshold + 1.96 * std_error
        
        normalized = self._normalize_threshold(threshold)
        
        return ThresholdEstimate(
            threshold=threshold,
            std_error=std_error,
            confidence_interval=(ci_lower, ci_upper),
            n_trials=self.trial_count,
            n_reversals=self.reversal_count,
            converged=self.converged,
            convergence_trial=self.convergence_trial,
            normalized_threshold=normalized,
            detection_threshold=self.parameters.detection_threshold
        )


class QUESTStaircase(AdaptiveStaircase):
    """
    QUEST (Quick Estimation by Sequential Testing) staircase.
    
    Wrapper around QUEST+ implementation with AdaptiveStaircase interface.
    """
    
    def __init__(self, parameters: StaircaseParameters, staircase_id: str = ""):
        super().__init__(parameters, staircase_id)
        
        # Create QUEST+ parameters
        quest_params = QuestPlusParameters(
            stimulus_min=parameters.min_intensity,
            stimulus_max=parameters.max_intensity,
            threshold_min=parameters.min_intensity,
            threshold_max=parameters.max_intensity,
            min_trials=parameters.min_trials,
            max_trials=parameters.max_trials,
            min_reversals=parameters.min_reversals
        )
        
        # Initialize QUEST+ staircase
        self.quest_staircase = QuestPlusStaircase(
            parameters=quest_params,
            participant_id="",
            task_id=staircase_id
        )
    
    def get_next_intensity(self) -> float:
        """Get next intensity from QUEST+ algorithm."""
        intensity = self.quest_staircase.get_next_intensity()
        self.current_intensity = intensity
        return intensity
    
    def update(self, intensity: float, response: bool) -> None:
        """Update QUEST+ staircase."""
        # Update QUEST+ staircase
        self.quest_staircase.update(intensity, response)
        
        # Update local tracking
        self.intensities.append(intensity)
        self.responses.append(response)
        self.timestamps.append(datetime.now())
        self.trial_count += 1
        
        # Check for reversals
        self._check_reversal(response)
        
        # Update convergence status
        self.converged = self.quest_staircase.is_converged()
        if self.converged and self.convergence_trial is None:
            self.convergence_trial = self.trial_count
    
    def get_threshold_estimate(self) -> ThresholdEstimate:
        """Get threshold estimate from QUEST+."""
        threshold, std_error = self.quest_staircase.get_threshold_estimate()
        
        ci_lower = threshold - 1.96 * std_error
        ci_upper = threshold + 1.96 * std_error
        
        normalized = self._normalize_threshold(threshold)
        
        return ThresholdEstimate(
            threshold=threshold,
            std_error=std_error,
            confidence_interval=(ci_lower, ci_upper),
            n_trials=self.trial_count,
            n_reversals=self.reversal_count,
            converged=self.converged,
            convergence_trial=self.convergence_trial,
            normalized_threshold=normalized,
            detection_threshold=self.parameters.detection_threshold
        )


class CrossModalThresholdNormalizer:
    """
    Normalizes thresholds across different sensory modalities.
    
    Provides methods for comparing thresholds across visual, auditory,
    and interoceptive modalities by normalizing to detection thresholds.
    """
    
    def __init__(self):
        """Initialize cross-modal normalizer."""
        self.detection_thresholds: Dict[str, float] = {}
        self.normalized_thresholds: Dict[str, float] = {}
        
        logger.info("Initialized CrossModalThresholdNormalizer")
    
    def set_detection_threshold(self, modality: str, threshold: float) -> None:
        """
        Set detection threshold for a modality.
        
        Args:
            modality: Modality name (e.g., 'visual', 'auditory', 'interoceptive')
            threshold: Detection threshold value
        """
        self.detection_thresholds[modality] = threshold
        logger.info(f"Set detection threshold for {modality}: {threshold:.4f}")
    
    def normalize_threshold(self, modality: str, threshold: float) -> Optional[float]:
        """
        Normalize threshold to detection threshold.
        
        Args:
            modality: Modality name
            threshold: Threshold value to normalize
            
        Returns:
            Normalized threshold (ratio to detection threshold)
        """
        if modality not in self.detection_thresholds:
            logger.warning(f"No detection threshold set for {modality}")
            return None
        
        detection_threshold = self.detection_thresholds[modality]
        if detection_threshold == 0:
            logger.error(f"Detection threshold for {modality} is zero")
            return None
        
        normalized = threshold / detection_threshold
        self.normalized_thresholds[modality] = normalized
        
        logger.debug(f"Normalized {modality} threshold: {threshold:.4f} -> {normalized:.4f}")
        return normalized
    
    def compare_thresholds(self, 
                          modality1: str, 
                          threshold1: float,
                          modality2: str,
                          threshold2: float) -> Optional[float]:
        """
        Compare thresholds across modalities.
        
        Args:
            modality1: First modality name
            threshold1: First threshold value
            modality2: Second modality name
            threshold2: Second threshold value
            
        Returns:
            Ratio of normalized thresholds (modality1 / modality2)
        """
        norm1 = self.normalize_threshold(modality1, threshold1)
        norm2 = self.normalize_threshold(modality2, threshold2)
        
        if norm1 is None or norm2 is None:
            return None
        
        if norm2 == 0:
            logger.error("Cannot compare: second normalized threshold is zero")
            return None
        
        ratio = norm1 / norm2
        logger.info(f"Threshold ratio {modality1}/{modality2}: {ratio:.4f}")
        
        return ratio
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of detection and normalized thresholds."""
        return {
            'detection_thresholds': self.detection_thresholds.copy(),
            'normalized_thresholds': self.normalized_thresholds.copy(),
            'modalities': list(self.detection_thresholds.keys())
        }


def create_staircase(staircase_type: StaircaseType,
                    parameters: StaircaseParameters,
                    staircase_id: str = "") -> AdaptiveStaircase:
    """
    Factory function to create adaptive staircase of specified type.
    
    Args:
        staircase_type: Type of staircase to create
        parameters: Staircase parameters
        staircase_id: Unique identifier
        
    Returns:
        AdaptiveStaircase instance
    """
    if staircase_type == StaircaseType.SIMPLE or staircase_type == StaircaseType.WEIGHTED:
        return SimpleStaircase(parameters, staircase_id)
    
    elif staircase_type == StaircaseType.PEST:
        return PESTStaircase(parameters, staircase_id)
    
    elif staircase_type == StaircaseType.QUEST or staircase_type == StaircaseType.QUEST_PLUS:
        return QUESTStaircase(parameters, staircase_id)
    
    else:
        logger.warning(f"Unknown staircase type {staircase_type}, using QUEST+")
        return QUESTStaircase(parameters, staircase_id)
