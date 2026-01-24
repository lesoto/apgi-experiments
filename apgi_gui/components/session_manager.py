"""
Unified session management system for APGI Framework GUI applications.

Provides consistent session handling across multiple GUI instances with
automatic state saving, recovery, and synchronization.
"""

import json
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import pickle
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Represents the state of a GUI session."""

    session_id: str
    gui_type: str
    created_at: datetime
    last_updated: datetime
    window_geometry: str
    window_state: str  # normal, maximized, minimized
    current_theme: str
    open_files: List[str]
    recent_files: List[str]
    user_preferences: Dict[str, Any]
    experiment_state: Optional[Dict[str, Any]] = None
    custom_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data["created_at"] = self.created_at.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        """Create from dictionary."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)


class SessionManager:
    """
    Unified session management system.

    Handles session creation, persistence, recovery, and synchronization
    across multiple GUI instances.
    """

    def __init__(self, gui_type: str = "default"):
        self.gui_type = gui_type
        self.current_session: Optional[SessionState] = None
        self.session_callbacks: List[Callable] = []
        self.auto_save_interval = 300  # 5 minutes
        self.auto_save_timer: Optional[threading.Timer] = None
        self.lock = threading.Lock()

        # Session storage
        self.session_dir = Path.home() / ".apgi_framework" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Current session file
        self.current_session_file = self.session_dir / f"{gui_type}_current.json"

        # Load or create session
        self._load_or_create_session()

        # Start auto-save
        self._start_auto_save()

        logger.info(f"Session manager initialized for {gui_type} GUI")

    def _load_or_create_session(self):
        """Load existing session or create a new one."""
        try:
            if self.current_session_file.exists():
                with open(self.current_session_file, "r") as f:
                    data = json.load(f)

                self.current_session = SessionState.from_dict(data)
                logger.info(
                    f"Loaded existing session: {self.current_session.session_id}"
                )
            else:
                self._create_new_session()

        except Exception as e:
            logger.warning(f"Failed to load session, creating new one: {e}")
            self._create_new_session()

    def _create_new_session(self):
        """Create a new session."""
        self.current_session = SessionState(
            session_id=str(uuid.uuid4()),
            gui_type=self.gui_type,
            created_at=datetime.now(),
            last_updated=datetime.now(),
            window_geometry="800x600+100+100",
            window_state="normal",
            current_theme="light",
            open_files=[],
            recent_files=[],
            user_preferences={},
            experiment_state=None,
            custom_data={},
        )

        self._save_session()
        logger.info(f"Created new session: {self.current_session.session_id}")

    def _start_auto_save(self):
        """Start the auto-save timer."""
        if self.auto_save_timer:
            self.auto_save_timer.cancel()

        self.auto_save_timer = threading.Timer(self.auto_save_interval, self._auto_save)
        self.auto_save_timer.daemon = True
        self.auto_save_timer.start()

    def _auto_save(self):
        """Auto-save the current session."""
        try:
            self.save_session()
            logger.debug("Auto-saved session")
        except Exception as e:
            logger.error(f"Auto-save failed: {e}")
        finally:
            # Restart the timer
            self._start_auto_save()

    def save_session(self):
        """Save the current session to disk."""
        if not self.current_session:
            return

        with self.lock:
            try:
                self.current_session.last_updated = datetime.now()

                with open(self.current_session_file, "w") as f:
                    json.dump(self.current_session.to_dict(), f, indent=2)

                # Also save to history
                self._save_to_history()

                logger.debug(f"Session saved: {self.current_session.session_id}")

            except Exception as e:
                logger.error(f"Failed to save session: {e}")

    def _save_to_history(self):
        """Save session to history for recovery."""
        try:
            history_file = self.session_dir / f"{self.gui_type}_history.json"

            # Load existing history
            history = []
            if history_file.exists():
                with open(history_file, "r") as f:
                    history = json.load(f)

            # Add current session
            history.append(self.current_session.to_dict())

            # Keep only last 10 sessions
            history = history[-10:]

            # Save history
            with open(history_file, "w") as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to save session to history: {e}")

    def get_session_state(self) -> Optional[SessionState]:
        """Get the current session state."""
        return self.current_session

    def update_window_state(self, geometry: str, state: str):
        """Update window geometry and state."""
        if self.current_session:
            with self.lock:
                self.current_session.window_geometry = geometry
                self.current_session.window_state = state
                self.current_session.last_updated = datetime.now()

    def update_theme(self, theme: str):
        """Update the current theme."""
        if self.current_session:
            with self.lock:
                self.current_session.current_theme = theme
                self.current_session.last_updated = datetime.now()

    def add_open_file(self, file_path: str):
        """Add a file to the open files list."""
        if self.current_session:
            with self.lock:
                if file_path not in self.current_session.open_files:
                    self.current_session.open_files.append(file_path)
                self._add_to_recent_files(file_path)
                self.current_session.last_updated = datetime.now()

    def remove_open_file(self, file_path: str):
        """Remove a file from the open files list."""
        if self.current_session:
            with self.lock:
                if file_path in self.current_session.open_files:
                    self.current_session.open_files.remove(file_path)
                self.current_session.last_updated = datetime.now()

    def _add_to_recent_files(self, file_path: str):
        """Add a file to recent files list."""
        if self.current_session:
            # Remove if already exists
            if file_path in self.current_session.recent_files:
                self.current_session.recent_files.remove(file_path)

            # Add to beginning
            self.current_session.recent_files.insert(0, file_path)

            # Keep only last 20 recent files
            self.current_session.recent_files = self.current_session.recent_files[:20]

    def get_recent_files(self) -> List[str]:
        """Get list of recent files."""
        if self.current_session:
            return self.current_session.recent_files.copy()
        return []

    def update_user_preference(self, key: str, value: Any):
        """Update a user preference."""
        if self.current_session:
            with self.lock:
                self.current_session.user_preferences[key] = value
                self.current_session.last_updated = datetime.now()

    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        if self.current_session:
            return self.current_session.user_preferences.get(key, default)
        return default

    def update_experiment_state(self, state: Dict[str, Any]):
        """Update experiment state."""
        if self.current_session:
            with self.lock:
                self.current_session.experiment_state = state
                self.current_session.last_updated = datetime.now()

    def get_experiment_state(self) -> Optional[Dict[str, Any]]:
        """Get experiment state."""
        if self.current_session:
            return self.current_session.experiment_state
        return None

    def set_custom_data(self, key: str, value: Any):
        """Set custom session data."""
        if self.current_session:
            with self.lock:
                if not self.current_session.custom_data:
                    self.current_session.custom_data = {}
                self.current_session.custom_data[key] = value
                self.current_session.last_updated = datetime.now()

    def get_custom_data(self, key: str, default: Any = None) -> Any:
        """Get custom session data."""
        if self.current_session and self.current_session.custom_data:
            return self.current_session.custom_data.get(key, default)
        return default

    def get_session_history(self) -> List[SessionState]:
        """Get session history for recovery."""
        try:
            history_file = self.session_dir / f"{self.gui_type}_history.json"

            if history_file.exists():
                with open(history_file, "r") as f:
                    history_data = json.load(f)

                return [SessionState.from_dict(data) for data in history_data]

            return []

        except Exception as e:
            logger.error(f"Failed to load session history: {e}")
            return []

    def restore_session(self, session_id: str) -> bool:
        """Restore a specific session from history."""
        try:
            history = self.get_session_history()

            for session in history:
                if session.session_id == session_id:
                    self.current_session = session
                    self._save_session()

                    # Notify callbacks
                    for callback in self.session_callbacks:
                        try:
                            callback("session_restored", session)
                        except Exception as e:
                            logger.error(f"Session callback error: {e}")

                    logger.info(f"Restored session: {session_id}")
                    return True

            logger.warning(f"Session not found: {session_id}")
            return False

        except Exception as e:
            logger.error(f"Failed to restore session: {e}")
            return False

    def clear_session(self):
        """Clear the current session (reset to defaults)."""
        self._create_new_session()

        # Notify callbacks
        for callback in self.session_callbacks:
            try:
                callback("session_cleared", self.current_session)
            except Exception as e:
                logger.error(f"Session callback error: {e}")

    def export_session(self, file_path: Path) -> bool:
        """Export current session to a file."""
        if not self.current_session:
            return False

        try:
            export_data = {
                "session": self.current_session.to_dict(),
                "exported_at": datetime.now().isoformat(),
                "gui_type": self.gui_type,
            }

            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"Session exported to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export session: {e}")
            return False

    def import_session(self, file_path: Path) -> bool:
        """Import session from a file."""
        try:
            with open(file_path, "r") as f:
                import_data = json.load(f)

            session_data = import_data["session"]
            self.current_session = SessionState.from_dict(session_data)
            self._save_session()

            # Notify callbacks
            for callback in self.session_callbacks:
                try:
                    callback("session_imported", self.current_session)
                except Exception as e:
                    logger.error(f"Session callback error: {e}")

            logger.info(f"Session imported from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to import session: {e}")
            return False

    def add_session_callback(self, callback: Callable):
        """Add a callback for session events."""
        self.session_callbacks.append(callback)

    def remove_session_callback(self, callback: Callable):
        """Remove a session callback."""
        if callback in self.session_callbacks:
            self.session_callbacks.remove(callback)

    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session."""
        if not self.current_session:
            return {}

        return {
            "session_id": self.current_session.session_id,
            "gui_type": self.current_session.gui_type,
            "created_at": self.current_session.created_at.isoformat(),
            "last_updated": self.current_session.last_updated.isoformat(),
            "window_state": self.current_session.window_state,
            "current_theme": self.current_session.current_theme,
            "open_files_count": len(self.current_session.open_files),
            "recent_files_count": len(self.current_session.recent_files),
            "preferences_count": len(self.current_session.user_preferences),
        }

    def cleanup_old_sessions(self, days: int = 30):
        """Clean up old session files."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            for file_path in self.session_dir.glob("*.json"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_path.unlink()
                    logger.debug(f"Cleaned up old session file: {file_path}")

        except Exception as e:
            logger.warning(f"Failed to cleanup old sessions: {e}")

    def __del__(self):
        """Cleanup when session manager is destroyed."""
        if self.auto_save_timer:
            self.auto_save_timer.cancel()

        # Save final session state
        if self.current_session:
            self.save_session()


class MultiGUISessionManager:
    """
    Manages sessions across multiple GUI instances.

    Provides synchronization and coordination between different GUI types.
    """

    def __init__(self):
        self.session_managers: Dict[str, SessionManager] = {}
        self.global_callbacks: List[Callable] = []
        self.lock = threading.Lock()

        # Global session storage
        self.global_session_dir = Path.home() / ".apgi_framework" / "global_sessions"
        self.global_session_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Multi-GUI session manager initialized")

    def get_session_manager(self, gui_type: str) -> SessionManager:
        """Get or create a session manager for a GUI type."""
        with self.lock:
            if gui_type not in self.session_managers:
                self.session_managers[gui_type] = SessionManager(gui_type)

                # Add global callback
                self.session_managers[gui_type].add_session_callback(
                    self._on_session_event
                )

            return self.session_managers[gui_type]

    def _on_session_event(self, event_type: str, session_data: Any):
        """Handle session events from individual GUIs."""
        # Notify global callbacks
        for callback in self.global_callbacks:
            try:
                callback(event_type, session_data)
            except Exception as e:
                logger.error(f"Global session callback error: {e}")

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active sessions."""
        sessions = {}

        for gui_type, manager in self.session_managers.items():
            sessions[gui_type] = manager.get_session_info()

        return sessions

    def synchronize_theme(self, theme: str):
        """Synchronize theme across all GUI instances."""
        for manager in self.session_managers.values():
            manager.update_theme(theme)
            manager.save_session()

        logger.info(f"Synchronized theme across all GUIs: {theme}")

    def get_global_recent_files(self) -> List[str]:
        """Get recent files from all GUI instances."""
        all_recent = []

        for manager in self.session_managers.values():
            all_recent.extend(manager.get_recent_files())

        # Remove duplicates and sort by most recent
        seen = set()
        unique_recent = []
        for file_path in all_recent:
            if file_path not in seen:
                seen.add(file_path)
                unique_recent.append(file_path)

        return unique_recent[:50]  # Limit to 50 most recent

    def add_global_callback(self, callback: Callable):
        """Add a global session callback."""
        self.global_callbacks.append(callback)

    def cleanup_all_sessions(self, days: int = 30):
        """Clean up old sessions for all GUI types."""
        for manager in self.session_managers.values():
            manager.cleanup_old_sessions(days)


# Global instance for easy access
_global_session_manager: Optional[MultiGUISessionManager] = None


def get_session_manager(gui_type: str = "default") -> SessionManager:
    """Get the session manager for a specific GUI type."""
    global _global_session_manager

    if _global_session_manager is None:
        _global_session_manager = MultiGUISessionManager()

    return _global_session_manager.get_session_manager(gui_type)


def get_global_session_manager() -> MultiGUISessionManager:
    """Get the global session manager."""
    global _global_session_manager

    if _global_session_manager is None:
        _global_session_manager = MultiGUISessionManager()

    return _global_session_manager
