"""
Error Handling Wrapper for Falsification Tests

Provides robust error handling, logging, and recovery for all falsification test controllers.
Implements comprehensive try-catch blocks, detailed error logging, automatic retry for transient
failures, and error recovery mechanisms.
"""

from typing import Callable, Any, Optional, Dict, List
from functools import wraps
import logging
from datetime import datetime
import traceback
import sys
import os

from ..exceptions import (
    IPIFrameworkError, ValidationError, SimulationError,
    StatisticalError, ConfigurationError
)
from ..validation.error_recovery import (
    with_retry, RetryConfig, get_recovery_manager, safe_execute
)
from ..validation.parameter_validator import get_validator


# Configure detailed logging with file handler
def setup_detailed_logging():
    """Setup detailed logging with both console and file handlers"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler for INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler for DEBUG and above (detailed logging)
    try:
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'falsification_tests_{datetime.now().strftime("%Y%m%d")}.log')
        
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.debug(f"Detailed logging initialized. Log file: {log_file}")
    except Exception as e:
        logger.warning(f"Could not setup file logging: {e}")
    
    return logger

logger = setup_detailed_logging()


def with_error_handling(validate_params: bool = True, 
                       enable_retry: bool = True,
                       log_errors: bool = True,
                       max_retries: int = 3):
    """
    Decorator that adds comprehensive error handling to test methods.
    
    Implements:
    - Try-catch blocks for all exception types
    - Detailed error logging with context information
    - Automatic retry for transient failures
    - Error recovery mechanisms
    - Troubleshooting guidance
    
    Args:
        validate_params: Whether to validate parameters before execution
        enable_retry: Whether to enable automatic retry on transient failures
        log_errors: Whether to log errors
        max_retries: Maximum number of retry attempts for transient failures
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get function name and context
            func_name = func.__name__
            start_time = datetime.now()
            context = {
                'function': func_name,
                'module': func.__module__,
                'timestamp': start_time,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys()),
                'kwargs_values': {k: v for k, v in kwargs.items() if not callable(v)}
            }
            
            # Log function entry
            logger.debug(f"Entering {func_name} with context: {context}")
            
            try:
                # Parameter validation with detailed error reporting
                if validate_params and kwargs:
                    try:
                        logger.debug(f"Validating parameters for {func_name}")
                        _validate_test_parameters(func_name, kwargs)
                        logger.debug(f"Parameter validation successful for {func_name}")
                    except ValidationError as e:
                        if log_errors:
                            logger.error(f"Parameter validation failed for {func_name}: {str(e)}")
                            logger.error(f"Invalid parameters: {kwargs}")
                            logger.error(f"Troubleshooting: Check parameter ranges and types")
                        raise
                
                # Execute function with retry if enabled
                if enable_retry:
                    logger.debug(f"Executing {func_name} with retry enabled (max_retries={max_retries})")
                    retry_config = RetryConfig(
                        max_attempts=max_retries,
                        initial_delay=1.0,
                        backoff_factor=2.0,
                        max_delay=10.0,
                        retriable_exceptions=[SimulationError, IOError, OSError, RuntimeError]
                    )
                    decorated_func = with_retry(retry_config)(func)
                    result = decorated_func(*args, **kwargs)
                else:
                    logger.debug(f"Executing {func_name} without retry")
                    result = func(*args, **kwargs)
                
                # Log successful execution
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(f"{func_name} completed successfully in {duration:.2f}s")
                logger.debug(f"Result type: {type(result).__name__}")
                
                return result
            
            except ValidationError as e:
                # Validation errors should not be retried
                if log_errors:
                    logger.error(f"Validation error in {func_name}: {str(e)}")
                    logger.error(f"Context: {context}")
                    logger.error(f"Troubleshooting:")
                    logger.error(f"  - Check parameter values are within valid ranges")
                    logger.error(f"  - Verify parameter types match expected types")
                    logger.error(f"  - Review parameter documentation")
                    
                    # Create detailed error report
                    error_report = create_error_report(func_name, e, context)
                    logger.debug(f"Detailed error report:\n{error_report}")
                
                # Log to recovery manager
                recovery_manager = get_recovery_manager()
                recovery_manager.log_error(e, context)
                raise
            
            except ConfigurationError as e:
                # Configuration errors should not be retried
                if log_errors:
                    logger.error(f"Configuration error in {func_name}: {str(e)}")
                    logger.error(f"Context: {context}")
                    logger.error(f"Troubleshooting:")
                    logger.error(f"  - Verify configuration file exists and is valid")
                    logger.error(f"  - Check for missing required configuration parameters")
                    logger.error(f"  - Ensure configuration values are properly formatted")
                    
                    error_report = create_error_report(func_name, e, context)
                    logger.debug(f"Detailed error report:\n{error_report}")
                
                recovery_manager = get_recovery_manager()
                recovery_manager.log_error(e, context)
                raise
            
            except SimulationError as e:
                # Simulation errors - attempt recovery
                if log_errors:
                    logger.error(f"Simulation error in {func_name}: {str(e)}")
                    logger.error(f"Context: {context}")
                    logger.error(f"Troubleshooting:")
                    logger.error(f"  - Try running with a different random seed")
                    logger.error(f"  - Check simulation parameters are reasonable")
                    logger.error(f"  - Verify input data is not corrupted")
                    
                    error_report = create_error_report(func_name, e, context)
                    logger.debug(f"Detailed error report:\n{error_report}")
                
                recovery_manager = get_recovery_manager()
                recovery_manager.log_error(e, context)
                
                # Attempt automatic recovery
                logger.info(f"Attempting automatic recovery for simulation error in {func_name}")
                recovery_result = recovery_manager.attempt_recovery(e, context)
                if recovery_result is not None:
                    logger.info(f"Recovery successful for {func_name}")
                    return recovery_result
                
                logger.error(f"Recovery failed for {func_name}, re-raising exception")
                raise
            
            except StatisticalError as e:
                # Statistical errors - log and raise
                if log_errors:
                    logger.error(f"Statistical error in {func_name}: {str(e)}")
                    logger.error(f"Context: {context}")
                    logger.error(f"Troubleshooting:")
                    logger.error(f"  - Verify sample size is sufficient")
                    logger.error(f"  - Check for numerical stability issues")
                    logger.error(f"  - Ensure data distributions are appropriate")
                    
                    error_report = create_error_report(func_name, e, context)
                    logger.debug(f"Detailed error report:\n{error_report}")
                
                recovery_manager = get_recovery_manager()
                recovery_manager.log_error(e, context)
                raise
            
            except MemoryError as e:
                # Memory errors - special handling
                if log_errors:
                    logger.critical(f"Memory error in {func_name}: {str(e)}")
                    logger.critical(f"Context: {context}")
                    logger.critical(f"Troubleshooting:")
                    logger.critical(f"  - Reduce batch size or number of trials")
                    logger.critical(f"  - Close other applications to free memory")
                    logger.critical(f"  - Consider processing data in chunks")
                    
                    error_report = create_error_report(func_name, e, context)
                    logger.debug(f"Detailed error report:\n{error_report}")
                
                recovery_manager = get_recovery_manager()
                recovery_manager.log_error(e, context)
                raise IPIFrameworkError(f"Memory error in {func_name}: Insufficient memory. Try reducing data size.") from e
            
            except KeyboardInterrupt:
                # User interruption - clean exit
                logger.warning(f"User interrupted {func_name}")
                logger.info(f"Cleaning up after interruption...")
                raise
            
            except IPIFrameworkError as e:
                # General framework errors
                if log_errors:
                    logger.error(f"Framework error in {func_name}: {str(e)}")
                    logger.error(f"Context: {context}")
                    logger.error(f"Troubleshooting:")
                    logger.error(f"  - Check system health with diagnostics")
                    logger.error(f"  - Review error log for patterns")
                    logger.error(f"  - Verify all dependencies are installed")
                    
                    error_report = create_error_report(func_name, e, context)
                    logger.debug(f"Detailed error report:\n{error_report}")
                
                recovery_manager = get_recovery_manager()
                recovery_manager.log_error(e, context)
                raise
            
            except Exception as e:
                # Unexpected errors - comprehensive logging
                if log_errors:
                    logger.critical(f"Unexpected error in {func_name}: {str(e)}")
                    logger.critical(f"Error type: {type(e).__name__}")
                    logger.critical(f"Error args: {e.args}")
                    logger.critical(f"Traceback:\n{traceback.format_exc()}")
                    logger.critical(f"Context: {context}")
                    logger.critical(f"System info: Python {sys.version}")
                    logger.critical(f"Troubleshooting:")
                    logger.critical(f"  - This is an unexpected error type")
                    logger.critical(f"  - Check the full traceback above")
                    logger.critical(f"  - Report this error if it persists")
                    
                    error_report = create_error_report(func_name, e, context)
                    logger.debug(f"Detailed error report:\n{error_report}")
                
                recovery_manager = get_recovery_manager()
                recovery_manager.log_error(e, context)
                
                # Wrap in framework error with full context
                wrapped_error = IPIFrameworkError(
                    f"Unexpected error in {func_name}: {type(e).__name__}: {str(e)}"
                )
                raise wrapped_error from e
            
            finally:
                # Always log function exit
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.debug(f"Exiting {func_name} after {duration:.2f}s")
        
        return wrapper
    return decorator


def _validate_test_parameters(func_name: str, params: Dict[str, Any]):
    """
    Validate test parameters based on function name.
    
    Args:
        func_name: Name of the function being called
        params: Parameters to validate
        
    Raises:
        ValidationError: If parameters are invalid
    """
    validator = get_validator()
    
    # Validate common parameters
    if 'n_trials' in params:
        n_trials = params['n_trials']
        if not isinstance(n_trials, int) or n_trials <= 0:
            raise ValidationError(f"n_trials must be a positive integer, got {n_trials}")
        if n_trials > 10000:
            logger.warning(f"Large n_trials ({n_trials}) may be slow")
    
    if 'n_participants' in params:
        n_participants = params['n_participants']
        if not isinstance(n_participants, int) or n_participants <= 0:
            raise ValidationError(f"n_participants must be a positive integer, got {n_participants}")
        if n_participants > 1000:
            logger.warning(f"Large n_participants ({n_participants}) may be slow")
    
    # Function-specific validation
    if 'soma_bias' in func_name.lower():
        if 'n_participants' in params and params['n_participants'] < 100:
            raise ValidationError(
                f"Soma-bias test requires n_participants >= 100, got {params['n_participants']}"
            )
    
    if 'threshold_insensitivity' in func_name.lower():
        if 'drug_conditions' in params:
            valid_drugs = ['propranolol', 'l_dopa', 'ssri', 'physostigmine', 'placebo']
            for drug in params['drug_conditions']:
                drug_name = drug.value if hasattr(drug, 'value') else str(drug)
                if drug_name.lower() not in valid_drugs:
                    raise ValidationError(f"Invalid drug type: {drug_name}")


class ErrorHandlingTestWrapper:
    """
    Wrapper class that adds comprehensive error handling to test controller instances.
    
    Features:
    - Automatic error logging and tracking
    - Error recovery attempts
    - Detailed error statistics
    - Retry mechanism for transient failures
    """
    
    def __init__(self, test_controller: Any):
        """
        Initialize wrapper with test controller.
        
        Args:
            test_controller: Test controller instance to wrap
        """
        self.test_controller = test_controller
        self.error_log: List[Dict[str, Any]] = []
        self.recovery_attempts: int = 0
        self.successful_recoveries: int = 0
        self.failed_recoveries: int = 0
        
        logger.info(f"Initialized ErrorHandlingTestWrapper for {type(test_controller).__name__}")
    
    def __getattr__(self, name: str) -> Any:
        """
        Wrap method calls with error handling.
        
        Args:
            name: Method name
            
        Returns:
            Wrapped method with error handling
        """
        attr = getattr(self.test_controller, name)
        
        if callable(attr) and name.startswith('run_'):
            # Wrap test execution methods with comprehensive error handling
            @with_error_handling(validate_params=True, enable_retry=True, log_errors=True, max_retries=3)
            def wrapped_method(*args, **kwargs):
                method_start_time = datetime.now()
                attempt_count = 0
                max_attempts = 3
                
                while attempt_count < max_attempts:
                    try:
                        attempt_count += 1
                        logger.info(f"Executing {name} (attempt {attempt_count}/{max_attempts})")
                        
                        result = attr(*args, **kwargs)
                        
                        # Log successful execution
                        execution_time = (datetime.now() - method_start_time).total_seconds()
                        logger.info(f"{name} completed successfully in {execution_time:.2f}s")
                        
                        return result
                        
                    except Exception as e:
                        # Log error with full context
                        error_entry = {
                            'method': name,
                            'timestamp': datetime.now(),
                            'error': str(e),
                            'error_type': type(e).__name__,
                            'attempt': attempt_count,
                            'args': args,
                            'kwargs': {k: v for k, v in kwargs.items() if not callable(v)},
                            'traceback': traceback.format_exc()
                        }
                        self.error_log.append(error_entry)
                        
                        logger.error(f"Error in {name} (attempt {attempt_count}/{max_attempts}): {str(e)}")
                        
                        # Determine if error is transient and should be retried
                        if attempt_count < max_attempts:
                            is_transient = handle_transient_failure(e, error_entry, attempt_count, max_attempts)
                            
                            if is_transient:
                                logger.info(f"Transient failure detected, attempting recovery...")
                                self.recovery_attempts += 1
                                
                                # Attempt recovery
                                recovery_result = recover_from_error(e, error_entry)
                                
                                if recovery_result is not None:
                                    self.successful_recoveries += 1
                                    logger.info(f"Recovery successful, returning result")
                                    return recovery_result
                                else:
                                    # Recovery signaled retry
                                    logger.info(f"Recovery initiated, retrying...")
                                    import time
                                    time.sleep(1.0 * attempt_count)  # Exponential backoff
                                    continue
                        
                        # If we get here, either not transient or max attempts reached
                        self.failed_recoveries += 1
                        logger.error(f"All recovery attempts failed for {name}")
                        raise
                
                # Should not reach here, but just in case
                raise IPIFrameworkError(f"Max attempts ({max_attempts}) exceeded for {name}")
            
            return wrapped_method
        
        return attr
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of errors encountered.
        
        Returns:
            Dictionary with error statistics and details
        """
        if not self.error_log:
            return {
                'total_errors': 0,
                'message': 'No errors encountered',
                'recovery_attempts': self.recovery_attempts,
                'successful_recoveries': self.successful_recoveries,
                'failed_recoveries': self.failed_recoveries
            }
        
        # Analyze error types
        error_types = {}
        error_methods = {}
        for entry in self.error_log:
            error_type = entry['error_type']
            method = entry['method']
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
            error_methods[method] = error_methods.get(method, 0) + 1
        
        # Calculate error rate
        total_errors = len(self.error_log)
        recovery_success_rate = (self.successful_recoveries / self.recovery_attempts * 100 
                                if self.recovery_attempts > 0 else 0)
        
        return {
            'total_errors': total_errors,
            'error_types': error_types,
            'error_methods': error_methods,
            'first_error': self.error_log[0]['timestamp'],
            'last_error': self.error_log[-1]['timestamp'],
            'recent_errors': self.error_log[-5:],  # Last 5 errors
            'recovery_attempts': self.recovery_attempts,
            'successful_recoveries': self.successful_recoveries,
            'failed_recoveries': self.failed_recoveries,
            'recovery_success_rate': f"{recovery_success_rate:.1f}%",
            'most_common_error': max(error_types.items(), key=lambda x: x[1])[0] if error_types else None,
            'most_problematic_method': max(error_methods.items(), key=lambda x: x[1])[0] if error_methods else None
        }
    
    def get_detailed_error_log(self) -> List[Dict[str, Any]]:
        """
        Get detailed error log with all recorded errors.
        
        Returns:
            List of error entries with full details
        """
        return self.error_log.copy()
    
    def clear_error_log(self):
        """Clear error log and reset statistics"""
        self.error_log.clear()
        self.recovery_attempts = 0
        self.successful_recoveries = 0
        self.failed_recoveries = 0
        logger.info("Error log cleared and statistics reset")
    
    def export_error_log(self, filepath: str):
        """
        Export error log to file for analysis.
        
        Args:
            filepath: Path to export file (JSON format)
        """
        import json
        
        try:
            export_data = {
                'summary': self.get_error_summary(),
                'errors': self.error_log
            }
            
            # Convert datetime objects to strings
            def datetime_converter(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=datetime_converter)
            
            logger.info(f"Error log exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export error log: {e}")


def create_safe_test_controller(controller_class: type, *args, **kwargs) -> ErrorHandlingTestWrapper:
    """
    Create a test controller instance with comprehensive error handling.
    
    Args:
        controller_class: Test controller class
        *args: Arguments for controller initialization
        **kwargs: Keyword arguments for controller initialization
        
    Returns:
        Wrapped test controller with error handling
        
    Raises:
        ConfigurationError: If controller cannot be initialized
    """
    try:
        logger.info(f"Creating test controller: {controller_class.__name__}")
        logger.debug(f"Controller args: {args}")
        logger.debug(f"Controller kwargs: {kwargs}")
        
        controller = controller_class(*args, **kwargs)
        wrapped_controller = ErrorHandlingTestWrapper(controller)
        
        logger.info(f"Successfully created and wrapped {controller_class.__name__}")
        return wrapped_controller
        
    except Exception as e:
        logger.error(f"Failed to create test controller {controller_class.__name__}: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        
        # Create detailed error report
        context = {
            'controller_class': controller_class.__name__,
            'args': args,
            'kwargs': kwargs
        }
        error_report = create_error_report(f"create_{controller_class.__name__}", e, context)
        logger.debug(f"Error report:\n{error_report}")
        
        raise ConfigurationError(f"Cannot initialize test controller {controller_class.__name__}: {str(e)}") from e


def initialize_error_handling():
    """
    Initialize error handling system with default configurations.
    
    This should be called at application startup to ensure proper error handling.
    """
    logger.info("Initializing error handling system...")
    
    try:
        # Initialize recovery manager with default strategies
        from ..validation.error_recovery import initialize_default_recovery_strategies
        initialize_default_recovery_strategies()
        logger.info("Default recovery strategies initialized")
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        logger.info("Logs directory verified")
        
        # Log system information
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {sys.platform}")
        
        logger.info("Error handling system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize error handling system: {e}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return False


def get_error_handling_status() -> Dict[str, Any]:
    """
    Get status of error handling system.
    
    Returns:
        Dictionary with error handling system status
    """
    recovery_manager = get_recovery_manager()
    error_stats = recovery_manager.get_error_statistics()
    
    return {
        'logging_configured': len(logger.handlers) > 0,
        'log_level': logging.getLevelName(logger.level),
        'recovery_manager_active': recovery_manager is not None,
        'total_errors_logged': error_stats.get('total_errors', 0),
        'error_types': error_stats.get('error_types', {}),
        'logs_directory_exists': os.path.exists('logs'),
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform
        }
    }


def log_test_execution(test_name: str, 
                      start_time: datetime,
                      end_time: datetime,
                      success: bool,
                      error: Optional[Exception] = None,
                      additional_info: Optional[Dict[str, Any]] = None):
    """
    Log comprehensive test execution details.
    
    Args:
        test_name: Name of the test
        start_time: Test start time
        end_time: Test end time
        success: Whether test succeeded
        error: Exception if test failed
        additional_info: Additional information to log
    """
    duration = (end_time - start_time).total_seconds()
    
    # Create execution log entry
    log_entry = {
        'test_name': test_name,
        'start_time': start_time,
        'end_time': end_time,
        'duration_seconds': duration,
        'success': success
    }
    
    if additional_info:
        log_entry.update(additional_info)
    
    if success:
        logger.info(f"✓ Test '{test_name}' completed successfully in {duration:.2f}s")
        logger.debug(f"Execution details: {log_entry}")
    else:
        logger.error(f"✗ Test '{test_name}' failed after {duration:.2f}s")
        if error:
            logger.error(f"Error type: {type(error).__name__}")
            logger.error(f"Error message: {str(error)}")
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            
            # Add error details to log entry
            log_entry['error_type'] = type(error).__name__
            log_entry['error_message'] = str(error)
            log_entry['traceback'] = traceback.format_exc()
        
        logger.debug(f"Execution details: {log_entry}")
        
        # Log to recovery manager
        recovery_manager = get_recovery_manager()
        recovery_manager.log_error(error if error else Exception("Test failed"), log_entry)


def create_error_report(test_name: str, 
                       error: Exception,
                       context: Dict[str, Any]) -> str:
    """
    Create detailed error report with comprehensive troubleshooting guidance.
    
    Args:
        test_name: Name of the test
        error: Exception that occurred
        context: Context information
        
    Returns:
        Formatted error report with troubleshooting steps
    """
    report_lines = [
        "=" * 80,
        f"ERROR REPORT: {test_name}",
        "=" * 80,
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Error Type: {type(error).__name__}",
        f"Error Message: {str(error)}",
        "",
        "Context Information:",
    ]
    
    for key, value in context.items():
        # Format value for readability
        if isinstance(value, dict):
            report_lines.append(f"  {key}:")
            for k, v in value.items():
                report_lines.append(f"    {k}: {v}")
        else:
            report_lines.append(f"  {key}: {value}")
    
    report_lines.extend([
        "",
        "Full Traceback:",
        "-" * 80,
        traceback.format_exc(),
        "-" * 80,
        "",
        "Troubleshooting Guide:",
    ])
    
    # Add detailed suggestions based on error type
    if isinstance(error, ValidationError):
        report_lines.extend([
            "  Parameter Validation Error:",
            "  1. Check that all parameter values are within valid ranges",
            "  2. Verify parameter types match expected types (int, float, etc.)",
            "  3. Review parameter documentation for requirements",
            "  4. Common issues:",
            "     - Negative values for counts (n_trials, n_participants)",
            "     - Sample size too small (soma-bias requires n >= 100)",
            "     - Invalid drug types for threshold insensitivity test",
            "  5. Use parameter validator to check values before running tests"
        ])
    elif isinstance(error, ConfigurationError):
        report_lines.extend([
            "  Configuration Error:",
            "  1. Verify configuration file exists and is readable",
            "  2. Check JSON/YAML syntax is valid",
            "  3. Ensure all required configuration parameters are present",
            "  4. Verify configuration values are properly formatted",
            "  5. Check file permissions if configuration cannot be loaded",
            "  6. Try resetting to default configuration"
        ])
    elif isinstance(error, SimulationError):
        report_lines.extend([
            "  Simulation Error:",
            "  1. Try running with a different random seed",
            "  2. Check simulation parameters are within reasonable ranges",
            "  3. Verify input data is not corrupted or missing",
            "  4. Reduce complexity if simulation is too demanding",
            "  5. Check for numerical instability (very large/small values)",
            "  6. Ensure sufficient system resources (memory, CPU)",
            "  7. Review simulator configuration and thresholds"
        ])
    elif isinstance(error, StatisticalError):
        report_lines.extend([
            "  Statistical Analysis Error:",
            "  1. Verify sample size is sufficient for analysis",
            "  2. Check for numerical stability issues (division by zero, etc.)",
            "  3. Ensure data distributions are appropriate",
            "  4. Look for outliers or invalid data points",
            "  5. Verify statistical assumptions are met",
            "  6. Try using alternative statistical methods",
            "  7. Check for missing or NaN values in data"
        ])
    elif isinstance(error, MemoryError):
        report_lines.extend([
            "  Memory Error:",
            "  1. Reduce batch size or number of trials",
            "  2. Close other applications to free memory",
            "  3. Process data in smaller chunks",
            "  4. Consider using a machine with more RAM",
            "  5. Check for memory leaks in long-running processes",
            "  6. Use memory profiling tools to identify issues"
        ])
    elif isinstance(error, (IOError, OSError)):
        report_lines.extend([
            "  I/O Error:",
            "  1. Check file paths are correct and accessible",
            "  2. Verify file permissions allow read/write",
            "  3. Ensure sufficient disk space is available",
            "  4. Check network connectivity if accessing remote files",
            "  5. Verify files are not locked by other processes",
            "  6. Try using absolute paths instead of relative paths"
        ])
    else:
        report_lines.extend([
            "  Unexpected Error:",
            "  1. Check system health with diagnostics tool",
            "  2. Review error log for patterns or related errors",
            "  3. Verify all dependencies are installed correctly",
            "  4. Try restarting the application",
            "  5. Check for system resource constraints",
            "  6. Report this error if it persists",
            "  7. Include this error report when seeking help"
        ])
    
    report_lines.extend([
        "",
        "Recovery Actions:",
    ])
    
    # Add recovery action suggestions
    recovery_manager = get_recovery_manager()
    error_stats = recovery_manager.get_error_statistics()
    
    if error_stats.get('total_errors', 0) > 0:
        report_lines.append(f"  - Total errors logged: {error_stats['total_errors']}")
        if 'error_types' in error_stats:
            report_lines.append("  - Error type distribution:")
            for err_type, count in error_stats['error_types'].items():
                report_lines.append(f"    {err_type}: {count}")
    
    report_lines.extend([
        "  - Check logs directory for detailed error history",
        "  - Use system health checker to diagnose issues",
        "  - Review recent changes that may have caused the error",
        "",
        "For Additional Help:",
        "  - Consult documentation at docs/",
        "  - Check examples/ directory for working code",
        "  - Review test files for proper usage patterns",
        "=" * 80
    ])
    
    return "\n".join(report_lines)


def handle_transient_failure(error: Exception, context: Dict[str, Any], 
                            attempt: int, max_attempts: int) -> bool:
    """
    Determine if an error is a transient failure that should be retried.
    
    Args:
        error: Exception that occurred
        context: Context information
        attempt: Current attempt number
        max_attempts: Maximum number of attempts
        
    Returns:
        True if error is transient and should be retried
    """
    # List of transient error indicators
    transient_indicators = [
        'timeout',
        'connection',
        'temporary',
        'busy',
        'locked',
        'unavailable',
        'retry'
    ]
    
    error_message = str(error).lower()
    
    # Check if error message contains transient indicators
    is_transient = any(indicator in error_message for indicator in transient_indicators)
    
    # Specific error types that are often transient
    transient_types = (IOError, OSError, RuntimeError, SimulationError)
    is_transient_type = isinstance(error, transient_types)
    
    # Don't retry if we've exhausted attempts
    if attempt >= max_attempts:
        logger.warning(f"Max retry attempts ({max_attempts}) reached, not retrying")
        return False
    
    # Log transient failure detection
    if is_transient or is_transient_type:
        logger.info(f"Transient failure detected (attempt {attempt}/{max_attempts}): {type(error).__name__}")
        logger.debug(f"Error message: {error_message}")
        return True
    
    return False


def recover_from_error(error: Exception, context: Dict[str, Any]) -> Optional[Any]:
    """
    Attempt to recover from an error using context-specific strategies.
    
    Args:
        error: Exception to recover from
        context: Context information
        
    Returns:
        Recovery result if successful, None otherwise
    """
    logger.info(f"Attempting error recovery for {type(error).__name__}")
    
    recovery_manager = get_recovery_manager()
    
    # Try registered recovery strategies first
    result = recovery_manager.attempt_recovery(error, context)
    if result is not None:
        logger.info("Recovery successful using registered strategy")
        return result
    
    # Try context-specific recovery
    if isinstance(error, SimulationError):
        logger.info("Attempting simulation error recovery")
        # Try with different random seed
        import numpy as np
        new_seed = np.random.randint(0, 1000000)
        np.random.seed(new_seed)
        logger.info(f"Reset random seed to {new_seed}")
        return None  # Signal to retry
    
    elif isinstance(error, (IOError, OSError)):
        logger.info("Attempting I/O error recovery")
        # Try creating directories if they don't exist
        if 'path' in context:
            try:
                import os
                path = context['path']
                os.makedirs(os.path.dirname(path), exist_ok=True)
                logger.info(f"Created directory for path: {path}")
                return None  # Signal to retry
            except Exception as e:
                logger.error(f"Failed to create directory: {e}")
    
    logger.warning("No recovery strategy available for this error")
    return None
