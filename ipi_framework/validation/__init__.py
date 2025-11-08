"""
Validation module for IPI Framework.

Provides parameter validation, system health checks, and diagnostic utilities.
"""

from .parameter_validator import (
    ParameterValidator,
    ValidationResult,
    get_validator
)
from .system_health import (
    SystemHealthChecker,
    HealthCheckResult,
    get_health_checker
)
from .error_recovery import (
    ErrorRecoveryManager,
    RetryConfig,
    with_retry,
    get_recovery_manager,
    safe_execute,
    validate_and_fix,
    initialize_default_recovery_strategies
)

# Initialize default recovery strategies on import
initialize_default_recovery_strategies()

__all__ = [
    'ParameterValidator',
    'ValidationResult',
    'get_validator',
    'SystemHealthChecker',
    'HealthCheckResult',
    'get_health_checker',
    'ErrorRecoveryManager',
    'RetryConfig',
    'with_retry',
    'get_recovery_manager',
    'safe_execute',
    'validate_and_fix',
]
