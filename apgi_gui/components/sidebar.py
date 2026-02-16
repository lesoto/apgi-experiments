"""Sidebar component for the APGI Framework GUI."""

import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from typing import Optional, Callable, Any, Dict
import json
import os
import threading
import time
from datetime import datetime
import logging

# Import user preferences for persistence
try:
    from ..utils.user_preferences import UserPreferences
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from apgi_gui.utils.user_preferences import UserPreferences


class Sidebar(ctk.CTkFrame):
    """Sidebar component containing navigation and tools."""

    def __init__(self, parent, app):
        """Initialize the sidebar.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent)
        self.app = app
        self.logger = logging.getLogger(__name__)

        # Initialize user preferences for persistence
        self.user_prefs = UserPreferences()

        # File monitoring
        self.file_monitor_active = False
        self.file_monitor_future = None
        self.monitor_interval = (
            self.app.config.file_monitor_interval
        )  # Use configurable interval
        self.file_timestamps = {}  # Store file timestamps for change detection
        self.file_lock = threading.Lock()  # Thread-safe access to file_timestamps

        # Import thread manager
        from apgi_framework.utils.thread_manager import thread_manager

        self.thread_manager = thread_manager

        self.setup_ui()
        self.start_file_monitoring()

    def setup_ui(self):
        """Set up the sidebar UI components."""
        self.logger.debug("Setting up sidebar UI")

        # Configure frame
        self.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self, text="APGI Framework", font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Navigation Section
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        nav_frame.grid_columnconfigure(0, weight=1)

        nav_label = ctk.CTkLabel(
            nav_frame, text="Navigation", font=ctk.CTkFont(size=16, weight="bold")
        )
        nav_label.grid(row=0, column=0, padx=10, pady=(10, 5))

        # Navigation buttons
        self.new_btn = ctk.CTkButton(
            nav_frame, text="New Configuration", command=self.app.new_file, height=40
        )
        self.new_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.open_btn = ctk.CTkButton(
            nav_frame, text="Open File", command=self.app.open_file, height=40
        )
        self.open_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.save_btn = ctk.CTkButton(
            nav_frame, text="Save File", command=self.app.save_file, height=40
        )
        self.save_btn.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Tools Section
        tools_frame = ctk.CTkFrame(self)
        tools_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        tools_frame.grid_columnconfigure(0, weight=1)

        tools_label = ctk.CTkLabel(
            tools_frame, text="Tools", font=ctk.CTkFont(size=16, weight="bold")
        )
        tools_label.grid(row=0, column=0, padx=10, pady=(10, 5))

        # Tool buttons
        self.undo_btn = ctk.CTkButton(
            tools_frame, text="Undo", command=self.app.undo, height=40
        )
        self.undo_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.redo_btn = ctk.CTkButton(
            tools_frame, text="Redo", command=self.app.redo, height=40
        )
        self.redo_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.theme_btn = ctk.CTkButton(
            tools_frame, text="Toggle Theme", command=self.app.toggle_theme, height=40
        )
        self.theme_btn.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Recent Files Section
        recent_frame = ctk.CTkFrame(self)
        recent_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        recent_frame.grid_columnconfigure(0, weight=1)
        recent_frame.grid_rowconfigure(1, weight=1)

        recent_label = ctk.CTkLabel(
            recent_frame, text="Recent Files", font=ctk.CTkFont(size=16, weight="bold")
        )
        recent_label.grid(row=0, column=0, padx=10, pady=(10, 5))

        # CustomTkinter scrollable frame for recent files
        self.recent_scrollable = ctk.CTkScrollableFrame(recent_frame, height=200)
        self.recent_scrollable.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.recent_scrollable.grid_columnconfigure(0, weight=1)

        # Recent files buttons (replacing tkinter Listbox)
        self.recent_file_buttons = []

        # Add backward compatibility listbox for tests
        self.recent_listbox = self._create_compatibility_listbox()

        # Help Section
        help_frame = ctk.CTkFrame(self)
        help_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        help_frame.grid_columnconfigure(0, weight=1)

        self.help_btn = ctk.CTkButton(
            help_frame, text="Help (F1)", command=self.app.show_help, height=40
        )
        self.help_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Configure grid weights for expansion
        self.grid_rowconfigure(3, weight=1)  # Recent files section expands

        # Load recent files
        self.update_recent_files()

        self.logger.debug("Sidebar UI setup completed")

    def update_recent_files(self):
        """Update the recent files list."""
        self.logger.debug("Updating recent files list")

        # Clear existing buttons
        for button in self.recent_file_buttons:
            button.destroy()
        self.recent_file_buttons.clear()

        # Clear compatibility listbox
        self.recent_listbox.clear()

        # Update file timestamps for monitoring
        with self.file_lock:
            self.file_timestamps.clear()

        # Create buttons for each recent file
        for i, file_path in enumerate(self.app.recent_files):
            # Store timestamp for monitoring
            try:
                if file_path.exists():
                    timestamp = file_path.stat().st_mtime
                    # Thread-safe update
                    with self.file_lock:
                        self.file_timestamps[str(file_path)] = timestamp
            except (OSError, PermissionError):
                self.logger.warning(f"Cannot access file: {file_path}")
                continue

            # Create button for the file
            display_name = file_path.name
            if len(display_name) >= 30:
                # Truncate long filenames
                display_name = display_name[:26] + "..."

            file_button = ctk.CTkButton(
                self.recent_scrollable,
                text=display_name,
                command=lambda fp=file_path: self._open_recent_file(fp),
                height=30,
            )
            file_button.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            self.recent_file_buttons.append(file_button)

            # Add tooltip with full path
            self._create_tooltip(file_button, str(file_path))

            # Update compatibility listbox
            self.recent_listbox.insert(i, display_name)

        self.logger.debug(f"Updated {len(self.recent_file_buttons)} recent files")

    def _create_tooltip(self, widget, text):
        """Create a proper tooltip widget for a widget.

        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text
        """
        # Create tooltip label
        tooltip = ctk.CTkLabel(
            widget,
            text=text,
            fg_color=("gray90", "gray20"),
            text_color=("black", "white"),
            corner_radius=5,
            padx=8,
            pady=4,
        )

        # Position tooltip above the widget
        def show_tooltip(event):
            try:
                # Get widget position
                x = widget.winfo_rootx() + widget.winfo_width() // 2
                y = widget.winfo_rooty() - 30

                # Calculate position to center tooltip
                tooltip.update_idletasks()
                tooltip_width = tooltip.winfo_reqwidth()
                x -= tooltip_width // 2

                # Place tooltip
                tooltip.place(x=x - widget.winfo_rootx(), y=-30)
                tooltip.lift()  # Bring to front

            except Exception as e:
                self.logger.debug(f"Error showing tooltip: {e}")

        def hide_tooltip(event):
            try:
                tooltip.place_forget()
            except:
                pass

        # Bind events
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

        # Also update status bar for additional feedback
        def on_enter(event):
            self.app.update_status(f"File: {text}")

        def on_leave(event):
            self.app.update_status("Ready")

        widget.bind("<Enter>", on_enter, add="+")
        widget.bind("<Leave>", on_leave, add="+")

    def _open_recent_file(self, file_path):
        """Open a recent file.

        Args:
            file_path: Path to the file to open
        """
        self.logger.info(f"Opening recent file: {file_path}")
        self.app.open_file(file_path)

    def cleanup_on_exit(self):
        """Clean up resources and save preferences on application exit."""
        try:
            # Recent files are already handled by the main app (_save_recent_files)
            # No need to duplicate here to avoid inconsistency

            # Stop file monitoring
            self.stop_file_monitoring()

            # Clean up file timestamps
            with self.file_lock:
                self.file_timestamps.clear()

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def start_file_monitoring(self):
        """Start monitoring recent files for external changes."""
        if not self.file_monitor_active:
            self.file_monitor_active = True
            self.file_monitor_future = self.thread_manager.submit_with_callback(
                fn=self._monitor_files, error_callback=self._handle_monitor_error
            )

    def stop_file_monitoring(self):
        """Stop file monitoring."""
        self.file_monitor_active = False
        if self.file_monitor_future and not self.file_monitor_future.done():
            self.file_monitor_future.cancel()

    def _handle_monitor_error(self, error):
        """Handle file monitoring errors."""
        self.logger.error(f"File monitoring error: {error}")

    def _monitor_files(self):
        """Monitor files for external changes using thread manager."""
        while self.file_monitor_active:
            try:
                self._check_file_changes()
                import time

                time.sleep(self.monitor_interval)
            except (OSError, PermissionError, RuntimeError) as e:
                # Log specific errors but continue monitoring
                self.logger.warning(f"File monitoring error: {e}")
                import time

                time.sleep(self.monitor_interval)
            except Exception as e:
                # Log unexpected errors with full traceback
                self.logger.warning(
                    f"Unexpected file monitoring error: {e}", exc_info=True
                )
                import time

                time.sleep(self.monitor_interval)

    def _check_file_changes(self):
        """Check for file changes and update UI if needed."""
        changes_detected = False

        # Thread-safe access to file_timestamps
        with self.file_lock:
            timestamps_copy = self.file_timestamps.copy()

        for file_path_str, old_timestamp in timestamps_copy.items():
            file_path = Path(file_path_str)

            try:
                if file_path.exists():
                    new_timestamp = file_path.stat().st_mtime
                    if new_timestamp > old_timestamp:
                        # File has been modified externally
                        changes_detected = True

                        # Thread-safe update of timestamp
                        with self.file_lock:
                            self.file_timestamps[file_path_str] = new_timestamp

                        # Update UI in main thread
                        self.after(0, lambda: self._handle_file_change(file_path))
                else:
                    # File was deleted - remove from timestamps
                    changes_detected = True
                    # Thread-safe removal of deleted file
                    with self.file_lock:
                        self.file_timestamps.pop(file_path_str, None)
                    self.after(0, lambda: self._handle_file_deleted(file_path))

            except (OSError, PermissionError) as e:
                # File might be inaccessible - remove from monitoring
                self.logger.warning(f"File monitoring error for {file_path_str}: {e}")
                with self.file_lock:
                    self.file_timestamps.pop(file_path_str, None)
                continue

        # Periodic cleanup: remove entries for files that no longer exist
        if len(self.file_timestamps) > 100:  # Only cleanup if dict is getting large
            self._cleanup_file_timestamps()

        return changes_detected

    def _cleanup_file_timestamps(self):
        """Clean up file timestamps dict by removing entries for non-existent files."""
        try:
            with self.file_lock:
                # Keep only entries for files that still exist
                valid_timestamps = {
                    path: mtime
                    for path, mtime in self.file_timestamps.items()
                    if Path(path).exists()
                }

                removed_count = len(self.file_timestamps) - len(valid_timestamps)
                self.file_timestamps = valid_timestamps

                if removed_count > 0:
                    self.logger.debug(
                        f"Cleaned up {removed_count} stale file timestamp entries"
                    )

        except Exception as e:
            self.logger.error(f"Error during file timestamps cleanup: {e}")

    def _handle_file_change(self, file_path: Path):
        """Handle external file change.

        Args:
            file_path: Path to the changed file
        """
        # Check if this is the currently open file
        if hasattr(self.app, "current_file") and self.app.current_file == file_path:
            # Show notification to user
            self.app.update_status(
                f"File '{file_path.name}' was modified externally", level="warning"
            )

            # Update file timestamp
            try:
                with self.file_lock:
                    self.file_timestamps[str(file_path)] = file_path.stat().st_mtime
            except (OSError, PermissionError):
                pass

    def _handle_file_deleted(self, file_path: Path):
        """Handle external file deletion.

        Args:
            file_path: Path to the deleted file
        """
        try:
            # Remove from timestamps
            with self.file_lock:
                self.file_timestamps.pop(str(file_path), None)

            # Remove from recent files if it was deleted
            if file_path in self.app.recent_files:
                self.app.recent_files.remove(file_path)
                self.app.config.save()
                self.update_recent_files()

            # Update status
            self.app.update_status(f"File deleted: {file_path.name}", "info")
        except KeyError:
            # File not in timestamps - this is fine
            pass
        except Exception as e:
            self.logger.error(f"Error handling file deletion: {e}")

    def refresh(self):
        """Refresh the sidebar content."""
        self.update_recent_files()

    def _create_compatibility_listbox(self):
        """Create a compatibility listbox for tests.

        Returns:
            Mock listbox object that provides the interface expected by tests
        """

        class CompatibilityListbox:
            """Mock listbox that provides the interface expected by tests."""

            def __init__(self, sidebar):
                self.sidebar = sidebar
                self._items = []

            def size(self):
                """Return the number of items."""
                return len(self._items)

            def get(self, index):
                """Get item at index."""
                if 0 <= index < len(self._items):
                    return self._items[index]
                return ""

            def insert(self, index, item):
                """Insert item at index."""
                self._items.insert(index, item)

            def delete(self, start, end=None):
                """Delete items from start to end."""
                if end is None:
                    end = start + 1
                del self._items[start:end]

            def clear(self):
                """Clear all items."""
                self._items.clear()

            def curselection(self):
                """Return current selection (empty for mock)."""
                return ()

        return CompatibilityListbox(self)

    def __del__(self):
        """Cleanup when sidebar is destroyed."""
        self.stop_file_monitoring()
