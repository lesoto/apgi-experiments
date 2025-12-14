"""
Threshold management system for dynamic ignition threshold adjustment.

This module implements the threshold manager that handles dynamic adjustment
of the ignition threshold (θₜ) based on context, adaptation, and task demands.
"""

import numpy as np
from typing import Optional, List, Dict
from enum import Enum
import warnings

from ..exceptions import MathematicalError
from .somatic_marker import ContextType


class ThresholdAdaptationType(Enum):
    """Types of threshold adaptation mechanisms."""
    FIXED = "fixed"
    HOMEOSTATIC = "homeostatic"
    CONTEXTUAL = "contextual"
    ADAPTIVE = "adaptive"


class ThresholdManager:
    """
    Manager for dynamic ignition threshold (θₜ) adjustment.
    
    Handles threshold modulation based on context, recent ignition history,
    and adaptive mechanisms to maintain optimal ignition rates.
    """
    
    def __init__(self,
                 baseline_threshold: float = 3.5,
                 min_threshold: float = 0.5,
                 max_threshold: float = 10.0,
                 adaptation_type: ThresholdAdaptationType = ThresholdAdaptationType.ADAPTIVE):
        """
        Initialize threshold manager.
        
        Args:
            baseline_threshold: Default threshold value
            min_threshold: Minimum allowed threshold
            max_threshold: Maximum allowed threshold
            adaptation_type: Type of threshold adaptation to use
        """
        if baseline_threshold <= 0:
            raise MathematicalError("Baseline threshold must be positive")
        if max_threshold <= min_threshold:
            raise MathematicalError("Maximum threshold must be greater than minimum")
        if not (min_threshold <= baseline_threshold <= max_threshold):
            raise MathematicalError("Baseline threshold must be within min/max bounds")
        
        self.baseline_threshold = baseline_threshold
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.adaptation_type = adaptation_type
        
        # Adaptation parameters
        self.target_ignition_rate = 0.3  # Target 30% ignition rate
        self.adaptation_rate = 0.05  # Rate of threshold adjustment
        self.context_sensitivity = 0.5  # Sensitivity to context changes
        
        # History tracking
        self._ignition_history: List[bool] = []
        self._threshold_history: List[float] = []
        self._current_threshold = baseline_threshold
        
        # Context-specific threshold modulations
        self._context_modulations = {
            ContextType.ROUTINE: 0.0,
            ContextType.HIGH_STAKES: -0.5,  # Lower threshold for high stakes
            ContextType.EMOTIONAL: -0.3,
            ContextType.THREAT: -0.8,  # Much lower threshold for threats
            ContextType.REWARD: -0.2,
            ContextType.NEUTRAL: 0.0
        }
    
    def get_current_threshold(self, 
                             context: Optional[ContextType] = None,
                             arousal: float = 1.0) -> float:
        """
        Get current ignition threshold with optional context modulation.
        
        Args:
            context: Current contextual situation
            arousal: Current arousal level (0.1 to 3.0)
            
        Returns:
            Current ignition threshold value
            
        Raises:
            MathematicalError: If arousal is out of valid range
        """
        if not (0.1 <= arousal <= 3.0):
            raise MathematicalError("Arousal must be between 0.1 and 3.0")
        
        threshold = self._current_threshold
        
        # Apply context modulation if provided
        if context is not None:
            context_adjustment = self._context_modulations.get(context, 0.0)
            threshold += self.context_sensitivity * context_adjustment
        
        # Apply arousal modulation (higher arousal lowers threshold)
        arousal_adjustment = -0.2 * (arousal - 1.0)  # Maps arousal to threshold adjustment
        threshold += arousal_adjustment
        
        # Apply bounds
        threshold = np.clip(threshold, self.min_threshold, self.max_threshold)
        
        return float(threshold)
    
    def update_threshold(self, 
                        ignition_occurred: bool,
                        context: Optional[ContextType] = None) -> float:
        """
        Update threshold based on recent ignition and adaptation type.
        
        Args:
            ignition_occurred: Whether ignition occurred in the last trial
            context: Current contextual situation
            
        Returns:
            Updated threshold value
        """
        # Record ignition in history
        self._ignition_history.append(ignition_occurred)
        
        # Limit history size
        if len(self._ignition_history) > 100:
            self._ignition_history = self._ignition_history[-100:]
        
        # Update threshold based on adaptation type
        if self.adaptation_type == ThresholdAdaptationType.FIXED:
            # No adaptation - keep baseline
            new_threshold = self.baseline_threshold
            
        elif self.adaptation_type == ThresholdAdaptationType.HOMEOSTATIC:
            # Homeostatic adaptation to maintain target ignition rate
            new_threshold = self._homeostatic_adaptation()
            
        elif self.adaptation_type == ThresholdAdaptationType.CONTEXTUAL:
            # Context-dependent adaptation
            new_threshold = self._contextual_adaptation(context)
            
        elif self.adaptation_type == ThresholdAdaptationType.ADAPTIVE:
            # Full adaptive mechanism
            new_threshold = self._adaptive_threshold_update(context)
        
        else:
            warnings.warn(f"Unknown adaptation type: {self.adaptation_type}")
            new_threshold = self.baseline_threshold
        
        # Apply bounds and update
        self._current_threshold = np.clip(new_threshold, 
                                        self.min_threshold, 
                                        self.max_threshold)
        
        # Record in history
        self._threshold_history.append(self._current_threshold)
        if len(self._threshold_history) > 100:
            self._threshold_history = self._threshold_history[-100:]
        
        return self._current_threshold
    
    def _homeostatic_adaptation(self) -> float:
        """Implement homeostatic threshold adaptation."""
        if len(self._ignition_history) < 10:
            return self._current_threshold
        
        # Calculate recent ignition rate
        recent_rate = np.mean(self._ignition_history[-20:])
        
        # Adjust threshold to move toward target rate
        rate_error = recent_rate - self.target_ignition_rate
        threshold_adjustment = self.adaptation_rate * rate_error
        
        return self._current_threshold + threshold_adjustment
    
    def _contextual_adaptation(self, context: Optional[ContextType]) -> float:
        """Implement context-dependent threshold adaptation."""
        base_threshold = self._homeostatic_adaptation()
        
        if context is None:
            return base_threshold
        
        # Apply context-specific adjustment
        context_adjustment = self._context_modulations.get(context, 0.0)
        return base_threshold + self.context_sensitivity * context_adjustment
    
    def _adaptive_threshold_update(self, context: Optional[ContextType]) -> float:
        """Implement full adaptive threshold mechanism."""
        # Start with homeostatic adaptation
        threshold = self._homeostatic_adaptation()
        
        # Add context sensitivity
        if context is not None:
            context_adjustment = self._context_modulations.get(context, 0.0)
            threshold += self.context_sensitivity * context_adjustment
        
        # Add variability-based adjustment
        if len(self._ignition_history) >= 10:
            recent_variability = np.std(self._ignition_history[-20:])
            # Higher variability slightly increases threshold for stability
            variability_adjustment = 0.1 * recent_variability
            threshold += variability_adjustment
        
        return threshold
    
    def reset_threshold(self, new_baseline: Optional[float] = None) -> None:
        """
        Reset threshold to baseline and clear history.
        
        Args:
            new_baseline: New baseline threshold (if None, uses current baseline)
        """
        if new_baseline is not None:
            if new_baseline <= 0:
                raise MathematicalError("New baseline threshold must be positive")
            self.baseline_threshold = new_baseline
        
        self._current_threshold = self.baseline_threshold
        self._ignition_history.clear()
        self._threshold_history.clear()
    
    def get_ignition_statistics(self) -> Dict[str, float]:
        """
        Get statistics about recent ignition patterns.
        
        Returns:
            Dictionary with ignition statistics
        """
        if len(self._ignition_history) == 0:
            return {
                'ignition_rate': 0.0,
                'n_trials': 0,
                'variability': 0.0,
                'recent_rate': 0.0
            }
        
        ignition_array = np.array(self._ignition_history, dtype=float)
        
        stats = {
            'ignition_rate': float(np.mean(ignition_array)),
            'n_trials': len(self._ignition_history),
            'variability': float(np.std(ignition_array)),
            'recent_rate': float(np.mean(ignition_array[-10:])) if len(ignition_array) >= 10 else float(np.mean(ignition_array))
        }
        
        return stats
    
    def update_context_modulation(self, 
                                 context: ContextType, 
                                 modulation: float) -> None:
        """
        Update threshold modulation for a specific context.
        
        Args:
            context: Context type to update
            modulation: New modulation value (can be negative)
        """
        self._context_modulations[context] = modulation
    
    def get_threshold_info(self) -> dict:
        """
        Get information about threshold manager configuration.
        
        Returns:
            Dictionary with threshold manager settings
        """
        return {
            "baseline_threshold": self.baseline_threshold,
            "min_threshold": self.min_threshold,
            "max_threshold": self.max_threshold,
            "current_threshold": self._current_threshold,
            "adaptation_type": self.adaptation_type.value,
            "target_ignition_rate": self.target_ignition_rate,
            "adaptation_rate": self.adaptation_rate,
            "context_sensitivity": self.context_sensitivity,
            "context_modulations": {ctx.value: mod for ctx, mod in self._context_modulations.items()},
            "history_length": len(self._ignition_history),
            "threshold_history_length": len(self._threshold_history)
        }