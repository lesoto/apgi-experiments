"""
Validation module for APGI Framework.

Provides parameter validation, system health checks, and diagnostic utilities.
"""

from .error_recovery import (
    ErrorRecoveryManager,
    RetryConfig,
    get_recovery_manager,
    initialize_default_recovery_strategies,
    safe_execute,
    validate_and_fix,
    with_retry,
)
from .parameter_validator import ParameterValidator, ValidationResult, get_validator
from .system_health import HealthCheckResult, SystemHealthChecker, get_health_checker

# Initialize default recovery strategies on import
initialize_default_recovery_strategies()

__all__ = [
    "ParameterValidator",
    "ValidationResult",
    "get_validator",
    "SystemHealthChecker",
    "HealthCheckResult",
    "get_health_checker",
    "ErrorRecoveryManager",
    "RetryConfig",
    "with_retry",
    "get_recovery_manager",
    "safe_execute",
    "validate_and_fix",
]
