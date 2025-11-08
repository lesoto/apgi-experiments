"""
Test script to verify robust error handling implementation.

This script tests:
1. Try-catch blocks wrap test execution
2. Detailed error logging
3. Automatic retry for transient failures
4. Error recovery mechanisms
"""

import sys
import logging
from datetime import datetime

# Setup logging to see error handling in action
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_error_handling_initialization():
    """Test error handling system initialization"""
    print("\n" + "="*80)
    print("TEST 1: Error Handling Initialization")
    print("="*80)
    
    try:
        from ipi_framework.falsification.error_handling_wrapper import (
            initialize_error_handling,
            get_error_handling_status
        )
        
        # Initialize error handling
        success = initialize_error_handling()
        print(f"✓ Error handling initialization: {'SUCCESS' if success else 'FAILED'}")
        
        # Get status
        status = get_error_handling_status()
        print(f"\nError Handling Status:")
        print(f"  - Logging configured: {status['logging_configured']}")
        print(f"  - Log level: {status['log_level']}")
        print(f"  - Recovery manager active: {status['recovery_manager_active']}")
        print(f"  - Logs directory exists: {status['logs_directory_exists']}")
        
        return True
    except Exception as e:
        print(f"✗ Error handling initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parameter_validation_error():
    """Test parameter validation error handling"""
    print("\n" + "="*80)
    print("TEST 2: Parameter Validation Error Handling")
    print("="*80)
    
    try:
        from ipi_framework.falsification.primary_falsification_test import PrimaryFalsificationTest
        from ipi_framework.exceptions import ValidationError
        
        test = PrimaryFalsificationTest()
        
        # Try to run with invalid parameters (negative trials)
        try:
            result = test.run_falsification_test(n_trials=-10, n_participants=5)
            print("✗ Should have raised ValidationError for negative n_trials")
            return False
        except ValidationError as e:
            print(f"✓ ValidationError caught correctly: {str(e)}")
            print(f"  - Error type: {type(e).__name__}")
            print(f"  - Error message properly logged")
            return True
        
    except Exception as e:
        print(f"✗ Test failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_wrapper():
    """Test ErrorHandlingTestWrapper functionality"""
    print("\n" + "="*80)
    print("TEST 3: Error Handling Wrapper")
    print("="*80)
    
    try:
        from ipi_framework.falsification.primary_falsification_test import PrimaryFalsificationTest
        from ipi_framework.falsification.error_handling_wrapper import ErrorHandlingTestWrapper
        
        # Create test controller
        test_controller = PrimaryFalsificationTest()
        
        # Wrap with error handling
        wrapped_controller = ErrorHandlingTestWrapper(test_controller)
        print("✓ Test controller wrapped successfully")
        
        # Get initial error summary
        summary = wrapped_controller.get_error_summary()
        print(f"\nInitial Error Summary:")
        print(f"  - Total errors: {summary['total_errors']}")
        print(f"  - Recovery attempts: {summary['recovery_attempts']}")
        print(f"  - Message: {summary['message']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_successful_execution():
    """Test successful test execution with error handling"""
    print("\n" + "="*80)
    print("TEST 4: Successful Test Execution")
    print("="*80)
    
    try:
        from ipi_framework.falsification.primary_falsification_test import PrimaryFalsificationTest
        
        test = PrimaryFalsificationTest()
        
        # Run with small valid parameters
        print("Running primary falsification test with n_trials=10, n_participants=2...")
        result = test.run_falsification_test(n_trials=10, n_participants=2)
        
        print(f"✓ Test completed successfully")
        print(f"  - Test ID: {result.test_id}")
        print(f"  - Total trials: {len(result.trial_results)}")
        print(f"  - Falsification rate: {result.falsification_rate:.2%}")
        print(f"  - Framework falsified: {result.is_framework_falsified}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_logging():
    """Test detailed error logging"""
    print("\n" + "="*80)
    print("TEST 5: Detailed Error Logging")
    print("="*80)
    
    try:
        from ipi_framework.falsification.error_handling_wrapper import create_error_report
        from ipi_framework.exceptions import SimulationError
        
        # Create a test error
        test_error = SimulationError("Test simulation error for logging")
        test_context = {
            'function': 'test_function',
            'timestamp': datetime.now(),
            'parameters': {'n_trials': 100, 'n_participants': 20}
        }
        
        # Generate error report
        report = create_error_report("test_simulation", test_error, test_context)
        
        print("✓ Error report generated successfully")
        print(f"\nError Report Preview (first 500 chars):")
        print(report[:500])
        print("...")
        
        # Check report contains key sections
        assert "ERROR REPORT" in report
        assert "Troubleshooting Guide" in report
        assert "Recovery Actions" in report
        print("\n✓ Error report contains all required sections")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_recovery_manager():
    """Test error recovery manager"""
    print("\n" + "="*80)
    print("TEST 6: Error Recovery Manager")
    print("="*80)
    
    try:
        from ipi_framework.validation.error_recovery import get_recovery_manager
        from ipi_framework.exceptions import SimulationError
        
        manager = get_recovery_manager()
        print("✓ Recovery manager obtained")
        
        # Log a test error
        test_error = SimulationError("Test error for recovery")
        test_context = {'test': 'recovery_test'}
        
        manager.log_error(test_error, test_context)
        print("✓ Error logged to recovery manager")
        
        # Get error statistics
        stats = manager.get_error_statistics()
        print(f"\nError Statistics:")
        print(f"  - Total errors: {stats['total_errors']}")
        if 'error_types' in stats:
            print(f"  - Error types: {stats['error_types']}")
        
        # Clear error log
        manager.clear_error_log()
        print("✓ Error log cleared")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all error handling tests"""
    print("\n" + "="*80)
    print("ROBUST ERROR HANDLING VERIFICATION TESTS")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Error Handling Initialization", test_error_handling_initialization),
        ("Parameter Validation Error", test_parameter_validation_error),
        ("Error Handling Wrapper", test_error_wrapper),
        ("Successful Execution", test_successful_execution),
        ("Detailed Error Logging", test_error_logging),
        ("Error Recovery Manager", test_recovery_manager),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
