"""
Example 1: Running Primary Falsification Test from CLI

This example demonstrates how to run the primary falsification test,
which tests whether full ignition signatures can occur without consciousness.

The primary falsification criterion is the most decisive test of the IPI Framework:
if we observe all neural signatures of ignition (P3b, gamma synchrony, BOLD activation,
PCI) without any evidence of consciousness, the framework would be falsified.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ipi_framework.main_controller import MainApplicationController
from ipi_framework.config import ConfigManager
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_primary_falsification_test_basic():
    """
    Basic example: Run primary falsification test with default parameters.
    """
    logger.info("="*60)
    logger.info("Example 1A: Basic Primary Falsification Test")
    logger.info("="*60)
    
    try:
        # Initialize the system
        controller = MainApplicationController()
        controller.initialize_system()
        
        # Get the falsification tests
        tests = controller.get_falsification_tests()
        primary_test = tests['primary']
        
        # Run the test with default parameters (1000 trials)
        logger.info("Running primary falsification test with 1000 trials...")
        result = primary_test.run_test(n_trials=1000)
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("RESULTS")
        logger.info("="*60)
        logger.info(f"Falsification Status: {'FALSIFIED' if result.is_falsified else 'NOT FALSIFIED'}")
        logger.info(f"Confidence Level: {result.confidence_level:.3f}")
        logger.info(f"Effect Size: {result.effect_size:.3f}")
        logger.info(f"P-value: {result.p_value:.6f}")
        logger.info(f"Statistical Power: {result.statistical_power:.3f}")
        logger.info("="*60 + "\n")
        
        # Cleanup
        controller.shutdown_system()
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


def run_primary_falsification_test_custom():
    """
    Advanced example: Run primary falsification test with custom parameters.
    """
    logger.info("="*60)
    logger.info("Example 1B: Custom Primary Falsification Test")
    logger.info("="*60)
    
    try:
        # Initialize with custom configuration
        controller = MainApplicationController()
        controller.initialize_system()
        
        # Update IPI parameters for a specific scenario
        # Example: Testing with higher interoceptive precision
        controller.config_manager.update_ipi_parameters(
            extero_precision=2.5,
            intero_precision=2.0,  # Higher than default
            threshold=3.0,  # Lower threshold
            steepness=2.5,  # Steeper sigmoid
            somatic_gain=1.5
        )
        
        # Update experimental configuration
        controller.config_manager.update_experimental_config(
            n_trials=2000,  # More trials for better statistical power
            random_seed=42,  # For reproducibility
            output_directory="results/custom_primary_test"
        )
        
        # Get the falsification tests
        tests = controller.get_falsification_tests()
        primary_test = tests['primary']
        
        # Run the test
        logger.info("Running primary falsification test with custom parameters...")
        logger.info(f"  - Trials: 2000")
        logger.info(f"  - Interoceptive Precision: 2.0")
        logger.info(f"  - Threshold: 3.0")
        logger.info(f"  - Random Seed: 42")
        
        result = primary_test.run_test(n_trials=2000)
        
        # Display detailed results
        logger.info("\n" + "="*60)
        logger.info("DETAILED RESULTS")
        logger.info("="*60)
        logger.info(f"Test Type: {result.test_type}")
        logger.info(f"Falsification Status: {'FALSIFIED' if result.is_falsified else 'NOT FALSIFIED'}")
        logger.info(f"Confidence Level: {result.confidence_level:.3f}")
        logger.info(f"Effect Size (Cohen's d): {result.effect_size:.3f}")
        logger.info(f"P-value: {result.p_value:.6f}")
        logger.info(f"Statistical Power: {result.statistical_power:.3f}")
        logger.info(f"Replication Count: {result.replication_count}")
        
        # Display interpretation
        logger.info("\nINTERPRETATION:")
        if result.is_falsified:
            logger.info("  ⚠️  The IPI Framework has been FALSIFIED!")
            logger.info("  Full ignition signatures were observed without consciousness.")
        else:
            logger.info("  ✓ The IPI Framework passed this falsification test.")
            logger.info("  No instances of full ignition without consciousness were found.")
        
        logger.info("="*60 + "\n")
        
        # Cleanup
        controller.shutdown_system()
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


def run_primary_falsification_test_with_validation():
    """
    Example with system validation: Validate system before running test.
    """
    logger.info("="*60)
    logger.info("Example 1C: Primary Test with System Validation")
    logger.info("="*60)
    
    try:
        # Initialize the system
        controller = MainApplicationController()
        controller.initialize_system()
        
        # Run system validation first
        logger.info("Running system validation...")
        validation_results = controller.run_system_validation()
        
        logger.info("\nValidation Results:")
        for component, status in validation_results.items():
            if component != 'overall':
                status_str = "✓ PASS" if status else "✗ FAIL"
                logger.info(f"  {component.replace('_', ' ').title()}: {status_str}")
        
        overall_status = "✓ PASS" if validation_results.get('overall', False) else "✗ FAIL"
        logger.info(f"\nOverall System Status: {overall_status}\n")
        
        if not validation_results.get('overall', False):
            logger.error("System validation failed. Cannot proceed with test.")
            return None
        
        # System is valid, proceed with test
        tests = controller.get_falsification_tests()
        primary_test = tests['primary']
        
        logger.info("Running primary falsification test...")
        result = primary_test.run_test(n_trials=1000)
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("RESULTS")
        logger.info("="*60)
        logger.info(f"Falsification Status: {'FALSIFIED' if result.is_falsified else 'NOT FALSIFIED'}")
        logger.info(f"Confidence Level: {result.confidence_level:.3f}")
        logger.info(f"P-value: {result.p_value:.6f}")
        logger.info("="*60 + "\n")
        
        # Cleanup
        controller.shutdown_system()
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == '__main__':
    print("\n" + "="*70)
    print("IPI Framework - Primary Falsification Test Examples")
    print("="*70 + "\n")
    
    # Run all examples
    print("Running Example 1A: Basic Test...")
    result_basic = run_primary_falsification_test_basic()
    
    print("\n" + "-"*70 + "\n")
    
    print("Running Example 1B: Custom Parameters...")
    result_custom = run_primary_falsification_test_custom()
    
    print("\n" + "-"*70 + "\n")
    
    print("Running Example 1C: With System Validation...")
    result_validated = run_primary_falsification_test_with_validation()
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70 + "\n")
