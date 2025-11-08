"""
Parameter Validation Example

This example demonstrates how to use the parameter validation system
in the IPI Framework, including:
- Validating individual parameters
- Validating complete configurations
- Handling validation errors and warnings
- Using validation in GUI applications
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ipi_framework.validation import get_validator
from ipi_framework.config import IPIParameters, ExperimentalConfig, ConfigManager
from ipi_framework.exceptions import ConfigurationError

def example_1_basic_validation():
    """Example 1: Basic parameter validation."""
    print("=" * 60)
    print("Example 1: Basic Parameter Validation")
    print("=" * 60)
    
    validator = get_validator()
    
    # Validate IPI parameters
    result = validator.validate_ipi_parameters(
        extero_precision=2.0,
        intero_precision=1.5,
        extero_error=1.2,
        intero_error=0.8,
        somatic_gain=1.3,
        threshold=3.5,
        steepness=2.0
    )
    
    print(f"\nValidation result: {'PASS' if result.is_valid else 'FAIL'}")
    print(result.get_message())

def example_2_handling_errors():
    """Example 2: Handling validation errors."""
    print("\n" + "=" * 60)
    print("Example 2: Handling Validation Errors")
    print("=" * 60)
    
    validator = get_validator()
    
    # Try to validate invalid parameters
    result = validator.validate_ipi_parameters(
        extero_precision=-1.0,  # Invalid: negative
        intero_precision=1.5,
        extero_error=1.2,
        intero_error=0.8,
        somatic_gain=1.3,
        threshold=3.5,
        steepness=2.0
    )
    
    if not result.is_valid:
        print("\n⚠️  Validation failed!")
        print("\nErrors found:")
        for error in result.errors:
            print(f"  • {error}")
        
        print("\nHow to fix:")
        print("  • Ensure extero_precision is positive (0.01-10.0)")
        print("  • Typical values are between 0.5 and 5.0")

def example_3_warnings_and_suggestions():
    """Example 3: Working with warnings and suggestions."""
    print("\n" + "=" * 60)
    print("Example 3: Warnings and Suggestions")
    print("=" * 60)
    
    validator = get_validator()
    
    # Validate with unusual but valid parameters
    result = validator.validate_experimental_config(
        n_trials=30,  # Low but valid
        n_participants=15,  # Low but valid
        alpha_level=0.05,
        effect_size_threshold=0.5,
        power_threshold=0.8
    )
    
    print(f"\nValidation result: {'PASS' if result.is_valid else 'FAIL'}")
    
    if result.warnings:
        print("\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"  • {warning}")
    
    if result.suggestions:
        print("\n💡 Suggestions:")
        for suggestion in result.suggestions:
            print(f"  • {suggestion}")

def example_4_config_manager_integration():
    """Example 4: Using validation with ConfigManager."""
    print("\n" + "=" * 60)
    print("Example 4: ConfigManager Integration")
    print("=" * 60)
    
    # ConfigManager automatically validates on creation
    print("\n1. Creating valid configuration:")
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
        print("   ✓ Configuration created successfully")
    except ConfigurationError as e:
        print(f"   ✗ Configuration rejected: {e}")
    
    # Try to create invalid configuration
    print("\n2. Attempting to create invalid configuration:")
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
        print("   ✗ Configuration created (should have failed!)")
    except ConfigurationError as e:
        print("   ✓ Configuration correctly rejected")
        print(f"\n   Reason: {str(e)[:100]}...")

def example_5_comprehensive_validation():
    """Example 5: Comprehensive validation of all parameters."""
    print("\n" + "=" * 60)
    print("Example 5: Comprehensive Validation")
    print("=" * 60)
    
    validator = get_validator()
    
    # Validate all parameter types at once
    result = validator.validate_all(
        ipi_params={
            'extero_precision': 2.0,
            'intero_precision': 1.5,
            'extero_error': 1.2,
            'intero_error': 0.8,
            'somatic_gain': 1.3,
            'threshold': 3.5,
            'steepness': 2.0
        },
        experimental_config={
            'n_trials': 1000,
            'n_participants': 100,
            'alpha_level': 0.05,
            'effect_size_threshold': 0.5,
            'power_threshold': 0.8
        },
        neural_thresholds={
            'p3b_threshold': 5.0,
            'gamma_plv_threshold': 0.3,
            'bold_z_threshold': 3.1,
            'pci_threshold': 0.4
        }
    )
    
    print(f"\nOverall validation: {'PASS' if result.is_valid else 'FAIL'}")
    
    if result.is_valid:
        print("\n✓ All parameters are valid and ready for use!")
    else:
        print("\n✗ Some parameters need attention:")
        print(result.get_message())

def example_6_parameter_info():
    """Example 6: Getting parameter information."""
    print("\n" + "=" * 60)
    print("Example 6: Parameter Information")
    print("=" * 60)
    
    validator = get_validator()
    
    # Get information about specific parameters
    params_to_check = ['extero_precision', 'threshold', 'n_trials', 'p3b_threshold']
    
    for param in params_to_check:
        print(f"\n{param}:")
        info = validator.get_parameter_info(param)
        print(f"  {info}")

def example_7_validation_history():
    """Example 7: Tracking validation history."""
    print("\n" + "=" * 60)
    print("Example 7: Validation History")
    print("=" * 60)
    
    validator = get_validator()
    
    # Perform several validations
    validator.validate_ipi_parameters(extero_precision=2.0, intero_precision=1.5,
                                     extero_error=1.2, intero_error=0.8,
                                     somatic_gain=1.3, threshold=3.5, steepness=2.0)
    
    validator.validate_experimental_config(n_trials=1000, n_participants=100,
                                          alpha_level=0.05)
    
    validator.validate_neural_thresholds(p3b_threshold=5.0, gamma_plv_threshold=0.3)
    
    # Get validation summary
    summary = validator.get_validation_summary()
    print(f"\n{summary}")

def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("IPI Framework Parameter Validation Examples")
    print("=" * 60)
    
    example_1_basic_validation()
    example_2_handling_errors()
    example_3_warnings_and_suggestions()
    example_4_config_manager_integration()
    example_5_comprehensive_validation()
    example_6_parameter_info()
    example_7_validation_history()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  • Always validate parameters before running experiments")
    print("  • Pay attention to warnings - they indicate unusual values")
    print("  • Use suggestions to optimize your parameter choices")
    print("  • ConfigManager provides automatic validation")
    print("  • Comprehensive validation checks all parameters at once")
    print("=" * 60)

if __name__ == "__main__":
    main()
