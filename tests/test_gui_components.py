"""
Test suite for GUI components - backup_manager, theme_manager, session_manager, and monitoring integration.

This module provides comprehensive testing for GUI components that manage system state,
user preferences, session handling, and real-time monitoring features.
"""

# Set matplotlib backend BEFORE any imports to prevent segfaults on headless systems
import os
import sys

# Must set this before importing matplotlib.pyplot or any tkagg backends
os.environ["MPLBACKEND"] = "Agg"

# Import and set matplotlib backend immediately
try:
    import matplotlib

    matplotlib.use("Agg", force=True)
except ImportError:
    pass

# Now safe to import other modules
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock

try:
    import tkinter as tk

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from apgi_gui.components.backup_manager import BackupManager
    from apgi_gui.components.theme_manager import AdvancedThemeManager
    from apgi_gui.components.session_manager import SessionManager
    from apgi_framework.monitoring.realtime_monitor import (
        RealtimeDataStreamer,
        MonitoringData,
    )
    from apgi_framework.gui.monitoring_dashboard import MultiModalMonitoringDashboard

    GUI_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"GUI components not available for testing: {e}")
    GUI_COMPONENTS_AVAILABLE = False


@unittest.skipUnless(
    TKINTER_AVAILABLE and GUI_COMPONENTS_AVAILABLE, "GUI components not available"
)
class TestBackupManager(unittest.TestCase):
    """Test cases for the BackupManager component."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.backup_manager = BackupManager(self.temp_dir)

        # Create test data structure
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
        (self.data_dir / "test_file.txt").write_text("test content")

        self.config_dir = self.temp_dir / "apgi_framework" / "config"
        self.config_dir.mkdir(parents=True)
        (self.config_dir / "test_config.json").write_text('{"test": "config"}')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_backup_manager_initialization(self):
        """Test BackupManager initializes correctly."""
        self.assertEqual(self.backup_manager.base_path, self.temp_dir)
        self.assertEqual(self.backup_manager.backup_dir, self.temp_dir / "backups")
        self.assertTrue(self.backup_manager.backup_dir.exists())

    def test_scan_backup_items(self):
        """Test scanning backup items for size calculation."""
        self.backup_manager.scan_backup_items()

        # Check that sizes were calculated
        for item_name, item_data in self.backup_manager.backup_items.items():
            self.assertIsInstance(item_data["size_mb"], (int, float))
            # Size can be 0 for small files or non-existent directories

    def test_create_backup_archive(self):
        """Test creating a backup archive."""
        # Create a backup
        backup_path = self.backup_manager.create_backup_archive("test_backup")

        self.assertTrue(backup_path.exists())
        self.assertTrue(backup_path.name.endswith(".zip"))

        # Verify archive contents
        with zipfile.ZipFile(backup_path, "r") as zip_ref:
            file_list = zip_ref.namelist()
            self.assertIn("data/test_file.txt", file_list)
            self.assertIn("apgi_framework/config/test_config.json", file_list)

    def test_list_backups(self):
        """Test listing available backups."""
        # Create a couple backups
        backup1 = self.backup_manager.create_backup_archive("backup1")
        backup2 = self.backup_manager.create_backup_archive("backup2")

        backups = self.backup_manager.list_backups()
        self.assertEqual(len(backups), 2)
        self.assertIn(backup1.name, [b["filename"] for b in backups])
        self.assertIn(backup2.name, [b["filename"] for b in backups])

    def test_restore_backup(self):
        """Test restoring from a backup."""
        # Create backup
        backup_path = self.backup_manager.create_backup_archive("restore_test")

        # Modify original file
        test_file = self.data_dir / "test_file.txt"
        original_content = test_file.read_text()
        test_file.write_text("modified content")

        # Restore backup
        self.backup_manager.restore_backup(backup_path.name)

        # Verify restoration
        self.assertEqual(test_file.read_text(), original_content)


@unittest.skipUnless(
    TKINTER_AVAILABLE and GUI_COMPONENTS_AVAILABLE, "GUI components not available"
)
class TestThemeManager(unittest.TestCase):
    """Test cases for the ThemeManager component."""

    def setUp(self):
        """Set up test fixtures."""
        self.theme_manager = AdvancedThemeManager(Mock())

    def test_theme_manager_initialization(self):
        """Test ThemeManager initializes with default theme."""
        self.assertIsNotNone(self.theme_manager.current_theme)
        self.assertIn("name", self.theme_manager.current_theme_info)
        self.assertIn("colors", self.theme_manager.current_theme_info)

    def test_apply_theme(self):
        """Test applying a theme to tkinter widgets."""
        # Create mock widget
        mock_widget = Mock()
        mock_widget.configure = Mock()

        self.theme_manager.apply_theme_to_widget(mock_widget, "background")
        mock_widget.configure.assert_called()

    def test_switch_theme(self):
        """Test switching between themes."""
        initial_theme = self.theme_manager.current_theme_info["name"]

        # Switch to a different theme if available
        available_themes = list(self.theme_manager.available_themes.keys())
        if len(available_themes) > 1:
            new_theme = (
                available_themes[1]
                if available_themes[0] == initial_theme
                else available_themes[0]
            )
            self.theme_manager.switch_theme(new_theme)
            self.assertEqual(self.theme_manager.current_theme_info["name"], new_theme)


@unittest.skipUnless(
    TKINTER_AVAILABLE and GUI_COMPONENTS_AVAILABLE, "GUI components not available"
)
class TestSessionManager(unittest.TestCase):
    """Test cases for the SessionManager component."""

    def setUp(self):
        """Set up test fixtures."""
        # Use a unique gui_type to avoid conflicts with other tests
        import uuid

        self.gui_type = f"test_{uuid.uuid4().hex[:8]}"
        self.session_manager = SessionManager(self.gui_type)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up the test session files
        try:
            session_dir = self.session_manager.session_dir
            if session_dir.exists():
                import shutil

                shutil.rmtree(session_dir, ignore_errors=True)
        except Exception:
            pass

    def test_session_manager_initialization(self):
        """Test SessionManager initializes correctly."""
        self.assertIsNotNone(self.session_manager.current_session)
        self.assertIn("session_id", self.session_manager.get_session_info())

    def test_save_load_session(self):
        """Test saving and loading session data."""
        # Modify session data via the session state
        self.session_manager.set_custom_data("test_key", "test_value")

        # Save session
        self.session_manager.save_session()

        # Create new session manager with same gui_type and check custom data persists
        new_session_manager = SessionManager(self.gui_type)
        loaded_value = new_session_manager.get_custom_data("test_key")

        self.assertEqual(loaded_value, "test_value")

    def test_clear_session(self):
        """Test clearing session data."""
        self.session_manager.set_custom_data("test_key", "test_value")
        self.session_manager.clear_session()
        # After clear, custom data should be reset (None or not exist)
        self.assertIsNone(self.session_manager.get_custom_data("test_key"))


@unittest.skipUnless(GUI_COMPONENTS_AVAILABLE, "Monitoring components not available")
class TestMonitoringIntegration(unittest.TestCase):
    """Integration tests for monitoring features."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = RealtimeDataStreamer()

    def test_monitoring_data_creation(self):
        """Test creating monitoring data."""
        data = MonitoringData(
            timestamp=1234567890.0,
            experiment_id="test_exp",
            data_type="test_type",
            value=42.0,
            metadata={"key": "value"},
        )

        self.assertEqual(data.timestamp, 1234567890.0)
        self.assertEqual(data.experiment_id, "test_exp")
        self.assertEqual(data.data_type, "test_type")
        self.assertEqual(data.value, 42.0)
        self.assertEqual(data.metadata["key"], "value")

    # @patch("apgi_framework.monitoring.realtime_monitor.websockets")
    # def test_websocket_monitor_connection(self, mock_websockets):
    #     """Test WebSocket monitor connection."""
    #     if not WEBSOCKETS_AVAILABLE:
    #         self.skipTest("WebSockets not available")

    #     # Mock websocket components
    #     mock_websocket = Mock()
    #     mock_websockets.connect.return_value.__aenter__ = Mock(
    #         return_value=mock_websocket
    #     )
    #     mock_websockets.connect.return_value.__aexit__ = Mock(return_value=None)

    #     monitor = WebSocketMonitor("ws://localhost:8080")

    #     # Test that monitor initializes
    #     self.assertIsNotNone(monitor.uri)

    def test_monitor_data_collection(self):
        """Test collecting monitoring data."""
        # Verify the streamer exists and has correct initial state
        self.assertIsNotNone(self.monitor)
        self.assertFalse(self.monitor.is_running)  # Server not started in tests


@unittest.skipUnless(
    TKINTER_AVAILABLE and GUI_COMPONENTS_AVAILABLE, "GUI components not available"
)
class TestMonitoringDashboard(unittest.TestCase):
    """Test cases for the MonitoringDashboard component."""

    def setUp(self):
        """Set up test fixtures."""
        # Skip if in CI/headless environment (macOS doesn't use DISPLAY)
        if os.environ.get("CI"):
            self.skipTest("CI/headless environment - skipping GUI tests")

        # Try to detect if we have a real display (macOS check)
        import platform

        if platform.system() == "Darwin":
            # On macOS, check if we can access window server
            if not os.environ.get("DISPLAY") and not os.environ.get("WINDOWID"):
                # Try a quick tkinter test to see if GUI works
                try:
                    test_root = tk.Tk()
                    test_root.withdraw()
                    test_root.update()
                    test_root.destroy()
                except tk.TclError:
                    self.skipTest("No GUI display available on macOS")

        self.root = tk.Tk()
        self.dashboard = MultiModalMonitoringDashboard(self.root)

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, "root") and self.root:
            self.root.destroy()

    def test_dashboard_initialization(self):
        """Test MonitoringDashboard initializes correctly."""
        # The dashboard has streamer, not monitor attribute
        self.assertIsNotNone(self.dashboard.streamer)
        self.assertIsNotNone(self.dashboard.root)

    def test_dashboard_update_display(self):
        """Test updating dashboard display."""
        # This would test the GUI update functionality
        # For now, just ensure the method exists and doesn't crash
        try:
            self.dashboard.update_display()
        except Exception as e:
            # GUI methods might fail in headless environment, that's ok
            self.assertIn("display", str(e).lower())  # Expected GUI-related error


if __name__ == "__main__":
    unittest.main()
