"""
Exception classes for the IPI Framework Falsification Testing System.

This module defines the hierarchy of exceptions used throughout the framework
to handle various error conditions in mathematical calculations, simulations,
statistical analysis, and experimental validation.
"""


class IPIFrameworkError(Exception):
    """Base exception for all IPI Framework errors."""
    pass


class MathematicalError(IPIFrameworkError):
    """Errors in mathematical calculations and computations."""
    pass


class SimulationError(IPIFrameworkError):
    """Errors in neural signature simulation and generation."""
    pass


class StatisticalError(IPIFrameworkError):
    """Errors in statistical analysis and validation."""
    pass


class ValidationError(IPIFrameworkError):
    """Errors in experimental validation and control mechanisms."""
    pass


class ConfigurationError(IPIFrameworkError):
    """Errors in configuration management and parameter validation."""
    pass


class DataError(IPIFrameworkError):
    """Errors in data management, storage, and retrieval."""
    pass