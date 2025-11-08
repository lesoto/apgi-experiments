"""
Test script for validation and error handling functionality.

This script demonstrates the new validation and error handling features.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ipi_framework.validation import (
    get_validator,
    get_health_checker,
    get_recovery_manager
)
from ipi_framework.config import IPIParameters, ExperimentalConfig
from ipi_framework.exceptions import ValidationError, ConfigurationError


def test_parameter_validation():
    """Test parameter validation"""
    print("\n" + "=" * 60)
    print("TEST: Parameter Validation")
    print("=" * 60)
    
    validator = get_validator()
    
    # Test valid parameters
    print("\n1. Testing valid IPI parameters...")
    result = validator.validate_ipi_parameters(
        extero_precision=2.0,
        intero_precision=1.5,
        extero_error=1.2,
        intero_error=0.8,
        somatic_gain=1.3,
        threshold=3.5,
        steepness=2.0
    )
    print(result.get_message())
    assert result.is_valid, "Valid parameters should pass validation"
    print("✓ Valid parameters passed")
    
    # Test invalid parameters
    print("\n2. Testing invalid IPI parameters...")
    result = validator.validate_ipi_parameters(
        extero_precision=-1.0,  # Invalid: negative
        intero_precision=1.5,
        extero_error=1.2,
        intero_error=0.8,
        somatic_gain=1.3,
        threshold=3.5,
        steepness=2.0
    )
    print(result.get_message())
    assert not result.is_valid, "Invalid parameters should fail validation"
    print("✓ Invalid parameters correctly rejected")
    
    # Test experimental config
    print("\n3. Testing experimental configuration...")
    result = validator.validate_experimental_config(
        n_trials=100,
        n_participants=50,
        alpha_level=0.05
    )
    print(result.get_message())
    assert result.is_valid, "Valid config should pass validation"
    print("✓ Valid experimental config passed")
    
    print("\n✓ All parameter validation tests passed!")


def test_config_integration():
    """Test configuration with validation"""
    print("\n" + "=" * 60)
    print("TEST: Configuration Integration")
    print("=" * 60)
    
    # Test valid configuration
    print("\n1. Creating valid IPI parameters...")
    try:
        params = IPIParameters(
            extero_precision=2.0,
            intero_precision=1.5,
            extero_error=1.2,
            intero_error=0.8,
            somatic_gain=1.3,
            threshold=3.5,
            steepness=2.0
        )
        print("✓ Valid IPI parameters created successfully")
    except Exception as e:
        print(f"✗ Failed to create valid parameters: {e}")
        raise
    
    # Test invalid configuration
    print("\n2. Testing invalid IPI parameters...")
    try:
        params = IPIParameters(
            extero_precision=-1.0,  # Invalid
            intero_precision=1.5,
            extero_error=1.2,
            intero_error=0.8,
            somatic_gain=1.3,
            threshold=3.5,
            steepness=2.0
        )
        print("✗ Invalid parameters should have raised error")
        assert False, "Should have raised ConfigurationError"
    except ConfigurationError as e:
        print(f"✓ Invalid parameters correctly rejected: {str(e)[:100]}...")
    
    print("\n✓ All configuration integration tests passed!")


def test_system_health():
    """Test system health checker"""
    print("\n" + "=" * 60)
    print("TEST: System Health Check")
    print("=" * 60)
    
    health_checker = get_health_checker()
    
    # Run full health check
    print("\n1. Running full system health check...")
    result = health_checker.run_full_health_check()
    print(result.get_report())
    
    # Check specific component
    print("\n2. Checking Python environment...")
    result = health_checker.check_component("python")
    print(f"Status: {result.overall_status}")
    
    # Get diagnostic info
    print("\n3. Getting diagnostic information...")
    info = health_checker.get_diagnostic_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n✓ System health check completed!")


def test_error_recovery():
    """Test error recovery mechanisms"""
    print("\n" + "=" * 60)
    print("TEST: Error Recovery")
    print("=" * 60)
    
    recovery_manager = get_recovery_manager()
    
    # Test error logging
    print("\n1. Testing error logging...")
    from ipi_framework.exceptions import SimulationError
    test_error = SimulationError("Test simulation error")
    context = {'test': 'context', 'value': 123}
    recovery_manager.log_error(test_error, context)
    print("✓ Error logged successfully")
    
    # Get error statistics
    print("\n2. Getting error statistics...")
    stats = recovery_manager.get_error_statistics()
    print(f"  Total errors: {stats['total_errors']}")
    print(f"  Error types: {stats.get('error_types', {})}")
    print("✓ Error statistics retrieved")
    
    print("\n✓ Error recovery tests completed!")


def test_parameter_info():
    """Test parameter information retrieval"""
    print("\n" + "=" * 60)
    print("TEST: Parameter Information")
    print("=" * 60)
    
    validator = get_validator()
    
    # Get info for various parameters
    params_to_check = ['threshold', 'extero_precision', 'n_trials', 'p3b_threshold']
    
    for param in params_to_check:
        print(f"\n{param}:")
        info = validator.get_parameter_info(param)
        print(f"  {info}")
    
    print("\n✓ Parameter information tests completed!")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("IPI FRAMEWORK VALIDATION & ERROR HANDLING TEST SUITE")
    print("=" * 60)
    
    try:
        test_parameter_validation()
        test_config_integration()
        test_system_health()
        test_error_recovery()
        test_parameter_info()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60 + "\n")
        
        return 0
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ TEST FAILED: {str(e)}")
        print("=" * 60 + "\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
