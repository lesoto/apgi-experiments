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


# Mock classes for testing
class DesignValidator:
    """Mock design validator for testing purposes."""

    def __init__(self):
        self.validation_rules = {}
        self.validation_results = {}

    def add_validation_rule(self, rule_name, rule_function):
        """Add a validation rule."""
        self.validation_rules[rule_name] = rule_function

    def validate_design(self, design_data):
        """Validate a design against all rules."""
        validation_id = f"validation_{hash(str(design_data)) % 10000:04d}"
        results = {}

        for rule_name, rule_function in self.validation_rules.items():
            try:
                results[rule_name] = rule_function(design_data)
            except Exception as e:
                results[rule_name] = {"valid": False, "error": str(e)}

        validation_result = {
            "validation_id": validation_id,
            "design_data": design_data,
            "rule_results": results,
            "overall_valid": all(r.get("valid", False) for r in results.values()),
            "timestamp": "2024-01-01T00:00:00Z",
        }

        self.validation_results[validation_id] = validation_result
        return validation_result

    def get_validation_result(self, validation_id):
        """Get validation result by ID."""
        return self.validation_results.get(validation_id)


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
    # Mock classes for testing
    "DesignValidator",
]
