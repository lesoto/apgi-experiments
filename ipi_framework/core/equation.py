"""
Core IPI ignition threshold equation implementation.

This module implements the fundamental IPI equation for calculating surprise
and ignition probability based on precision-weighted prediction errors.

The core equation is:
- Surprise: Sₜ = Πₑ·|εₑ| + Πᵢ(M_{c,a})·|εᵢ|
- Ignition Probability: Bₜ = σ(α(Sₜ - θₜ))
"""

import numpy as np
from typing import Union, Optional
import warnings

from ..exceptions import MathematicalError


class IPIEquation:
    """
    Core implementation of the IPI ignition threshold equation.
    
    This class provides methods for calculating precision-weighted surprise
    and ignition probability based on the IPI Framework mathematical model.
    """
    
    def __init__(self, numerical_stability: bool = True):
        """
        Initialize the IPI equation calculator.
        
        Args:
            numerical_stability: Whether to apply numerical stability measures
                                for sigmoid calculations.
        """
        self.numerical_stability = numerical_stability
        self._max_sigmoid_input = 500.0  # Prevent overflow in sigmoid
    
    def calculate_surprise(self, 
                          extero_error: float,
                          intero_error: float, 
                          extero_precision: float,
                          intero_precision: float,
                          somatic_gain: float = 1.0) -> float:
        """
        Calculate total precision-weighted surprise.
        
        Implements: Sₜ = Πₑ·|εₑ| + Πᵢ(M_{c,a})·|εᵢ|
        
        Args:
            extero_error: Exteroceptive prediction error (εₑ)
            intero_error: Interoceptive prediction error (εᵢ)  
            extero_precision: Exteroceptive precision (Πₑ)
            intero_precision: Base interoceptive precision (Πᵢ)
            somatic_gain: Somatic marker gain (M_{c,a})
            
        Returns:
            Total precision-weighted surprise (dimensionless, range 0-10)
            
        Raises:
            MathematicalError: If precision values are non-positive or
                              if somatic gain is non-positive.
        """
        # Validate inputs
        if extero_precision <= 0:
            raise MathematicalError("Exteroceptive precision must be positive")
        if intero_precision <= 0:
            raise MathematicalError("Interoceptive precision must be positive")
        if somatic_gain <= 0:
            raise MathematicalError("Somatic marker gain must be positive")
        
        # Calculate precision-weighted surprise components
        extero_component = extero_precision * abs(extero_error)
        
        # Apply somatic marker gain to interoceptive precision
        modulated_intero_precision = intero_precision * somatic_gain
        intero_component = modulated_intero_precision * abs(intero_error)
        
        # Total surprise
        surprise = extero_component + intero_component
        
        # Ensure output is in expected range (0-10)
        if surprise < 0:
            warnings.warn("Negative surprise calculated, setting to 0")
            surprise = 0.0
        elif surprise > 10:
            warnings.warn(f"Surprise value {surprise} exceeds expected range (0-10)")
        
        return float(surprise)
    
    def calculate_ignition_probability(self,
                                     surprise: float,
                                     threshold: float,
                                     steepness: float = 2.0) -> float:
        """
        Calculate ignition probability using logistic sigmoid function.
        
        Implements: Bₜ = σ(α(Sₜ - θₜ))
        
        Args:
            surprise: Total precision-weighted surprise (Sₜ)
            threshold: Ignition threshold (θₜ)
            steepness: Sigmoid steepness parameter (α)
            
        Returns:
            Ignition probability (0-1)
            
        Raises:
            MathematicalError: If steepness parameter is non-positive.
        """
        if steepness <= 0:
            raise MathematicalError("Steepness parameter must be positive")
        
        # Calculate sigmoid input
        sigmoid_input = steepness * (surprise - threshold)
        
        # Apply numerical stability if enabled
        if self.numerical_stability:
            sigmoid_input = np.clip(sigmoid_input, 
                                  -self._max_sigmoid_input, 
                                  self._max_sigmoid_input)
        
        # Calculate logistic sigmoid
        try:
            probability = self._logistic_sigmoid(sigmoid_input)
        except (OverflowError, FloatingPointError) as e:
            raise MathematicalError(f"Numerical error in sigmoid calculation: {e}")
        
        return float(probability)
    
    def is_ignition_triggered(self,
                             surprise: float,
                             threshold: float,
                             steepness: float = 2.0,
                             probability_threshold: float = 0.5) -> bool:
        """
        Determine if ignition is triggered based on probability threshold.
        
        Args:
            surprise: Total precision-weighted surprise
            threshold: Ignition threshold
            steepness: Sigmoid steepness parameter
            probability_threshold: Minimum probability for ignition (default 0.5)
            
        Returns:
            True if ignition is triggered, False otherwise
        """
        probability = self.calculate_ignition_probability(surprise, threshold, steepness)
        return probability >= probability_threshold
    
    def _logistic_sigmoid(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Compute logistic sigmoid function with numerical stability.
        
        σ(x) = 1 / (1 + exp(-x))
        
        Args:
            x: Input value(s)
            
        Returns:
            Sigmoid output(s)
        """
        # Use numerically stable implementation
        # For x >= 0: σ(x) = 1 / (1 + exp(-x))
        # For x < 0: σ(x) = exp(x) / (1 + exp(x))
        
        if isinstance(x, np.ndarray):
            result = np.zeros_like(x)
            positive_mask = x >= 0
            negative_mask = ~positive_mask
            
            if np.any(positive_mask):
                result[positive_mask] = 1.0 / (1.0 + np.exp(-x[positive_mask]))
            if np.any(negative_mask):
                exp_x = np.exp(x[negative_mask])
                result[negative_mask] = exp_x / (1.0 + exp_x)
                
            return result
        else:
            if x >= 0:
                return 1.0 / (1.0 + np.exp(-x))
            else:
                exp_x = np.exp(x)
                return exp_x / (1.0 + exp_x)
    
    def calculate_full_equation(self,
                               extero_error: float,
                               intero_error: float,
                               extero_precision: float, 
                               intero_precision: float,
                               threshold: float,
                               steepness: float = 2.0,
                               somatic_gain: float = 1.0) -> tuple[float, float]:
        """
        Calculate both surprise and ignition probability in one call.
        
        Args:
            extero_error: Exteroceptive prediction error
            intero_error: Interoceptive prediction error
            extero_precision: Exteroceptive precision
            intero_precision: Interoceptive precision
            threshold: Ignition threshold
            steepness: Sigmoid steepness parameter
            somatic_gain: Somatic marker gain
            
        Returns:
            Tuple of (surprise, ignition_probability)
        """
        surprise = self.calculate_surprise(
            extero_error, intero_error, extero_precision, 
            intero_precision, somatic_gain
        )
        
        probability = self.calculate_ignition_probability(
            surprise, threshold, steepness
        )
        
        return surprise, probability
    
    def get_equation_info(self) -> dict:
        """
        Get information about the equation implementation.
        
        Returns:
            Dictionary with equation details and parameters.
        """
        return {
            "equation_name": "IPI Ignition Threshold Equation",
            "surprise_formula": "Sₜ = Πₑ·|εₑ| + Πᵢ(M_{c,a})·|εᵢ|",
            "ignition_formula": "Bₜ = σ(α(Sₜ - θₜ))",
            "numerical_stability": self.numerical_stability,
            "max_sigmoid_input": self._max_sigmoid_input,
            "expected_surprise_range": "0-10 (dimensionless)",
            "probability_range": "0-1"
        }