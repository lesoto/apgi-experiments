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
        
        # File monitoring
        self.file_monitor_active = False
        self.file_monitor_thread = None
        self.file_timestamps: Dict[str, float] = {}
        self.monitor_interval = 2.0  # Check every 2 seconds
        
        self.setup_ui()
        self.start_file_monitoring()
    
    def setup_ui(self):
        """Set up the sidebar UI components."""
        self.logger.debug("Setting up sidebar UI")
        
        # Configure frame
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="APGI Framework",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation Section
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        nav_frame.grid_columnconfigure(0, weight=1)
        
        nav_label = ctk.CTkLabel(
            nav_frame,
            text="Navigation",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        nav_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        # Navigation buttons
        self.new_btn = ctk.CTkButton(
            nav_frame,
            text="New Configuration",
            command=self.app.new_file,
            height=40
        )
        self.new_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.open_btn = ctk.CTkButton(
            nav_frame,
            text="Open File",
            command=self.app.open_file,
            height=40
        )
        self.open_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.save_btn = ctk.CTkButton(
            nav_frame,
            text="Save File",
            command=self.app.save_file,
            height=40
        )
        self.save_btn.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Tools Section
        tools_frame = ctk.CTkFrame(self)
        tools_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        tools_frame.grid_columnconfigure(0, weight=1)
        
        tools_label = ctk.CTkLabel(
            tools_frame,
            text="Tools",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        tools_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        # Tool buttons
        self.undo_btn = ctk.CTkButton(
            tools_frame,
            text="Undo",
            command=self.app.undo,
            height=40
        )
        self.undo_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.redo_btn = ctk.CTkButton(
            tools_frame,
            text="Redo",
            command=self.app.redo,
            height=40
        )
        self.redo_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.theme_btn = ctk.CTkButton(
            tools_frame,
            text="Toggle Theme",
            command=self.app.toggle_theme,
            height=40
        )
        self.theme_btn.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Recent Files Section
        recent_frame = ctk.CTkFrame(self)
        recent_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        recent_frame.grid_columnconfigure(0, weight=1)
        recent_frame.grid_rowconfigure(1, weight=1)
        
        recent_label = ctk.CTkLabel(
            recent_frame,
            text="Recent Files",
            font=ctk.CTkFont(size=16, weight="bold")
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
            help_frame,
            text="Help (F1)",
            command=self.app.show_help,
            height=40
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
        self.file_timestamps.clear()
        
        # Create buttons for each recent file
        for i, file_path in enumerate(self.app.recent_files):
            # Store timestamp for monitoring
            try:
                if file_path.exists():
                    self.file_timestamps[str(file_path)] = file_path.stat().st_mtime
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
                height=30
            )
            file_button.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            self.recent_file_buttons.append(file_button)
            
            # Add tooltip with full path
            self._create_tooltip(file_button, str(file_path))
            
            # Update compatibility listbox
            self.recent_listbox.insert(i, display_name)
        
        self.logger.debug(f"Updated {len(self.recent_file_buttons)} recent files")
    
    def _create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget.
        
        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text
        """
        def on_enter(event):
            # Update status bar with full path
            self.app.update_status(f"File: {text}")
        
        def on_leave(event):
            # Clear status
            self.app.update_status("Ready")
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _open_recent_file(self, file_path):
        """Open a recent file.
        
        Args:
            file_path: Path to the file to open
        """
        self.logger.info(f"Opening recent file: {file_path}")
        self.app.open_file(file_path)
    
    def start_file_monitoring(self):
        """Start monitoring recent files for external changes."""
        if not self.file_monitor_active:
            self.file_monitor_active = True
            self.file_monitor_thread = threading.Thread(
                target=self._monitor_files,
                daemon=True
            )
            self.file_monitor_thread.start()
    
    def stop_file_monitoring(self):
        """Stop file monitoring."""
        self.file_monitor_active = False
        if self.file_monitor_thread:
            self.file_monitor_thread.join(timeout=1.0)
    
    def _monitor_files(self):
        """Monitor files for external changes in a separate thread."""
        while self.file_monitor_active:
            try:
                self._check_file_changes()
                time.sleep(self.monitor_interval)
            except Exception as e:
                # Log error but continue monitoring
                print(f"File monitoring error: {e}")
                time.sleep(self.monitor_interval)
    
    def _check_file_changes(self):
        """Check for file changes and update UI if needed."""
        changes_detected = False
        
        for file_path_str, old_timestamp in self.file_timestamps.items():
            file_path = Path(file_path_str)
            
            try:
                if file_path.exists():
                    new_timestamp = file_path.stat().st_mtime
                    if new_timestamp > old_timestamp:
                        # File has been modified externally
                        changes_detected = True
                        self.file_timestamps[file_path_str] = new_timestamp
                        
                        # Update UI in main thread
                        self.after(0, lambda: self._handle_file_change(file_path))
                else:
                    # File was deleted
                    changes_detected = True
                    self.after(0, lambda: self._handle_file_deleted(file_path))
                    
            except (OSError, PermissionError):
                # File might be inaccessible
                continue
        
        return changes_detected
    
    def _handle_file_change(self, file_path: Path):
        """Handle external file change.
        
        Args:
            file_path: Path to the changed file
        """
        # Check if this is the currently open file
        if hasattr(self.app, 'current_file') and self.app.current_file == file_path:
            # Show notification to user
            self.app.update_status(
                f"File '{file_path.name}' was modified externally",
                color="warning"
            )
            
            # Update file timestamp
            try:
                self.file_timestamps[str(file_path)] = file_path.stat().st_mtime
            except (OSError, PermissionError):
                pass
    
    def _handle_file_deleted(self, file_path: Path):
        """Handle external file deletion.
        
        Args:
            file_path: Path to the deleted file
        """
        # Remove from timestamps
        self.file_timestamps.pop(str(file_path), None)
        
        # Remove from recent files if it was deleted
        if file_path in self.app.recent_files:
            self.app.recent_files.remove(file_path)
            self.app.config.save()
            self.update_recent_files()
            
            # Update status
            self.app.update_status(
                f"File '{file_path.name}' was deleted",
                color="warning"
            )
    
    def on_recent_select(self, event):
        """Handle recent file selection (legacy method for compatibility).
        
        Args:
            event: Listbox selection event (no longer used)
        """
        # This method is kept for compatibility but no longer used
        # since we replaced the Listbox with CustomTkinter buttons
        pass
    
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
