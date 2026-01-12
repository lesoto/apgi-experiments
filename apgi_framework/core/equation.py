"""
Core APGI ignition threshold equation implementation.

This module implements the fundamental APGI equation for calculating surprise
and ignition probability based on precision-weighted prediction errors.

The core equation is:
- Surprise: Sₜ = Πₑ·|εₑ| + Πᵢ(M_{c,a})·|εᵢ|
- Ignition Probability: Bₜ = σ(α(Sₜ - θₜ))
"""

import numpy as np
from typing import Union, Optional, TYPE_CHECKING
import warnings
import logging

from apgi_framework.exceptions import MathematicalError

if TYPE_CHECKING:
    from apgi_framework.core.precision import PrecisionCalculator
    from apgi_framework.core.prediction_error import PredictionErrorProcessor
    from apgi_framework.core.somatic_marker import SomaticMarkerEngine
    from apgi_framework.core.threshold import ThresholdManager


class APGIEquation:
    """
    Core implementation of the APGI ignition threshold equation.

    This class provides methods for calculating precision-weighted surprise
    and ignition probability based on the APGI Framework mathematical model.
    Integrates with PrecisionCalculator, PredictionErrorProcessor,
    SomaticMarkerEngine, and ThresholdManager for complete functionality.
    """

    def __init__(
        self,
        precision_calculator: Optional["PrecisionCalculator"] = None,
        prediction_error_processor: Optional["PredictionErrorProcessor"] = None,
        somatic_marker_engine: Optional["SomaticMarkerEngine"] = None,
        threshold_manager: Optional["ThresholdManager"] = None,
        numerical_stability: bool = True,
    ):
        """
        Initialize the APGI equation calculator with integrated components.

        Args:
            precision_calculator: Calculator for precision values (Πₑ, Πᵢ)
            prediction_error_processor: Processor for prediction errors (εₑ, εᵢ)
            somatic_marker_engine: Engine for somatic marker gain (M_{c,a})
            threshold_manager: Manager for dynamic threshold (θₜ)
            numerical_stability: Whether to apply numerical stability measures
        """
        self.numerical_stability = numerical_stability
        self._max_sigmoid_input = 500.0  # Prevent overflow in sigmoid

        # Integrated components
        self.precision_calculator = precision_calculator
        self.prediction_error_processor = prediction_error_processor
        self.somatic_marker_engine = somatic_marker_engine
        self.threshold_manager = threshold_manager

        # Initialize logger
        self.logger = logging.getLogger(__name__)

    def calculate_surprise(
        self,
        extero_error: float,
        intero_error: float,
        extero_precision: float,
        intero_precision: float,
        somatic_gain: float = 1.0,
    ) -> float:
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
            # Clamp to valid range without warning - this can happen in normal operations
            # when precision-weighted errors cancel out
            surprise = 0.0
        elif surprise > 10:
            # Log at debug level only - this is expected for large prediction errors
            self.logger.debug(
                f"Surprise value {surprise:.3f} exceeds typical range (0-10), clamping to 10"
            )
            surprise = 10.0

        return float(surprise)

    def calculate_ignition_probability(
        self, surprise: float, threshold: float, steepness: float = 2.0
    ) -> float:
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
            sigmoid_input = np.clip(
                sigmoid_input, -self._max_sigmoid_input, self._max_sigmoid_input
            )

        # Calculate logistic sigmoid
        try:
            probability = self._logistic_sigmoid(sigmoid_input)
        except (OverflowError, FloatingPointError) as e:
            raise MathematicalError(f"Numerical error in sigmoid calculation: {e}")

        return float(probability)

    def is_ignition_triggered(
        self,
        surprise: float,
        threshold: float,
        steepness: float = 2.0,
        probability_threshold: float = 0.5,
    ) -> bool:
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
        probability = self.calculate_ignition_probability(
            surprise, threshold, steepness
        )
        return probability >= probability_threshold

    def _logistic_sigmoid(
        self, x: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
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

    def calculate_full_equation(
        self,
        extero_error: float,
        intero_error: float,
        extero_precision: float,
        intero_precision: float,
        threshold: float,
        steepness: float = 2.0,
        somatic_gain: float = 1.0,
    ) -> tuple[float, float]:
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
            extero_error, intero_error, extero_precision, intero_precision, somatic_gain
        )

        probability = self.calculate_ignition_probability(
            surprise, threshold, steepness
        )

        return surprise, probability

    def calculate_integrated_surprise(
        self,
        raw_extero_error: float,
        raw_intero_error: float,
        extero_variance: float,
        intero_variance: float,
        context: Optional["ContextType"] = None,
        arousal: float = 1.0,
        valence: float = 0.0,
        stakes: float = 1.0,
    ) -> float:
        """
        Calculate surprise using integrated components for full processing pipeline.

        Args:
            raw_extero_error: Raw exteroceptive prediction error
            raw_intero_error: Raw interoceptive prediction error
            extero_variance: Variance for exteroceptive precision calculation
            intero_variance: Variance for interoceptive precision calculation
            context: Contextual situation for somatic marker
            arousal: Arousal level for somatic marker and threshold
            valence: Emotional valence for somatic marker
            stakes: Situational stakes for somatic marker

        Returns:
            Total precision-weighted surprise

        Raises:
            MathematicalError: If required components are not available
        """
        if not all(
            [
                self.precision_calculator,
                self.prediction_error_processor,
                self.somatic_marker_engine,
            ]
        ):
            raise MathematicalError(
                "Required components not available for integrated calculation"
            )

        # Process prediction errors
        processed_extero_error = (
            self.prediction_error_processor.process_exteroceptive_error(
                raw_extero_error
            )
        )
        processed_intero_error = (
            self.prediction_error_processor.process_interoceptive_error(
                raw_intero_error
            )
        )

        # Calculate precisions
        extero_precision = self.precision_calculator.calculate_exteroceptive_precision(
            extero_variance
        )
        intero_precision = self.precision_calculator.calculate_interoceptive_precision(
            intero_variance, arousal=arousal
        )

        # Calculate somatic marker gain
        from .somatic_marker import ContextType

        context_enum = context if context is not None else ContextType.NEUTRAL
        somatic_gain = self.somatic_marker_engine.calculate_somatic_gain(
            context=context_enum, arousal=arousal, valence=valence, stakes=stakes
        )

        # Calculate final surprise
        return self.calculate_surprise(
            extero_error=processed_extero_error,
            intero_error=processed_intero_error,
            extero_precision=extero_precision,
            intero_precision=intero_precision,
            somatic_gain=somatic_gain,
        )

    def calculate_integrated_ignition_probability(
        self,
        raw_extero_error: float,
        raw_intero_error: float,
        extero_variance: float,
        intero_variance: float,
        context: Optional["ContextType"] = None,
        arousal: float = 1.0,
        valence: float = 0.0,
        stakes: float = 1.0,
        steepness: float = 2.0,
    ) -> tuple[float, float]:
        """
        Calculate both surprise and ignition probability using integrated components.

        Args:
            raw_extero_error: Raw exteroceptive prediction error
            raw_intero_error: Raw interoceptive prediction error
            extero_variance: Variance for exteroceptive precision calculation
            intero_variance: Variance for interoceptive precision calculation
            context: Contextual situation
            arousal: Arousal level
            valence: Emotional valence
            stakes: Situational stakes
            steepness: Sigmoid steepness parameter

        Returns:
            Tuple of (surprise, ignition_probability)

        Raises:
            MathematicalError: If required components are not available
        """
        if not self.threshold_manager:
            raise MathematicalError(
                "ThresholdManager not available for integrated calculation"
            )

        # Calculate surprise using integrated components
        surprise = self.calculate_integrated_surprise(
            raw_extero_error=raw_extero_error,
            raw_intero_error=raw_intero_error,
            extero_variance=extero_variance,
            intero_variance=intero_variance,
            context=context,
            arousal=arousal,
            valence=valence,
            stakes=stakes,
        )

        # Get current threshold from threshold manager
        from .somatic_marker import ContextType

        context_enum = context if context is not None else ContextType.NEUTRAL
        current_threshold = self.threshold_manager.get_current_threshold(
            context=context_enum, arousal=arousal
        )

        # Calculate ignition probability
        probability = self.calculate_ignition_probability(
            surprise=surprise, threshold=current_threshold, steepness=steepness
        )

        return surprise, probability

    def update_threshold_from_ignition(
        self, ignition_occurred: bool, context: Optional["ContextType"] = None
    ) -> float:
        """
        Update threshold based on ignition outcome using integrated ThresholdManager.

        Args:
            ignition_occurred: Whether ignition occurred in the last trial
            context: Current contextual situation

        Returns:
            Updated threshold value

        Raises:
            MathematicalError: If ThresholdManager is not available
        """
        if not self.threshold_manager:
            raise MathematicalError(
                "ThresholdManager not available for threshold update"
            )

        from .somatic_marker import ContextType

        context_enum = context if context is not None else ContextType.NEUTRAL

        return self.threshold_manager.update_threshold(
            ignition_occurred=ignition_occurred, context=context_enum
        )

    def validate_integrated_components(self) -> dict:
        """
        Validate that all integrated components are properly configured.

        Returns:
            Dictionary with validation results for each component
        """
        validation_results = {
            "precision_calculator": self.precision_calculator is not None,
            "prediction_error_processor": self.prediction_error_processor is not None,
            "somatic_marker_engine": self.somatic_marker_engine is not None,
            "threshold_manager": self.threshold_manager is not None,
            "all_components_available": False,
        }

        validation_results["all_components_available"] = all(
            [
                validation_results["precision_calculator"],
                validation_results["prediction_error_processor"],
                validation_results["somatic_marker_engine"],
                validation_results["threshold_manager"],
            ]
        )

        return validation_results

    def get_equation_info(self) -> dict:
        """
        Get information about the equation implementation.

        Returns:
            Dictionary with equation details and parameters.
        """
        component_info = self.validate_integrated_components()

        return {
            "equation_name": "APGI Ignition Threshold Equation",
            "surprise_formula": "Sₜ = Πₑ·|εₑ| + Πᵢ(M_{c,a})·|εᵢ|",
            "ignition_formula": "Bₜ = σ(α(Sₜ - θₜ))",
            "numerical_stability": self.numerical_stability,
            "max_sigmoid_input": self._max_sigmoid_input,
            "expected_surprise_range": "0-10 (dimensionless)",
            "probability_range": "0-1",
            "integrated_components": component_info,
            "available_methods": [
                "calculate_surprise",
                "calculate_ignition_probability",
                "calculate_integrated_surprise",
                "calculate_integrated_ignition_probability",
                "update_threshold_from_ignition",
            ],
        }
