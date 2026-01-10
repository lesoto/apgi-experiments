"""Logging configuration for the APGI Framework GUI."""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


def setup_logging(name: str, log_dir: str) -> logging.Logger:
    """Set up logging configuration.

    Args:
        name: Name of the logger
        log_dir: Directory to store log files

    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )

    # Create handlers
    # File handler with rotation (10MB per file, keep 5 backups)
    log_file = log_path / f"{name}.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Prevent double logging if called multiple times
    logger.propagate = False

    return logger


def log_exceptions(logger: logging.Logger):
    """Decorator to log exceptions from functions.

    Args:
        logger: Logger instance to use for logging

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Exception in {func.__name__}")
                raise

        return wrapper

    return decorator


def log_duration(logger: logging.Logger, level: int = logging.DEBUG):
    """Decorator to log the execution time of functions.

    Args:
        logger: Logger instance to use for logging
        level: Logging level to use (default: DEBUG)

    Returns:
        Decorator function
    """
    import time

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                logger.log(level, f"{func.__name__} took {duration:.3f} seconds")

        return wrapper

    return decorator
