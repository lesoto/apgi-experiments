"""
Precision calculation module for the APGI Framework.

This module implements precision calculations for both exteroceptive (Πₑ)
and interoceptive (Πᵢ) components, including validation and edge case handling.
"""

import warnings
from typing import Tuple

import numpy as np

from apgi_framework.exceptions import MathematicalError


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

    def calculate_exteroceptive_precision(
        self, variance: float, confidence: float = 1.0
    ) -> float:
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

    def calculate_interoceptive_precision(
        self, variance: float, attention: float = 1.0, arousal: float = 1.0
    ) -> float:
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

    def calculate_precision_from_samples(
        self, samples: np.ndarray, method: str = "inverse_variance"
    ) -> float:
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
                warnings.warn(
                    "Zero or negative standard deviation, using minimum precision"
                )
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

    def validate_precision_pair(
        self, extero_precision: float, intero_precision: float
    ) -> Tuple[bool, str]:
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
                return (
                    False,
                    f"Exteroceptive precision {extero_precision} out of bounds [{self.min_precision}, {self.max_precision}]",
                )

            if not (self.min_precision <= intero_precision <= self.max_precision):
                return (
                    False,
                    f"Interoceptive precision {intero_precision} out of bounds [{self.min_precision}, {self.max_precision}]",
                )

            # Check for reasonable ratios (optional validation)
            ratio = extero_precision / intero_precision
            if ratio > 1000 or ratio < 0.001:
                return (
                    False,
                    f"Precision ratio {ratio:.3f} may indicate unrealistic values",
                )

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
            warnings.warn(
                f"Precision {precision} below minimum, clipping to {self.min_precision}"
            )
            return self.min_precision
        elif precision > self.max_precision:
            warnings.warn(
                f"Precision {precision} above maximum, clipping to {self.max_precision}"
            )
            return self.max_precision
        else:
            return precision

    def calculate_precision(
        self, data: np.ndarray, method: str = "inverse_variance"
    ) -> float:
        """
        Calculate precision from sample data (alias for calculate_precision_from_samples).

        Args:
            data: Array of prediction error samples
            method: Calculation method ("inverse_variance", "inverse_std", "fisher_information")

        Returns:
            Calculated precision value
        """
        return self.calculate_precision_from_samples(data, method)

    def confidence_interval(self, data: np.ndarray, confidence: float = 0.95) -> tuple:
        """
        Calculate confidence interval for data.

        Args:
            data: Array of samples
            confidence: Confidence level (default 0.95)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if len(data) == 0:
            raise MathematicalError("Cannot calculate CI for empty data")
        if len(data) < 2:
            raise MathematicalError("Need at least 2 samples for CI calculation")

        from scipy import stats

        mean = np.mean(data)
        sem = stats.sem(data)  # Standard error of mean
        df = len(data) - 1  # Degrees of freedom

        # Get t-value for confidence level
        t_value = stats.t.ppf((1 + confidence) / 2, df)

        margin = t_value * sem
        return (mean - margin, mean + margin)

    def relative_precision(self, data: np.ndarray) -> float:
        """
        Calculate relative precision (coefficient of variation inverse).

        Args:
            data: Array of samples

        Returns:
            Relative precision value
        """
        mean = np.mean(data)
        std = np.std(data, ddof=1)

        if std == 0:
            return float("inf") if mean == 0 else self.max_precision

        cv = std / abs(mean) if mean != 0 else float("inf")
        if cv == 0:
            return self.max_precision

        return min(1.0 / cv, self.max_precision)

    def coefficient_of_variation(self, data: np.ndarray) -> float:
        """
        Calculate coefficient of variation (CV).

        Args:
            data: Array of samples

        Returns:
            Coefficient of variation
        """
        mean = np.mean(data)
        std = np.std(data, ddof=1)

        if mean == 0:
            return 0.0 if std == 0 else float("inf")

        return float(std / abs(mean))

    def standard_error(self, data: np.ndarray) -> float:
        """
        Calculate standard error of the mean.

        Args:
            data: Array of samples

        Returns:
            Standard error
        """
        if len(data) == 0:
            raise MathematicalError("Cannot calculate SE for empty data")

        return float(np.std(data, ddof=1) / np.sqrt(len(data)))

    def calculate_precision_batch(
        self, datasets: list, method: str = "inverse_variance"
    ) -> list:
        """
        Calculate precision for multiple datasets.

        Args:
            datasets: List of numpy arrays
            method: Calculation method

        Returns:
            List of precision values
        """
        return [self.calculate_precision(d, method) for d in datasets]

    def precision_metrics(self, data: np.ndarray) -> dict:
        """
        Calculate comprehensive precision metrics.

        Args:
            data: Array of samples

        Returns:
            Dictionary with precision metrics
        """
        return {
            "precision": self.calculate_precision(data),
            "confidence_interval_95": self.confidence_interval(data, 0.95),
            "relative_precision": self.relative_precision(data),
            "coefficient_of_variation": self.coefficient_of_variation(data),
            "standard_error": self.standard_error(data),
        }

    def get_precision_info(self) -> dict:
        """
        Get information about precision calculation settings.

        Returns:
            Dictionary with precision calculator configuration
        """
        return {
            "min_precision": self.min_precision,
            "max_precision": self.max_precision,
            "calculation_methods": [
                "inverse_variance",
                "inverse_std",
                "fisher_information",
            ],
            "extero_modulation_factors": ["confidence"],
            "intero_modulation_factors": ["attention", "arousal"],
        }
