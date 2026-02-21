"""
Error logging utilities for APGI Framework.

Provides integration between error handling and configuration system.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_error_log_dir(gui_config_path: Optional[Path] = None) -> Path:
    """
    Get the configured error log directory.

    Attempts to use the GUI config system's log_dir if available,
    otherwise falls back to the default ~/.apgi/error_logs.

    Args:
        gui_config_path: Optional path to GUI config file

    Returns:
        Path to the error log directory
    """
    try:
        # Try to import and use GUI config
        from apgi_gui.utils.config import ConfigManager

        config = ConfigManager()
        log_dir = Path(config.log_dir) / "error_logs"
        logger.debug(f"Using configured error log directory: {log_dir}")
        return log_dir

    except ImportError:
        # GUI config not available, use default
        log_dir = Path.home() / ".apgi" / "error_logs"
        logger.debug(
            f"GUI config not available, using default error log directory: {log_dir}"
        )
        return log_dir
    except Exception as e:
        # Error accessing config, fall back to default
        log_dir = Path.home() / ".apgi" / "error_logs"
        logger.warning(
            f"Error accessing GUI config ({e}), using default error log directory: {log_dir}"
        )
        return log_dir
