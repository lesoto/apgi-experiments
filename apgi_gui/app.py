"""Main application module for APGI Framework GUI."""

import os
import json
import logging
import tkinter as tk
from pathlib import Path
from typing import Dict, Any, Optional, List
import customtkinter as ctk
from datetime import datetime

# Import custom components - handle both relative and absolute imports
try:
    from .components.sidebar import Sidebar
    from .components.main_area import MainArea
    from .components.status_bar import StatusBar
    from .utils.logger import setup_logging
    from .utils.config import AppConfig
except ImportError:
    # Fallback to absolute imports when run directly
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from apgi_gui.components.sidebar import Sidebar
    from apgi_gui.components.main_area import MainArea
    from apgi_gui.components.status_bar import StatusBar
    from apgi_gui.utils.logger import setup_logging
    from apgi_gui.utils.config import AppConfig


class APGIFrameworkApp(ctk.CTk):
    """Main application class for APGI Framework GUI."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        # Initialize application state
        self.title("APGI Framework GUI")
        self.geometry("1800x1000+50+50")
        self.minsize(1200, 800)

        # Initialize configuration
        self.config = AppConfig()

        # Set appearance
        ctk.set_appearance_mode(self.config.theme)
        ctk.set_default_color_theme("blue")

        # Initialize application data
        self.current_file: Optional[Path] = None
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self.recent_files: List[Path] = []

        # Setup logging
        self.logger = setup_logging("apgi_gui", self.config.log_dir)
        self.logger.info("APGI Framework GUI started")

        # Setup UI
        self._setup_ui()
        self._setup_keyboard_shortcuts()

        # Load recent files
        self._load_recent_files()

        # Center window on screen
        self._center_window()

    def _setup_ui(self) -> None:
        """Set up the main user interface."""
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create main containers
        self.sidebar = Sidebar(self, self)
        self.main_area = MainArea(self, self)
        self.status_bar = StatusBar(self, self)

        # Layout
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.status_bar.grid(row=1, column=1, sticky="ew")

    def _setup_keyboard_shortcuts(self) -> None:
        """Set up comprehensive keyboard shortcuts."""
        # File operations
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_file_as())
        self.bind("<Control-Shift-s>", lambda e: self.save_file_as())
        self.bind("<Control-w>", lambda e: self.close_file())
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<Control-Shift-q>", lambda e: self.quit())  # Force quit

        # Edit operations
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-Shift-z>", lambda e: self.redo())  # Alternative redo
        self.bind("<Control-y>", lambda e: self.redo())
        self.bind("<Control-a>", lambda e: self.select_all())
        self.bind("<Control-c>", lambda e: self.copy())
        self.bind("<Control-v>", lambda e: self.paste())
        self.bind("<Control-x>", lambda e: self.cut())

        # View operations
        self.bind("<F1>", lambda e: self.show_help())
        self.bind("<Control-h>", lambda e: self.show_help())
        self.bind("<Control-t>", lambda e: self.toggle_theme())
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<Control-0>", lambda e: self.reset_zoom())
        self.bind("<Control-plus>", lambda e: self.zoom_in())
        self.bind("<Control-minus>", lambda e: self.zoom_out())

        # Navigation
        self.bind("<Control-1>", lambda e: self.switch_to_tab("Configuration"))
        self.bind("<Control-2>", lambda e: self.switch_to_tab("Analysis"))
        self.bind("<Control-3>", lambda e: self.switch_to_tab("Visualization"))
        self.bind("<Control-4>", lambda e: self.switch_to_tab("Results"))
        self.bind("<Control-Tab>", lambda e: self.next_tab())
        self.bind("<Control-Shift-Tab>", lambda e: self.previous_tab())

        # Application operations
        self.bind("<Control-r>", lambda e: self.run_analysis())
        self.bind("<F5>", lambda e: self.refresh())
        self.bind("<Control-f>", lambda e: self.find())
        self.bind("<Control-g>", lambda e: self.find_next())
        self.bind("<Control-Shift-g>", lambda e: self.find_previous())

        # Debug/Development shortcuts
        self.bind("<Control-d>", lambda e: self.toggle_debug_mode())
        self.bind("<Control-l>", lambda e: self.show_log())
        self.bind("<Control-p>", lambda e: self.show_preferences())

        # Window management
        self.bind("<Alt-F4>", lambda e: self.quit())
        self.bind("<Control-m>", lambda e: self.minimize_window())
        self.bind("<Control-Shift-M>", lambda e: self.maximize_window())

    def _center_window(self) -> None:
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _load_recent_files(self) -> None:
        """Load the list of recently opened files."""
        try:
            if self.config.recent_files_path.exists():
                with open(self.config.recent_files_path, "r") as f:
                    recent_files = json.load(f)
                    self.recent_files = [
                        Path(f) for f in recent_files if Path(f).exists()
                    ]
        except Exception as e:
            self.logger.error(f"Error loading recent files: {e}")

    def _save_recent_files(self) -> None:
        """Save the list of recently opened files."""
        try:
            with open(self.config.recent_files_path, "w") as f:
                json.dump([str(f) for f in self.recent_files], f)
        except Exception as e:
            self.logger.error(f"Error saving recent files: {e}")

    def update_status(self, message: str, level: str = "info") -> None:
        """Update the status bar with a message.

        Args:
            message: The message to display
            level: The message level (info, warning, error)
        """
        self.status_bar.set_status(message, level)

        # Log the message
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(message)

    def new_file(self) -> None:
        """Create a new file."""
        self.current_file = None
        self.main_area.clear()
        self.update_status("New file created")

    def open_file(self, file_path: Optional[Path] = None) -> None:
        """Open a file.

        Args:
            file_path: Path to the file to open. If None, shows a file dialog.
        """
        if file_path is None:
            file_path = tk.filedialog.askopenfilename(
                title="Open APGI Configuration",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                initialdir=self.config.data_dir,
            )
            if not file_path:
                return
            file_path = Path(file_path)

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            self.current_file = file_path
            self.main_area.load_data(data)

            # Add to recent files
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
            self.recent_files.insert(0, file_path)
            self.recent_files = self.recent_files[:10]  # Keep only 10 most recent
            self._save_recent_files()

            self.update_status(f"Opened {file_path.name}")

        except Exception as e:
            self.update_status(f"Error opening file: {e}", "error")

    def save_file(self) -> None:
        """Save the current file."""
        if self.current_file is None:
            self.save_file_as()
        else:
            self._save_to_file(self.current_file)

    def save_file_as(self) -> None:
        """Save the current file with a new name."""
        file_path = tk.filedialog.asksaveasfilename(
            title="Save APGI Configuration",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialdir=self.config.data_dir,
        )

        if not file_path:
            return

        file_path = Path(file_path)
        self._save_to_file(file_path)
        self.current_file = file_path

    def _save_to_file(self, file_path: Path) -> None:
        """Save data to a file.

        Args:
            file_path: Path to save the file to
        """
        try:
            data = self.main_area.get_data()
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)

            self.update_status(f"Saved to {file_path.name}")

            # Add to recent files if not already there
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
            self.recent_files.insert(0, file_path)
            self.recent_files = self.recent_files[:10]  # Keep only 10 most recent
            self._save_recent_files()

        except Exception as e:
            self.update_status(f"Error saving file: {e}", "error")

    def undo(self) -> None:
        """Undo the last action."""
        if self.undo_stack:
            self.redo_stack.append(self.main_area.get_data())
            self.main_area.load_data(self.undo_stack.pop())
            self.update_status("Undo successful")
        else:
            self.update_status("Nothing to undo", "warning")

    def redo(self) -> None:
        """Redo the last undone action."""
        if self.redo_stack:
            self.undo_stack.append(self.main_area.get_data())
            self.main_area.load_data(self.redo_stack.pop())
            self.update_status("Redo successful")
        else:
            self.update_status("Nothing to redo", "warning")

    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        if self.config.theme == "dark":
            self.config.theme = "light"
            ctk.set_appearance_mode("light")
            self.update_status("Switched to light theme")
        else:
            self.config.theme = "dark"
            ctk.set_appearance_mode("dark")
            self.update_status("Switched to dark theme")

        # Save the theme preference
        self.config.save()

    def show_help(self) -> None:
        """Show the help dialog."""
        help_text = """APGI Framework GUI Help

Keyboard Shortcuts:
  File Operations:
    Ctrl+N           - New file
    Ctrl+O           - Open file
    Ctrl+S           - Save file
    Ctrl+Shift+S     - Save file as
    Ctrl+W           - Close file
    Ctrl+Q           - Quit application
    
  Edit Operations:
    Ctrl+Z           - Undo
    Ctrl+Y           - Redo
    Ctrl+Shift+Z     - Redo (alternative)
    Ctrl+A           - Select all
    Ctrl+C           - Copy
    Ctrl+V           - Paste
    Ctrl+X           - Cut
    
  View Operations:
    Ctrl+T           - Toggle theme
    F11              - Toggle fullscreen
    Ctrl+0           - Reset zoom
    Ctrl+Plus        - Zoom in
    Ctrl+Minus       - Zoom out
    
  Navigation:
    Ctrl+1           - Configuration tab
    Ctrl+2           - Analysis tab
    Ctrl+3           - Visualization tab
    Ctrl+4           - Results tab
    Ctrl+Tab         - Next tab
    Ctrl+Shift+Tab   - Previous tab
    
  Application:
    Ctrl+R           - Run analysis
    F5               - Refresh
    Ctrl+F           - Find
    Ctrl+G           - Find next
    Ctrl+Shift+G     - Find previous
    F1               - Show help
    Ctrl+H           - Show help (alternative)
    
  Debug/Development:
    Ctrl+D           - Toggle debug mode
    Ctrl+L           - Show log
    Ctrl+P           - Show preferences
    
  Window Management:
    Alt+F4           - Quit application
    Ctrl+M           - Minimize window
    Ctrl+Shift+M     - Maximize window

For more information, visit the project documentation."""

        # Create help dialog
        help_dialog = ctk.CTkToplevel(self)
        help_dialog.title("Help - APGI Framework GUI")
        help_dialog.geometry("600x500")
        help_dialog.transient(self)
        help_dialog.grab_set()

        # Create scrollable text widget
        help_text_widget = ctk.CTkTextbox(help_dialog)
        help_text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        help_text_widget.insert("1.0", help_text)
        help_text_widget.configure(state="disabled")

        # Close button
        close_button = ctk.CTkButton(
            help_dialog, text="Close", command=help_dialog.destroy
        )
        close_button.pack(pady=10)

    # Additional methods for new keyboard shortcuts
    def close_file(self) -> None:
        """Close the current file."""
        if self.current_file:
            # Save current state to undo stack
            self.undo_stack.append(self.main_area.get_data())
            self.current_file = None
            self.main_area.clear()
            self.status_bar.set_file(None)
            self.update_status("File closed")
        else:
            self.update_status("No file to close", "warning")

    def select_all(self) -> None:
        """Select all content in the current focused widget."""
        try:
            focused = self.focus_get()
            if hasattr(focused, "tag_add"):
                focused.tag_add("sel", "1.0", "end")
                focused.mark_set("insert", "1.0")
                focused.see("insert")
        except:
            pass

    def copy(self) -> None:
        """Copy selected content."""
        try:
            focused = self.focus_get()
            if hasattr(focused, "selection_get"):
                self.clipboard_clear()
                self.clipboard_append(focused.selection_get())
                self.update_status("Copied to clipboard")
        except:
            self.update_status("Nothing to copy", "warning")

    def paste(self) -> None:
        """Paste content from clipboard."""
        try:
            focused = self.focus_get()
            if hasattr(focused, "insert"):
                clipboard_content = self.clipboard_get()
                focused.insert("insert", clipboard_content)
                self.update_status("Pasted from clipboard")
        except:
            self.update_status("Nothing to paste", "warning")

    def cut(self) -> None:
        """Cut selected content."""
        try:
            focused = self.focus_get()
            if hasattr(focused, "selection_get") and hasattr(focused, "delete"):
                clipboard_content = focused.selection_get()
                self.clipboard_clear()
                self.clipboard_append(clipboard_content)
                focused.delete("sel.first", "sel.last")
                self.update_status("Cut to clipboard")
        except:
            self.update_status("Nothing to cut", "warning")

    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        current_state = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not current_state)
        self.update_status(
            f"Fullscreen {'enabled' if not current_state else 'disabled'}"
        )

    def reset_zoom(self) -> None:
        """Reset zoom to default."""
        # Placeholder for zoom functionality
        self.update_status("Zoom reset to 100%")

    def zoom_in(self) -> None:
        """Zoom in."""
        # Placeholder for zoom functionality
        self.update_status("Zoomed in")

    def zoom_out(self) -> None:
        """Zoom out."""
        # Placeholder for zoom functionality
        self.update_status("Zoomed out")

    def switch_to_tab(self, tab_name: str) -> None:
        """Switch to a specific tab."""
        try:
            self.main_area.tabview.set(tab_name)
            self.update_status(f"Switched to {tab_name} tab")
        except:
            self.update_status(f"Failed to switch to {tab_name} tab", "error")

    def next_tab(self) -> None:
        """Switch to the next tab."""
        try:
            current = self.main_area.tabview.get()
            tabs = ["Configuration", "Analysis", "Visualization", "Results"]
            current_index = tabs.index(current) if current in tabs else 0
            next_index = (current_index + 1) % len(tabs)
            self.switch_to_tab(tabs[next_index])
        except:
            pass

    def previous_tab(self) -> None:
        """Switch to the previous tab."""
        try:
            current = self.main_area.tabview.get()
            tabs = ["Configuration", "Analysis", "Visualization", "Results"]
            current_index = tabs.index(current) if current in tabs else 0
            prev_index = (current_index - 1) % len(tabs)
            self.switch_to_tab(tabs[prev_index])
        except:
            pass

    def run_analysis(self) -> None:
        """Run the current analysis."""
        self.main_area.run_analysis()

    def refresh(self) -> None:
        """Refresh the current view."""
        self.sidebar.refresh()
        self.update_status("Refreshed")

    def find(self) -> None:
        """Open find dialog."""
        # Placeholder for find functionality
        self.update_status("Find functionality not yet implemented")

    def find_next(self) -> None:
        """Find next occurrence."""
        # Placeholder for find functionality
        self.update_status("Find next not yet implemented")

    def find_previous(self) -> None:
        """Find previous occurrence."""
        # Placeholder for find functionality
        self.update_status("Find previous not yet implemented")

    def toggle_debug_mode(self) -> None:
        """Toggle debug mode."""
        # Placeholder for debug functionality
        self.update_status("Debug mode toggled")

    def show_log(self) -> None:
        """Show application log."""
        # Placeholder for log viewer
        self.update_status("Log viewer not yet implemented")

    def show_preferences(self) -> None:
        """Show preferences dialog."""
        # Placeholder for preferences
        self.update_status("Preferences not yet implemented")

    def minimize_window(self) -> None:
        """Minimize the window."""
        self.iconify()
        self.update_status("Window minimized")

    def maximize_window(self) -> None:
        """Maximize the window."""
        self.state("zoomed")
        self.update_status("Window maximized")

    def run(self) -> None:
        """Run the application."""
        self.mainloop()


if __name__ == "__main__":
    app = APGIFrameworkApp()
    app.run()
