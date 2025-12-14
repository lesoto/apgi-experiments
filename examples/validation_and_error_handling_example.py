"""
Example: Using Validation and Error Handling Features

This example demonstrates how to use the new validation and error handling
features in the APGI Framework.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apgi_framework.validation import (
    get_validator, 
    get_health_checker,
    with_retry, 
    RetryConfig
)
from apgi_framework.config import APGIParameters, ExperimentalConfig, ConfigManager
from apgi_framework.falsification.primary_falsification_test import PrimaryFalsificationTest
from apgi_framework.falsification.error_handling_wrapper import (
    with_error_handling,
    ErrorHandlingTestWrapper
)
from apgi_framework.exceptions import ValidationError, ConfigurationError


def example_1_parameter_validation():
    """Example 1: Validating parameters before use"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Parameter Validation")
    print("=" * 60)
    
    validator = get_validator()
    
    # Validate APGI parameters
    print("\nValidating APGI parameters...")
    result = validator.validate_apgi_parameters(
        extero_precision=2.0,
        intero_precision=1.5,
        extero_error=1.2,
        intero_error=0.8,
        somatic_gain=1.3,
        threshold=3.5,
        steepness=2.0
    )
    
    if result.is_valid:
        print("✓ Parameters are valid!")
    else:
        print("✗ Parameters are invalid:")
        print(result.get_message())
    
    # Show warnings and suggestions even for valid parameters
    if result.warnings or result.suggestions:
        print("\nAdditional information:")
        print(result.get_message())


def example_2_system_health_check():
    """Example 2: Running system health check"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: System Health Check")
    print("=" * 60)
    
    health_checker = get_health_checker()
    
    # Run full health check
    print("\nRunning full system health check...")
    result = health_checker.run_full_health_check()
    
    # Show summary
    print(f"\nOverall Status: {result.overall_status.upper()}")
    print(f"Checks Passed: {result.checks_passed}")
    print(f"Checks Failed: {result.checks_failed}")
    print(f"Warnings: {result.checks_warning}")
    
    # Show component status
    print("\nComponent Status:")
    for component, status in result.component_status.items():
        status_icon = "✓" if status == "healthy" else "⚠️" if status == "warning" else "❌"
        print(f"  {status_icon} {component}: {status}")
    
    # Show recommendations if any
    if result.recommendations:
        print("\nRecommendations:")
        for rec in result.recommendations:
            print(f"  • {rec}")


def example_3_safe_configuration():
    """Example 3: Creating configuration with validation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Safe Configuration Creation")
    print("=" * 60)
    
    # Create valid configuration
    print("\n1. Creating valid configuration...")
    try:
        apgi_params = APGIParameters(
            extero_precision=2.0,
            intero_precision=1.5,
            extero_error=1.2,
            intero_error=0.8,
            somatic_gain=1.3,
            threshold=3.5,
            steepness=2.0
        )
        print("✓ Valid APGI parameters created")
        
        exp_config = ExperimentalConfig(
            n_trials=100,
            n_participants=50,
            alpha_level=0.05
        )
        print("✓ Valid experimental config created")
        
    except ConfigurationError as e:
        print(f"✗ Configuration error: {e}")
    
    # Try to create invalid configuration
    print("\n2. Attempting to create invalid configuration...")
    try:
        invalid_params = APGIParameters(
            extero_precision=-1.0,  # Invalid: negative
            intero_precision=1.5,
            extero_error=1.2,
            intero_error=0.8,
            somatic_gain=1.3,
            threshold=3.5,
            steepness=2.0
        )
        print("✗ Should have raised error!")
    except ConfigurationError as e:
        print(f"✓ Invalid configuration correctly rejected")
        print(f"   Error: {str(e)[:100]}...")


def example_4_safe_test_execution():
    """Example 4: Running tests with error handling"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Safe Test Execution")
    print("=" * 60)
    
    # Create test controller with error handling
    print("\n1. Creating test controller with error handling...")
    try:
        test_controller = PrimaryFalsificationTest()
        safe_controller = ErrorHandlingTestWrapper(test_controller)
        print("✓ Safe test controller created")
    except Exception as e:
        print(f"✗ Failed to create controller: {e}")
        return
    
    # Run test with automatic error handling
    print("\n2. Running test with error handling...")
    print("   (Using small parameters for quick demo)")
    try:
        result = safe_controller.run_falsification_test(
            n_trials=10,  # Small for demo
            n_participants=5
        )
        print(f"✓ Test completed successfully")
        print(f"   Falsification rate: {result.falsification_rate:.2%}")
        print(f"   Framework falsified: {result.is_framework_falsified}")
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    # Show error summary
    error_summary = safe_controller.get_error_summary()
    if error_summary['total_errors'] > 0:
        print(f"\n3. Error summary:")
        print(f"   Total errors: {error_summary['total_errors']}")
        print(f"   Error types: {error_summary['error_types']}")
    else:
        print(f"\n3. No errors encountered during test execution")


def example_5_parameter_info():
    """Example 5: Getting parameter information"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Parameter Information")
    print("=" * 60)
    
    validator = get_validator()
    
    # Get info for various parameters
    parameters = ['threshold', 'extero_precision', 'n_trials', 'p3b_threshold']
    
    print("\nParameter Information:")
    for param in parameters:
        print(f"\n{param}:")
        info = validator.get_parameter_info(param)
        # Print each line with indentation
        for line in info.split('\n'):
            print(f"  {line}")


def example_6_error_recovery():
    """Example 6: Error recovery and logging"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Error Recovery and Logging")
    print("=" * 60)
    
    recovery_manager = get_recovery_manager()
    
    # Simulate an error
    print("\n1. Simulating error...")
    from apgi_framework.exceptions import SimulationError
    test_error = SimulationError("Example simulation error")
    context = {
        'function': 'example_function',
        'parameters': {'n_trials': 100},
        'timestamp': 'now'
    }
    recovery_manager.log_error(test_error, context)
    print("✓ Error logged")
    
    # Get error statistics
    print("\n2. Error statistics:")
    stats = recovery_manager.get_error_statistics()
    print(f"   Total errors logged: {stats['total_errors']}")
    if stats['total_errors'] > 0:
        print(f"   Error types: {stats.get('error_types', {})}")
        print(f"   First error: {stats.get('first_error', 'N/A')}")
        print(f"   Last error: {stats.get('last_error', 'N/A')}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("APGI FRAMEWORK VALIDATION & ERROR HANDLING EXAMPLES")
    print("=" * 60)
    
    try:
        example_1_parameter_validation()
        example_2_system_health_check()
        example_3_safe_configuration()
        example_4_safe_test_execution()
        example_5_parameter_info()
        example_6_error_recovery()
        
        print("\n" + "=" * 60)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
