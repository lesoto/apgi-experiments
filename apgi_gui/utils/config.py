"""Configuration management for the APGI Framework GUI."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class AppConfig:
    """Manages application configuration and paths."""
    
    def __init__(self):
        """Initialize the configuration with default values."""
        # Base directories
        self.app_name = "apgi_gui"
        self.app_dir = Path.home() / f".{self.app_name}"
        self.config_file = self.app_dir / "config.json"
        
        # Create app directory if it doesn't exist
        self.app_dir.mkdir(exist_ok=True)
        
        # Default configuration
        self._default_config = {
            "theme": "light",
            "recent_files": [],
            "data_dir": str(Path.home() / "Documents" / "APGI_Data"),
            "log_dir": str(self.app_dir / "logs"),
            "window_width": 1800,
            "window_height": 1000,
            "window_x": 50,
            "window_y": 50,
            "max_recent_files": 10,
        }
        
        # Load or create config file
        self._config = self._load_config()
        
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
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Merge with default config to ensure all keys exist
                merged_config = self._default_config.copy()
                merged_config.update(config)
                return merged_config
            except Exception:
                # If there's an error loading the config, use defaults
                return self._default_config.copy()
        else:
            # If config file doesn't exist, create it with defaults
            self._save_config(self._default_config)
            return self._default_config.copy()
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
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
            value: Theme name ("light" or "dark")
        """
        if value in ["light", "dark"]:
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
    
    @property
    def recent_files_path(self) -> Path:
        """Get the path to the recent files list."""
        return self.app_dir / "recent_files.json"
    
    @property
    def max_recent_files(self) -> int:
        """Get the maximum number of recent files to remember."""
        return self._config["max_recent_files"]
    
    @property
    def window_size(self) -> tuple[int, int]:
        """Get the window size as (width, height)."""
        return (self._config["window_width"], self._config["window_height"])
    
    @property
    def window_position(self) -> tuple[int, int]:
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
