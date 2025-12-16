"""
Standardized logging configuration for APGI Framework.

Provides consistent logging across all modules with proper levels,
formatting, and security considerations. Replaces inconsistent print() usage.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime, timezone
import json
import traceback
from contextlib import contextmanager


class APGILogger:
    """
    Standardized logger for the APGI Framework.
    
    Provides consistent logging with security features, structured output,
    and proper error handling to replace inconsistent print() statements.
    """
    
    def __init__(self, name: str, log_level: str = "INFO", 
                 log_file: Optional[Union[str, Path]] = None,
                 enable_console: bool = True,
                 enable_structured: bool = False):
        """
        Initialize APGI logger.
        
        Args:
            name: Logger name (usually module name)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path
            enable_console: Whether to output to console
            enable_structured: Whether to use JSON structured logging
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.enable_structured = enable_structured
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Set log level
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatters
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.structured_formatter = StructuredFormatter()
        
        # Add console handler if enabled
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(
                self.structured_formatter if enable_structured else self.formatter
            )
            self.logger.addHandler(console_handler)
        
        # Add file handler if specified
        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use rotating file handler to prevent large log files
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setFormatter(
                self.structured_formatter if enable_structured else self.formatter
            )
            self.logger.addHandler(file_handler)
        
        # Prevent propagation to root logger to avoid duplicate messages
        self.logger.propagate = False
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception details."""
        if exception:
            kwargs['exception_type'] = type(exception).__name__
            kwargs['exception_message'] = str(exception)
            kwargs['traceback'] = traceback.format_exc()
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message with optional exception details."""
        if exception:
            kwargs['exception_type'] = type(exception).__name__
            kwargs['exception_message'] = str(exception)
            kwargs['traceback'] = traceback.format_exc()
        self._log(logging.CRITICAL, message, **kwargs)
    
    def experiment_start(self, experiment_id: str, parameters: Dict[str, Any]):
        """Log experiment start."""
        self.info(f"Experiment started: {experiment_id}", 
                 experiment_id=experiment_id,
                 parameters=parameters,
                 event_type="experiment_start")
    
    def experiment_end(self, experiment_id: str, status: str, duration: float):
        """Log experiment end."""
        self.info(f"Experiment completed: {experiment_id} ({status})",
                 experiment_id=experiment_id,
                 status=status,
                 duration_seconds=duration,
                 event_type="experiment_end")
    
    def security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related event."""
        self.warning(f"Security event: {event_type}",
                    security_event_type=event_type,
                    details=details,
                    event_type="security")
    
    def performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log performance metric."""
        self.debug(f"Performance: {metric_name} = {value} {unit}",
                   metric_name=metric_name,
                   metric_value=value,
                   metric_unit=unit,
                   event_type="performance")
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method with extra data."""
        extra_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'module': self.name,
            **kwargs
        }
        
        if self.enable_structured:
            self.logger.log(level, message, extra={'extra_data': extra_data})
        else:
            # For non-structured logging, add key info to message
            if kwargs:
                key_info = ', '.join(f"{k}={v}" for k, v in list(kwargs.items())[:3])
                message = f"{message} [{key_info}]"
            self.logger.log(level, message)
    
    @contextmanager
    def log_execution(self, operation: str):
        """Context manager to log operation execution time."""
        start_time = datetime.now()
        self.debug(f"Starting operation: {operation}")
        
        try:
            yield
            duration = (datetime.now() - start_time).total_seconds()
            self.info(f"Completed operation: {operation}", 
                     operation=operation,
                     duration_seconds=duration)
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.error(f"Failed operation: {operation}", exception=e,
                      operation=operation,
                      duration_seconds=duration)
            raise


class StructuredFormatter(logging.Formatter):
    """JSON structured formatter for machine-readable logs."""
    
    def format(self, record):
        log_entry = {
            'execution_time_seconds': record.execution_time.total_seconds(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra data if available
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
        
        return json.dumps(log_entry)


class LoggingManager:
    """
    Centralized logging manager for the APGI Framework.
    
    Manages logger instances, configuration, and provides
    factory methods for consistent logging setup.
    """
    
    _loggers: Dict[str, APGILogger] = {}
    _global_config: Dict[str, Any] = {}
    
    @classmethod
    def configure_global_logging(cls, 
                               log_level: str = "INFO",
                               log_dir: Optional[Union[str, Path]] = None,
                               enable_structured: bool = False,
                               enable_console: bool = True):
        """
        Configure global logging settings.
        
        Args:
            log_level: Default logging level
            log_dir: Directory for log files
            enable_structured: Enable JSON structured logging
            enable_console: Enable console output
        """
        cls._global_config = {
            'log_level': log_level,
            'log_dir': Path(log_dir) if log_dir else None,
            'enable_structured': enable_structured,
            'enable_console': enable_console
        }
        
        # Create log directory if specified
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_logger(cls, name: str, 
                  log_file: Optional[Union[str, Path]] = None,
                  **kwargs) -> APGILogger:
        """
        Get or create a logger instance.
        
        Args:
            name: Logger name
            log_file: Optional specific log file
            **kwargs: Additional logger configuration
            
        Returns:
            APGILogger instance
        """
        if name not in cls._loggers:
            # Merge global config with specific config
            config = cls._global_config.copy()
            config.update(kwargs)
            
            # Determine log file path
            if log_file is None and config.get('log_dir'):
                log_file = Path(config['log_dir']) / f"{name.replace('.', '_')}.log"
            
            # Create logger
            cls._loggers[name] = APGILogger(
                name=name,
                log_level=config.get('log_level', 'INFO'),
                log_file=log_file,
                enable_console=config.get('enable_console', True),
                enable_structured=config.get('enable_structured', False)
            )
        
        return cls._loggers[name]
    
    @classmethod
    def replace_print_with_logging(cls, module_name: str):
        """
        Replace print() statements with logging for a specific module.
        
        This is a utility function to help migrate from print() to proper logging.
        
        Args:
            module_name: Name of the module to modify
        """
        logger = cls.get_logger(module_name)
        
        # Create a print replacement function
        def safe_print(*args, **kwargs):
            """Print replacement that logs instead."""
            message = ' '.join(str(arg) for arg in args)
            logger.info(message)
        
        # This would need to be called from the target module
        return safe_print


def get_logger(name: str, **kwargs) -> APGILogger:
    """
    Convenience function to get a logger.
    
    Args:
        name: Logger name
        **kwargs: Additional configuration
        
    Returns:
        APGILogger instance
    """
    return LoggingManager.get_logger(name, **kwargs)


def setup_logging(log_level: str = "INFO",
                 log_dir: Optional[str] = None,
                 enable_structured: bool = False):
    """
    Setup global logging configuration.
    
    Args:
        log_level: Default logging level
        log_dir: Directory for log files
        enable_structured: Enable JSON structured logging
    """
    LoggingManager.configure_global_logging(
        log_level=log_level,
        log_dir=log_dir,
        enable_structured=enable_structured
    )


# Common logger instances for core modules
def get_security_logger() -> APGILogger:
    """Get logger for security-related events."""
    return get_logger("apgi.security")


def get_experiment_logger() -> APGILogger:
    """Get logger for experiment operations."""
    return get_logger("apgi.experiments")


def get_data_logger() -> APGILogger:
    """Get logger for data operations."""
    return get_logger("apgi.data")


def get_gui_logger() -> APGILogger:
    """Get logger for GUI operations."""
    return get_logger("apgi.gui")


def get_analysis_logger() -> APGILogger:
    """Get logger for analysis operations."""
    return get_logger("apgi.analysis")
