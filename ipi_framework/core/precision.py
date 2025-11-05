"""
Precision calculation module for the IPI Framework.

This module implements precision calculations for both exteroceptive (Πₑ)
and interoceptive (Πᵢ) components, including validation and edge case handling.
"""

import numpy as np
from typing import Union, Optional, Tuple
import warnings

from ..exceptions import MathematicalError


class PrecisionCalculator:
    """
    Calculator for exteroceptive and interoceptive precision values.
    
    Precision represents the inverse of uncertainty/variance in prediction
    errors, with higher precision indicating more reliable predictions.
    """
    
    def __init__(self, min_precision: float = 1e-6, max_precision: float = 100.0):
        """
        Initialize precision calculator with bounds.
        
        Args:
            min_precision: Minimum allowed precision value to prevent division by zero
            max_precision: Maximum allowed precision value to prevent numerical issues
        """
        if min_precision <= 0:
            raise MathematicalError("Minimum precision must be positive")
        if max_precision <= min_precision:
            raise MathematicalError("Maximum precision must be greater than minimum")
            
        self.min_precision = min_precision
        self.max_precision = max_precision
    
    def calculate_exteroceptive_precision(self,
                                        variance: float,
                                        confidence: float = 1.0) -> float:
        """
        Calculate exteroceptive precision (Πₑ).
        
        Precision is typically the inverse of variance, modulated by confidence.
        
        Args:
            variance: Variance of exteroceptive prediction errors
            confidence: Confidence modulation factor (default 1.0)
            
        Returns:
            Exteroceptive precision value
            
        Raises:
            MathematicalError: If variance is non-positive or confidence is non-positive
        """
        if variance <= 0:
            raise MathematicalError("Variance must be positive")
        if confidence <= 0:
            raise MathematicalError("Confidence must be positive")
        
        # Calculate precision as inverse variance, modulated by confidence
        precision = confidence / variance
        
        # Apply bounds
        precision = self._apply_precision_bounds(precision)
        
        return float(precision)
    
    def calculate_interoceptive_precision(self,
                                        variance: float,
                                        attention: float = 1.0,
                                        arousal: float = 1.0) -> float:
        """
        Calculate base interoceptive precision (Πᵢ).
        
        Interoceptive precision can be modulated by attention and arousal states.
        
        Args:
            variance: Variance of interoceptive prediction errors
            attention: Attention modulation factor (default 1.0)
            arousal: Arousal modulation factor (default 1.0)
            
        Returns:
            Base interoceptive precision value
            
        Raises:
            MathematicalError: If variance is non-positive or modulation factors are non-positive
        """
        if variance <= 0:
            raise MathematicalError("Variance must be positive")
        if attention <= 0:
            raise MathematicalError("Attention factor must be positive")
        if arousal <= 0:
            raise MathematicalError("Arousal factor must be positive")
        
        # Calculate precision with attention and arousal modulation
        precision = (attention * arousal) / variance
        
        # Apply bounds
        precision = self._apply_precision_bounds(precision)
        
        return float(precision)
    
    def calculate_precision_from_samples(self,
                                       samples: np.ndarray,
                                       method: str = "inverse_variance") -> float:
        """
        Calculate precision from sample data.
        
        Args:
            samples: Array of prediction error samples
            method: Calculation method ("inverse_variance", "inverse_std", "fisher_information")
            
        Returns:
            Calculated precision value
            
        Raises:
            MathematicalError: If samples are invalid or method is unknown
        """
        if len(samples) == 0:
            raise MathematicalError("Sample array cannot be empty")
        
        samples = np.asarray(samples)
        
        if method == "inverse_variance":
            variance = np.var(samples, ddof=1)  # Sample variance
            if variance <= 0:
                warnings.warn("Zero or negative variance, using minimum precision")
                return self.min_precision
            precision = 1.0 / variance
            
        elif method == "inverse_std":
            std = np.std(samples, ddof=1)  # Sample standard deviation
            if std <= 0:
                warnings.warn("Zero or negative standard deviation, using minimum precision")
                return self.min_precision
            precision = 1.0 / std
            
        elif method == "fisher_information":
            # Simplified Fisher information approximation
            variance = np.var(samples, ddof=1)
            if variance <= 0:
                warnings.warn("Zero or negative variance, using minimum precision")
                return self.min_precision
            precision = len(samples) / variance
            
        else:
            raise MathematicalError(f"Unknown precision calculation method: {method}")
        
        # Apply bounds
        precision = self._apply_precision_bounds(precision)
        
        return float(precision)
    
    def validate_precision_pair(self,
                               extero_precision: float,
                               intero_precision: float) -> Tuple[bool, str]:
        """
        Validate a pair of exteroceptive and interoceptive precision values.
        
        Args:
            extero_precision: Exteroceptive precision value
            intero_precision: Interoceptive precision value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check individual bounds
            if not (self.min_precision <= extero_precision <= self.max_precision):
                return False, f"Exteroceptive precision {extero_precision} out of bounds [{self.min_precision}, {self.max_precision}]"
            
            if not (self.min_precision <= intero_precision <= self.max_precision):
                return False, f"Interoceptive precision {intero_precision} out of bounds [{self.min_precision}, {self.max_precision}]"
            
            # Check for reasonable ratios (optional validation)
            ratio = extero_precision / intero_precision
            if ratio > 1000 or ratio < 0.001:
                return False, f"Precision ratio {ratio:.3f} may indicate unrealistic values"
            
            return True, "Valid precision pair"
            
        except (TypeError, ValueError) as e:
            return False, f"Invalid precision values: {e}"
    
    def _apply_precision_bounds(self, precision: float) -> float:
        """
        Apply minimum and maximum bounds to precision value.
        
        Args:
            precision: Raw precision value
            
        Returns:
            Bounded precision value
        """
        if precision < self.min_precision:
            warnings.warn(f"Precision {precision} below minimum, clipping to {self.min_precision}")
            return self.min_precision
        elif precision > self.max_precision:
            warnings.warn(f"Precision {precision} above maximum, clipping to {self.max_precision}")
            return self.max_precision
        else:
            return precision
    
    def get_precision_info(self) -> dict:
        """
        Get information about precision calculation settings.
        
        Returns:
            Dictionary with precision calculator configuration
        """
        return {
            "min_precision": self.min_precision,
            "max_precision": self.max_precision,
            "calculation_methods": ["inverse_variance", "inverse_std", "fisher_information"],
            "extero_modulation_factors": ["confidence"],
            "intero_modulation_factors": ["attention", "arousal"]
        }