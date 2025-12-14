"""
Exception classes for the APGI Framework Falsification Testing System.

This module defines the hierarchy of exceptions used throughout the framework
to handle various error conditions in mathematical calculations, simulations,
statistical analysis, and experimental validation.
"""


class APGIFrameworkError(Exception):
    """Base exception for all APGI Framework errors."""
    pass


class MathematicalError(APGIFrameworkError):
    """Errors in mathematical calculations and computations."""
    pass


class SimulationError(APGIFrameworkError):
    """Errors in neural signature simulation and generation."""
    pass


class StatisticalError(APGIFrameworkError):
    """Errors in statistical analysis and validation."""
    pass


class ValidationError(APGIFrameworkError):
    """Errors in experimental validation and control mechanisms."""
    pass


class ConfigurationError(APGIFrameworkError):
    """Errors in configuration management and parameter validation."""
    pass


class DataError(APGIFrameworkError):
    """Errors in data management, storage, and retrieval."""
    pass


class DataManagementError(APGIFrameworkError):
    """Errors in integrated data management operations."""
    pass


class VisualizationError(APGIFrameworkError):
    """Errors in visualization and plotting operations."""
    pass


class DashboardError(APGIFrameworkError):
    """Errors in dashboard and monitoring operations."""
    pass


class PersistenceError(APGIFrameworkError):
    """Errors in data persistence and storage operations."""
    pass


class ReportGenerationError(APGIFrameworkError):
    """Errors in report generation operations."""
    pass


class DataExportError(APGIFrameworkError):
    """Errors in data export operations."""
    pass