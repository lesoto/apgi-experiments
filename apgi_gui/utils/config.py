"""Configuration management for the APGI Framework GUI."""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ValidationError:
    """Configuration validation error."""

    field: str
    message: str
    severity: str = "warning"  # "warning", "error"


class ConfigValidator:
    """Validates configuration values."""

    @staticmethod
    def validate_theme(value: str) -> Optional[ValidationError]:
        """Validate theme value."""
        if value not in ["light", "dark", "system"]:
            return ValidationError(
                "theme", f"Invalid theme: {value}. Must be 'light', 'dark', or 'system'"
            )
        return None

    @staticmethod
    def validate_window_geometry(
        width: int, height: int, x: int, y: int
    ) -> List[ValidationError]:
        """Validate window geometry."""
        errors = []

        if width < 800 or width > 3840:
            errors.append(
                ValidationError(
                    "window_width", f"Width {width} out of range (800-3840)"
                )
            )

        if height < 600 or height > 2160:
            errors.append(
                ValidationError(
                    "window_height", f"Height {height} out of range (600-2160)"
                )
            )

        if x < -3840 or x > 3840:
            errors.append(
                ValidationError("window_x", f"X position {x} out of range (-3840-3840)")
            )

        if y < -2160 or y > 2160:
            errors.append(
                ValidationError("window_y", f"Y position {y} out of range (-2160-2160)")
            )

        return errors

    @staticmethod
    def validate_directory(path: str, field_name: str) -> Optional[ValidationError]:
        """Validate directory path."""
        try:
            path_obj = Path(path).expanduser().resolve()
            # Check if parent directory exists or can be created
            if not path_obj.parent.exists():
                return ValidationError(
                    field_name, f"Parent directory does not exist: {path_obj.parent}"
                )
        except Exception as e:
            return ValidationError(field_name, f"Invalid path: {path}")
        return None

    @staticmethod
    def validate_max_recent_files(value: int) -> Optional[ValidationError]:
        """Validate max recent files."""
        if value < 0 or value > 50:
            return ValidationError(
                "max_recent_files", f"Value {value} out of range (0-50)"
            )
        return None


class AppConfig:
    """Manages application configuration and paths."""

    def __init__(self):
        """Initialize the configuration with default values."""
        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Base directories
        self.app_name = "apgi_gui"
        self.app_dir = Path.home() / f".{self.app_name}"
        self.config_file = self.app_dir / "config.json"
        self.validator = ConfigValidator()

        # Create app directory if it doesn't exist
        self.app_dir.mkdir(exist_ok=True)

        # Default configuration
        self._default_config = {
            "theme": "system",
            "recent_files": [],  # type: List[str]
            "data_dir": str(Path.home() / "Documents" / "APGI_Data"),
            "log_dir": str(self.app_dir / "logs"),
            "window_width": 1800,
            "window_height": 1000,
            "window_x": 50,
            "window_y": 50,
            "max_recent_files": 10,
            "auto_save": True,
            "backup_count": 5,
            "file_monitor_interval": 2.0,  # File monitoring interval in seconds
            "max_undo_size": 100,  # Maximum undo/redo stack size
            "undo_memory_limit_mb": 50,  # Memory limit for undo stack in MB
        }

        # Load or create config file
        self._config = self._load_config()

        # Validate loaded config
        self._validate_and_fix_config()

        # Ensure all required directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        # Create data directory
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

        # Create log directory
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create a new one.

        Returns:
            Dict containing the configuration
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # Validate config structure
                if not isinstance(config, dict):
                    raise ValueError("Config must be a dictionary")

                # Merge with default config to ensure all keys exist
                merged_config = self._default_config.copy()
                merged_config.update(config)

                self.logger.info(f"Configuration loaded from {self.config_file}")
                return merged_config

            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON in config file: {e}")
                # Backup corrupted config and use defaults
                self._backup_corrupted_config()
                return self._default_config.copy()
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                return self._default_config.copy()
        else:
            # If config file doesn't exist, create it with defaults
            self.logger.info("Creating new configuration file with defaults")
            self._save_config(self._default_config)
            return self._default_config.copy()

    def _backup_corrupted_config(self) -> None:
        """Backup corrupted configuration file."""
        if self.config_file.exists():
            backup_path = self.config_file.with_suffix(".json.corrupted")
            try:
                import shutil

                shutil.copy2(self.config_file, backup_path)
                self.logger.warning(f"Corrupted config backed up to {backup_path}")
            except Exception as e:
                self.logger.error(f"Failed to backup corrupted config: {e}")

    def _validate_and_fix_config(self) -> None:
        """Validate current configuration and fix issues."""
        errors = []

        # Validate theme
        theme_error = self.validator.validate_theme(self._config.get("theme", ""))
        if theme_error:
            errors.append(theme_error)
            self._config["theme"] = self._default_config["theme"]

        # Validate window geometry
        width = self._config.get("window_width", 1800)
        height = self._config.get("window_height", 1000)
        x = self._config.get("window_x", 50)
        y = self._config.get("window_y", 50)

        geometry_errors = self.validator.validate_window_geometry(width, height, x, y)
        errors.extend(geometry_errors)

        # Fix geometry issues
        if geometry_errors:
            self._config["window_width"] = self._default_config["window_width"]
            self._config["window_height"] = self._default_config["window_height"]
            self._config["window_x"] = self._default_config["window_x"]
            self._config["window_y"] = self._default_config["window_y"]

        # Validate directories
        data_dir_error = self.validator.validate_directory(
            self._config.get("data_dir", ""), "data_dir"
        )
        if data_dir_error:
            errors.append(data_dir_error)
            self._config["data_dir"] = self._default_config["data_dir"]

        # Validate max recent files
        max_files_error = self.validator.validate_max_recent_files(
            self._config.get("max_recent_files", 10)
        )
        if max_files_error:
            errors.append(max_files_error)
            self._config["max_recent_files"] = self._default_config["max_recent_files"]

        # Log validation results
        if errors:
            self.logger.warning(f"Configuration validation found {len(errors)} issues:")
            for error in errors:
                self.logger.warning(f"  {error.field}: {error.message}")
            # Save fixed configuration
            self._save_config(self._config)

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file with error handling.

        Args:
            config: Configuration dictionary to save
        """
        try:
            # Create backup if file exists
            if self.config_file.exists():
                backup_path = self.config_file.with_suffix(".json.bak")
                import shutil

                shutil.copy2(self.config_file, backup_path)

            # Save new config
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Configuration saved to {self.config_file}")

        except PermissionError as e:
            self.logger.error(f"Permission denied saving config: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            raise

    def save(self) -> None:
        """Save the current configuration to file."""
        self._save_config(self._config)

    @property
    def theme(self) -> str:
        """Get the current theme."""
        return self._config["theme"]

    @theme.setter
    def theme(self, value: str) -> None:
        """Set the current theme.

        Args:
            value: Theme name ("light", "dark", or "system")
        """
        if value in ["light", "dark", "system"]:
            self._config["theme"] = value

    @property
    def data_dir(self) -> str:
        """Get the data directory path."""
        return self._config["data_dir"]

    @data_dir.setter
    def data_dir(self, value: str) -> None:
        """Set the data directory path.

        Args:
            value: Path to the data directory
        """
        self._config["data_dir"] = str(Path(value).expanduser().resolve())

    @property
    def log_dir(self) -> str:
        """Get the log directory path."""
        return self._config["log_dir"]

    @log_dir.setter
    def log_dir(self, value: str) -> None:
        """Set the log directory path.

        Args:
            value: Path to the log directory
        """
        self._config["log_dir"] = str(Path(value).expanduser().resolve())

    @property
    def file_monitor_interval(self) -> float:
        """Get the file monitoring interval in seconds."""
        return float(self._config["file_monitor_interval"])

    @file_monitor_interval.setter
    def file_monitor_interval(self, value: float) -> None:
        """Set the file monitoring interval in seconds.

        Args:
            value: Interval in seconds (must be between 0.1 and 60.0)
        """
        if 0.1 <= value <= 60.0:
            self._config["file_monitor_interval"] = float(value)
        else:
            raise ValueError(
                "File monitor interval must be between 0.1 and 60.0 seconds"
            )

    @property
    def recent_files_path(self) -> Path:
        """Get the path to the recent files list."""
        return self.app_dir / "recent_files.json"

    @property
    def max_recent_files(self) -> int:
        """Get the maximum number of recent files to remember."""
        return self._config["max_recent_files"]

    @property
    def max_undo_size(self) -> int:
        """Get the maximum undo/redo stack size."""
        return self._config["max_undo_size"]

    @max_undo_size.setter
    def max_undo_size(self, value: int) -> None:
        """Set the maximum undo/redo stack size."""
        if 10 <= value <= 1000:
            self._config["max_undo_size"] = value
        else:
            raise ValueError("Max undo size must be between 10 and 1000")

    @property
    def undo_memory_limit_mb(self) -> int:
        """Get the undo stack memory limit in MB."""
        return self._config["undo_memory_limit_mb"]

    @undo_memory_limit_mb.setter
    def undo_memory_limit_mb(self, value: int) -> None:
        """Set the undo stack memory limit in MB."""
        if 10 <= value <= 500:
            self._config["undo_memory_limit_mb"] = value
        else:
            raise ValueError("Undo memory limit must be between 10 and 500 MB")

    @property
    def window_size(self) -> Tuple[int, int]:
        """Get the window size as (width, height)."""
        return (self._config["window_width"], self._config["window_height"])

    @property
    def window_position(self) -> Tuple[int, int]:
        """Get the window position as (x, y)."""
        return (self._config["window_x"], self._config["window_y"])

    def update_window_geometry(self, width: int, height: int, x: int, y: int) -> None:
        """Update the window geometry in the config.

        Args:
            width: Window width
            height: Window height
            x: Window x position
            y: Window y position
        """
        self._config["window_width"] = width
        self._config["window_height"] = height
        self._config["window_x"] = x
        self._config["window_y"] = y
        self.save()
