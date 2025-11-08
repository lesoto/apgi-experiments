"""
Test script for parameter validation functionality.

This script tests the parameter validation system to ensure it correctly
validates IPI parameters, experimental configuration, and provides helpful
error messages and warnings.
"""

from ipi_framework.validation import get_validator
from ipi_framework.config import IPIParameters, ExperimentalConfig, ConfigManager
from ipi_framework.exceptions import ConfigurationError

def test_ipi_parameter_validation():
    """Test IPI parameter validation."""
    print("=" * 60)
    print("Testing IPI Parameter Validation")
    print("=" * 60)
    
    validator = get_validator()
    
    # Test 1: Valid parameters
    print("\n1. Testing valid parameters:")
    result = validator.validate_ipi_parameters(
        extero_precision=2.0,
        intero_precision=1.5,
        extero_error=1.2,
        intero_error=0.8,
        somatic_gain=1.3,
        threshold=3.5,
        steepness=2.0
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())
    
    # Test 2: Invalid parameters (negative precision)
    print("\n2. Testing invalid parameters (negative precision):")
    result = validator.validate_ipi_parameters(
        extero_precision=-1.0,
        intero_precision=1.5,
        extero_error=1.2,
        intero_error=0.8,
        somatic_gain=1.3,
        threshold=3.5,
        steepness=2.0
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())
    
    # Test 3: Parameters with warnings (unusual values)
    print("\n3. Testing parameters with warnings (very low precision):")
    result = validator.validate_ipi_parameters(
        extero_precision=0.2,
        intero_precision=1.5,
        extero_error=1.2,
        intero_error=0.8,
        somatic_gain=1.3,
        threshold=3.5,
        steepness=2.0
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())
    
    # Test 4: Out of range values
    print("\n4. Testing out of range values (threshold too high):")
    result = validator.validate_ipi_parameters(
        extero_precision=2.0,
        intero_precision=1.5,
        extero_error=1.2,
        intero_error=0.8,
        somatic_gain=1.3,
        threshold=15.0,
        steepness=2.0
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())

def test_experimental_config_validation():
    """Test experimental configuration validation."""
    print("\n" + "=" * 60)
    print("Testing Experimental Configuration Validation")
    print("=" * 60)
    
    validator = get_validator()
    
    # Test 1: Valid configuration
    print("\n1. Testing valid configuration:")
    result = validator.validate_experimental_config(
        n_trials=1000,
        n_participants=100,
        alpha_level=0.05,
        effect_size_threshold=0.5,
        power_threshold=0.8
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())
    
    # Test 2: Low trial count (warning)
    print("\n2. Testing low trial count (should warn):")
    result = validator.validate_experimental_config(
        n_trials=30,
        n_participants=100,
        alpha_level=0.05,
        effect_size_threshold=0.5,
        power_threshold=0.8
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())
    
    # Test 3: Invalid alpha level
    print("\n3. Testing invalid alpha level:")
    result = validator.validate_experimental_config(
        n_trials=1000,
        n_participants=100,
        alpha_level=1.5,
        effect_size_threshold=0.5,
        power_threshold=0.8
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())

def test_neural_threshold_validation():
    """Test neural signature threshold validation."""
    print("\n" + "=" * 60)
    print("Testing Neural Signature Threshold Validation")
    print("=" * 60)
    
    validator = get_validator()
    
    # Test 1: Valid thresholds
    print("\n1. Testing valid thresholds:")
    result = validator.validate_neural_thresholds(
        p3b_threshold=5.0,
        gamma_plv_threshold=0.3,
        bold_z_threshold=3.1,
        pci_threshold=0.4
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())
    
    # Test 2: Low P3b threshold (suggestion)
    print("\n2. Testing low P3b threshold (should suggest):")
    result = validator.validate_neural_thresholds(
        p3b_threshold=2.5,
        gamma_plv_threshold=0.3,
        bold_z_threshold=3.1,
        pci_threshold=0.4
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())
    
    # Test 3: Invalid threshold (out of range)
    print("\n3. Testing invalid threshold (out of range):")
    result = validator.validate_neural_thresholds(
        p3b_threshold=25.0,
        gamma_plv_threshold=0.3,
        bold_z_threshold=3.1,
        pci_threshold=0.4
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())

def test_config_manager_validation():
    """Test ConfigManager automatic validation."""
    print("\n" + "=" * 60)
    print("Testing ConfigManager Automatic Validation")
    print("=" * 60)
    
    # Test 1: Valid IPIParameters
    print("\n1. Creating valid IPIParameters:")
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
        print("✓ IPIParameters created successfully")
    except ConfigurationError as e:
        print(f"✗ Failed to create IPIParameters: {e}")
    
    # Test 2: Invalid IPIParameters
    print("\n2. Creating invalid IPIParameters (negative precision):")
    try:
        params = IPIParameters(
            extero_precision=-1.0,
            intero_precision=1.5,
            extero_error=1.2,
            intero_error=0.8,
            somatic_gain=1.3,
            threshold=3.5,
            steepness=2.0
        )
        print("✗ IPIParameters created (should have failed)")
    except ConfigurationError as e:
        print(f"✓ Correctly rejected invalid parameters:\n{e}")
    
    # Test 3: Valid ExperimentalConfig
    print("\n3. Creating valid ExperimentalConfig:")
    try:
        config = ExperimentalConfig(
            n_trials=1000,
            n_participants=100,
            alpha_level=0.05,
            effect_size_threshold=0.5,
            power_threshold=0.8
        )
        print("✓ ExperimentalConfig created successfully")
    except ConfigurationError as e:
        print(f"✗ Failed to create ExperimentalConfig: {e}")
    
    # Test 4: Invalid ExperimentalConfig
    print("\n4. Creating invalid ExperimentalConfig (negative trials):")
    try:
        config = ExperimentalConfig(
            n_trials=-100,
            n_participants=100,
            alpha_level=0.05,
            effect_size_threshold=0.5,
            power_threshold=0.8
        )
        print("✗ ExperimentalConfig created (should have failed)")
    except ConfigurationError as e:
        print(f"✓ Correctly rejected invalid configuration:\n{e}")

def test_comprehensive_validation():
    """Test comprehensive validation of all parameters."""
    print("\n" + "=" * 60)
    print("Testing Comprehensive Validation")
    print("=" * 60)
    
    validator = get_validator()
    
    # Test with all parameter types
    print("\n1. Testing comprehensive validation with all valid parameters:")
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
    print(f"Valid: {result.is_valid}")
    print(result.get_message())
    
    # Test with mixed valid/invalid parameters
    print("\n2. Testing comprehensive validation with some invalid parameters:")
    result = validator.validate_all(
        ipi_params={
            'extero_precision': -1.0,  # Invalid
            'intero_precision': 1.5,
            'extero_error': 1.2,
            'intero_error': 0.8,
            'somatic_gain': 1.3,
            'threshold': 3.5,
            'steepness': 2.0
        },
        experimental_config={
            'n_trials': 30,  # Low (warning)
            'n_participants': 100,
            'alpha_level': 0.05,
            'effect_size_threshold': 0.5,
            'power_threshold': 0.8
        },
        neural_thresholds={
            'p3b_threshold': 25.0,  # Invalid
            'gamma_plv_threshold': 0.3,
            'bold_z_threshold': 3.1,
            'pci_threshold': 0.4
        }
    )
    print(f"Valid: {result.is_valid}")
    print(result.get_message())

def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("IPI Framework Parameter Validation Test Suite")
    print("=" * 60)
    
    test_ipi_parameter_validation()
    test_experimental_config_validation()
    test_neural_threshold_validation()
    test_config_manager_validation()
    test_comprehensive_validation()
    
    print("\n" + "=" * 60)
    print("All validation tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
