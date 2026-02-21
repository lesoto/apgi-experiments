"""User preferences management for APGI Framework GUI."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class UserPreferences:
    """Manage user preferences and settings persistence."""

    def __init__(self, config_dir: Path = None):
        """Initialize user preferences manager.

        Args:
            config_dir: Directory to store preferences file
        """
        if config_dir is None:
            config_dir = Path.home() / ".apgi_framework"

        self.config_dir = config_dir
        self.config_file = config_dir / "preferences.json"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Default preferences
        self.defaults = {
            "recent_files": [],
            "window_geometry": "",
            "theme": "light",
            "font_size": 12,
            "auto_save": True,
            "max_recent_files": 10,
        }

        self.preferences = self._load_preferences()

    def _load_preferences(self) -> Dict[str, Any]:
        """Load preferences from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**self.defaults, **loaded}
            else:
                return self.defaults.copy()
        except Exception as e:
            logger.warning(f"Failed to load preferences: {e}")
            return self.defaults.copy()

    def save_preferences(self) -> bool:
        """Save preferences to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.preferences, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return False

    def get_recent_files(self) -> List[str]:
        """Get list of recent files."""
        return self.preferences.get("recent_files", [])

    def add_recent_file(self, file_path: str) -> None:
        """Add a file to recent files list."""
        recent_files = self.get_recent_files()

        # Remove if already exists (to move to top)
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Add to beginning
        recent_files.insert(0, file_path)

        # Limit to max_recent_files
        max_files = self.preferences.get("max_recent_files", 10)
        recent_files = recent_files[:max_files]

        self.preferences["recent_files"] = recent_files
        self.save_preferences()

    def clear_recent_files(self) -> None:
        """Clear recent files list."""
        self.preferences["recent_files"] = []
        self.save_preferences()

    def set_window_geometry(self, geometry: str) -> None:
        """Set window geometry."""
        self.preferences["window_geometry"] = geometry
        self.save_preferences()

    def get_window_geometry(self) -> str:
        """Get window geometry."""
        return self.preferences.get("window_geometry", "")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value."""
        return self.preferences.get(key, default)

    def set_preference(self, key: str, value: Any) -> None:
        """Set a preference value."""
        self.preferences[key] = value
        self.save_preferences()
