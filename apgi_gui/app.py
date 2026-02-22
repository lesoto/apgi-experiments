"""Main application module for APGI Framework GUI."""

import json
import logging
import tkinter as tk
from collections import deque
from pathlib import Path
from tkinter import TclError
from typing import List, Optional

# Import customtkinter for theme support (optional)
try:
    import customtkinter as ctk

    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None
    print("Warning: CustomTkinter not available. Using basic tkinter fallback.")

# Import custom components - handle both relative and absolute imports
try:
    from .components.main_area import MainArea
    from .components.sidebar import Sidebar
    from .components.status_bar import StatusBar
    from .utils.config import AppConfig
    from .utils.logger import setup_logging
except ImportError:
    # Fallback to absolute imports when run directly
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    from apgi_gui.components.main_area import MainArea
    from apgi_gui.components.sidebar import Sidebar
    from apgi_gui.components.status_bar import StatusBar
    from apgi_gui.utils.config import AppConfig
    from apgi_gui.utils.logger import setup_logging


class APGIFrameworkApp(ctk.CTk if CUSTOMTKINTER_AVAILABLE else tk.Tk):
    """Main application class for APGI Framework GUI."""

    def __init__(self):
        """Initialize the application."""
        if not CUSTOMTKINTER_AVAILABLE:
            tk.messagebox.showerror(
                "Missing Dependency",
                "CustomTkinter is required for this application.\n"
                "Please install it with: pip install customtkinter",
            )
            sys.exit(1)

        super().__init__()

        # Initialize application state
        self.title("APGI Framework GUI")

        # Initialize logging
        self.logger = logging.getLogger(__name__)

        # Widget tracking for theme and zoom updates
        self._tracked_widgets = set()
        self._text_widgets = set()

        # Zoom functionality
        self.zoom_level = 1.0  # 100% zoom level
        self.min_zoom = 0.5  # 50% minimum
        self.max_zoom = 2.0  # 200% maximum
        self.zoom_step = 0.1  # 10% step

        # Initialize configuration
        self.config = AppConfig()

        # Adaptive window sizing based on screen resolution
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = min(
            int(screen_width * 0.8), 1800
        )  # Cap at 1800 for large screens
        window_height = min(
            int(screen_height * 0.8), 1000
        )  # Cap at 1000 for large screens

        # Center window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(min(window_width, 1200), min(window_height, 800))

        # Set appearance
        ctk.set_appearance_mode(self.config.theme)
        ctk.set_default_color_theme("blue")

        # Initialize application data
        self.current_file: Optional[Path] = None
        MAX_UNDO_SIZE = self.config.max_undo_size  # Use configurable limit
        self.undo_stack: deque = deque(maxlen=MAX_UNDO_SIZE)
        self.redo_stack: deque = deque(maxlen=MAX_UNDO_SIZE)
        self.recent_files: List[Path] = []

        # Memory monitoring for undo/redo
        self._undo_memory_usage = 0  # Track memory usage in bytes for undo stack
        self._redo_memory_usage = 0  # Track memory usage in bytes for redo stack
        self._undo_memory_limit = (
            self.config.undo_memory_limit_mb * 1024 * 1024
        )  # Convert MB to bytes

        # Widget tracking for theme and zoom updates
        self._tracked_widgets = set()
        self._text_widgets = set()

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

        # Bind close event to save recent files
        self.protocol("WM_DELETE_WINDOW", self.on_close)

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

    def on_close(self) -> None:
        """Handle application close event."""
        self._save_recent_files()
        self.quit()

    def update_status(self, message: str, level: str = "info") -> None:
        """Update the status bar with a message.

        Args:
            message: The message to display
            level: The message level (info, warning, error)
        """
        self.after(0, lambda: self.status_bar.set_status(message, level))

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
            # Validate file path
            if not file_path.exists():
                self.update_status(f"Error [file not found]: {file_path.name}", "error")
                return
            if not file_path.is_file():
                self.update_status(f"Error [not a file]: {file_path.name}", "error")
                return

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

            # Update sidebar recent files display
            if hasattr(self, "sidebar"):
                self.sidebar.update_recent_files()

            self.update_status(f"Opened {file_path.name}")

        except (OSError, PermissionError, RuntimeError) as e:
            # Log specific errors but continue monitoring
            self.logger.error(f"Error [file monitoring]: {e}")
        except Exception as e:
            # Log unexpected errors with full traceback
            self.logger.error(f"Error [unexpected file monitoring]: {e}", exc_info=True)
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

            # Update sidebar recent files display
            if hasattr(self, "sidebar"):
                self.sidebar.update_recent_files()

        except Exception as e:
            self.update_status(f"Error saving file: {e}", "error")

    def _get_object_size(self, obj) -> int:
        """Get approximate memory size of an object."""
        try:
            import sys

            return sys.getsizeof(obj)
        except Exception:
            return 1024  # Fallback estimate

    def _add_to_undo_stack(self, data):
        """Add data to undo stack with memory monitoring."""
        data_size = self._get_object_size(data)

        # Check if adding this would exceed memory limit for undo stack
        while (
            self.undo_stack
            and self._undo_memory_usage + data_size > self._undo_memory_limit
        ):
            oldest = self.undo_stack.popleft()
            self._undo_memory_usage -= self._get_object_size(oldest)
            self.logger.debug("Removed old undo entry due to memory limit")

        # Add new item to undo stack
        self.undo_stack.append(data)
        self._undo_memory_usage += data_size

        # Clear redo stack when new action is performed
        self.redo_stack.clear()
        self._redo_memory_usage = 0

    def undo(self) -> None:
        """Undo the last action with memory monitoring."""
        if self.undo_stack:
            current_data = self.main_area.get_data()
            current_size = self._get_object_size(current_data)

            # Add current state to redo stack
            if self._redo_memory_usage + current_size <= self._undo_memory_limit:
                self.redo_stack.append(current_data)
                self._redo_memory_usage += current_size

            # Get and remove from undo stack
            undo_data = self.undo_stack.pop()
            undo_size = self._get_object_size(undo_data)
            self._undo_memory_usage -= undo_size

            # Apply undo
            self.main_area.load_data(undo_data)
            self.update_status("Undo successful")
        else:
            self.update_status("Nothing to undo", "warning")

    def redo(self) -> None:
        """Redo the last undone action with memory monitoring."""
        if self.redo_stack:
            current_data = self.main_area.get_data()
            current_size = self._get_object_size(current_data)

            # Add current state back to undo stack
            if self._undo_memory_usage + current_size <= self._undo_memory_limit:
                self.undo_stack.append(current_data)
                self._undo_memory_usage += current_size

            # Get and remove from redo stack
            redo_data = self.redo_stack.pop()
            redo_size = self._get_object_size(redo_data)
            self._redo_memory_usage -= redo_size

            # Apply redo
            self.main_area.load_data(redo_data)
            self.update_status("Redo successful")
        else:
            self.update_status("Nothing to redo", "warning")

    def get_undo_memory_usage_mb(self) -> float:
        """Get current undo/redo stack memory usage in MB."""
        return (self._undo_memory_usage + self._redo_memory_usage) / (1024 * 1024)

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

        # Propagate theme changes to all components
        self._propagate_theme_to_components()

    def _propagate_theme_to_components(self) -> None:
        """Propagate current theme to all UI components comprehensively."""
        try:
            # Force theme update on CustomTkinter level
            ctk.set_appearance_mode(self.config.theme)

            # Update all widgets recursively from the root to ensure comprehensive coverage
            self._update_widget_theme_recursive(self)

            # Force UI refresh
            self.update_idletasks()
            self.after(100, self._force_theme_refresh)

        except Exception as e:
            self.logger.error(f"Error propagating theme: {e}")

    def _update_widget_theme_recursive(self, widget) -> None:
        """Recursively update theme for a widget and all its children."""
        try:
            # Track this widget for future updates
            self._tracked_widgets.add(widget)

            # Check if it's a text widget for zoom tracking
            if hasattr(widget, "cget") and "font" in widget.keys():
                self._text_widgets.add(widget)

            # Update the widget itself
            if hasattr(widget, "configure"):
                try:
                    # Force widget to redraw with new theme
                    widget.update()
                except Exception as e:
                    self.logger.debug(f"Error updating widget theme: {e}")

            # Recursively update all child widgets
            for child in widget.winfo_children():
                self._update_widget_theme_recursive(child)

        except Exception as e:
            self.logger.debug(f"Error updating widget theme: {e}")

    def _update_all_tracked_widgets(self) -> None:
        """Update all tracked widgets with current theme."""
        for widget in list(self._tracked_widgets):
            try:
                if widget.winfo_exists():
                    widget.update()
                else:
                    # Remove widgets that no longer exist
                    self._tracked_widgets.discard(widget)
                    self._text_widgets.discard(widget)
            except Exception:
                # Remove problematic widgets
                self._text_widgets.discard(widget)
                self._tracked_widgets.discard(widget)

    def _force_theme_refresh(self) -> None:
        """Force a complete theme refresh after a delay."""
        try:
            self.update()
            self.update_idletasks()
        except Exception as e:
            self.logger.debug(f"Error in force theme refresh: {e}")

    def track_widget(self, widget) -> None:
        """Add a widget to the tracking list for theme and zoom updates."""
        if widget:
            self._tracked_widgets.add(widget)
            if hasattr(widget, "cget") and "font" in widget.keys():
                self._text_widgets.add(widget)

    def show_help(self) -> None:
        """Show context-sensitive help dialog."""
        try:
            # Get current context
            current_tab = self._get_current_tab()
            focused_widget = self._get_focused_widget_info()

            # Generate context-specific help content
            help_content = self._generate_context_help(current_tab, focused_widget)

            # Create help dialog
            help_dialog = ctk.CTkToplevel(self)
            help_dialog.title(f"Help - {current_tab} Tab")
            help_dialog.geometry("700x600")
            help_dialog.transient(self)
            help_dialog.grab_set()

            # Create scrollable text widget
            help_text_widget = ctk.CTkTextbox(help_dialog, wrap="word")
            help_text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            help_text_widget.insert("1.0", help_content)
            help_text_widget.configure(state="disabled")

            # Button frame
            button_frame = ctk.CTkFrame(help_dialog)
            button_frame.pack(fill="x", padx=10, pady=10)

            # General help button
            general_btn = ctk.CTkButton(
                button_frame,
                text="General Help",
                command=lambda: self._show_general_help(help_text_widget),
            )
            general_btn.pack(side="left", padx=5)

            # Close button
            close_button = ctk.CTkButton(
                button_frame, text="Close", command=help_dialog.destroy
            )
            close_button.pack(side="right", padx=5)

        except Exception as e:
            self.logger.error(f"Error opening context help: {e}")
            self.update_status("Error opening help", "error")
            # Fallback to general help
            self._show_general_help_fallback()

    def _get_current_tab(self) -> str:
        """Get the name of the currently active tab."""
        try:
            if hasattr(self, "main_area") and hasattr(self.main_area, "tabview"):
                return self.main_area.tabview.get()
            return "Application"
        except Exception:
            return "Application"

    def _get_focused_widget_info(self) -> dict:
        """Get information about the currently focused widget."""
        try:
            focused = self.focus_get()
            if focused:
                info = {"widget": focused, "type": type(focused).__name__}

                # Add context-specific information
                if hasattr(focused, "winfo_class"):
                    info["class"] = focused.winfo_class()

                # Check if it's in a specific area
                if hasattr(self, "sidebar") and self._is_widget_in_sidebar(focused):
                    info["area"] = "sidebar"
                elif hasattr(self, "main_area") and self._is_widget_in_main_area(
                    focused
                ):
                    info["area"] = "main_area"
                elif hasattr(self, "status_bar") and self._is_widget_in_status_bar(
                    focused
                ):
                    info["area"] = "status_bar"

                return info
            return {}
        except Exception:
            return {}

    def _is_widget_in_sidebar(self, widget) -> bool:
        """Check if widget is within the sidebar."""
        try:
            if hasattr(self, "sidebar"):
                return widget in self.sidebar.winfo_children() or any(
                    widget in child.winfo_children()
                    for child in self.sidebar.winfo_children()
                )
            return False
        except Exception:
            return False

    def _is_widget_in_main_area(self, widget) -> bool:
        """Check if widget is within the main area."""
        try:
            if hasattr(self, "main_area"):
                return widget in self.main_area.winfo_children() or any(
                    widget in child.winfo_children()
                    for child in self.main_area.winfo_children()
                )
            return False
        except Exception:
            return False

    def _is_widget_in_status_bar(self, widget) -> bool:
        """Check if widget is within the status bar."""
        try:
            if hasattr(self, "status_bar"):
                return widget in self.status_bar.winfo_children() or any(
                    widget in child.winfo_children()
                    for child in self.status_bar.winfo_children()
                )
            return False
        except Exception:
            return False

    def _generate_context_help(self, current_tab: str, focused_info: dict) -> str:
        """Generate context-specific help content."""
        help_sections = []

        # Tab-specific help
        tab_help = self._get_tab_specific_help(current_tab)
        if tab_help:
            help_sections.append(f"## {current_tab} Tab Help\n\n{tab_help}")

        # Widget-specific help
        if focused_info:
            widget_help = self._get_widget_specific_help(focused_info)
            if widget_help:
                help_sections.append(f"## Current Context\n\n{widget_help}")

        # General shortcuts
        general_shortcuts = self._get_general_shortcuts()
        help_sections.append(f"## General Shortcuts\n\n{general_shortcuts}")

        # Footer
        footer = "\n\nFor more information, visit the project documentation or press F1 for general help."
        help_sections.append(footer)

        return "\n\n".join(help_sections)

    def _get_tab_specific_help(self, tab_name: str) -> str:
        """Get help content specific to a tab."""
        tab_help = {
            "Configuration": """
Configure your APGI experiment parameters:

• **Parameters Tab**: Set θ₀ (Ignition Threshold), Πᵢ (Interoceptive Precision), and other model parameters
• **Stimuli Tab**: Configure stimulus presentation settings and timing
• **Hardware Tab**: Set up connections to EEG, cardiac monitors, and other devices
• **Validation Tab**: Configure parameter validation and error checking

Use the 'Run Analysis' button or Ctrl+R to test your configuration.
            """,
            "Analysis": """
Analyze your experimental data:

• **Data Import**: Load experimental data from CSV, JSON, or real-time sources
• **Processing**: Apply filtering, artifact removal, and preprocessing steps
• **Model Fitting**: Fit APGI models to your data using Bayesian methods
• **Visualization**: View results with interactive plots and statistics

Select data files from the sidebar and use analysis tools in the toolbar.
            """,
            "Visualization": """
Visualize your results:

• **Time Series**: Plot physiological signals over time
• **Phase Space**: View state space trajectories
• **Statistical Plots**: Display parameter distributions and confidence intervals
• **Interactive Controls**: Zoom, pan, and filter visualizations

Use the toolbar controls to customize plot appearance and export images.
            """,
            "Results": """
Review and export your analysis results:

• **Summary Statistics**: View key metrics and parameter estimates
• **Model Comparison**: Compare different model fits and validation scores
• **Export Options**: Save results as PDF reports, CSV data, or images
• **Session History**: Review previous analysis sessions

Use the export buttons to save your work in various formats.
            """,
        }
        return tab_help.get(tab_name, "")

    def _get_widget_specific_help(self, focused_info: dict) -> str:
        """Get help content specific to the focused widget."""
        widget_type = focused_info.get("type", "")
        area = focused_info.get("area", "")

        if "Entry" in widget_type or "Text" in widget_type:
            return "You are currently editing a text field. Type your input and press Enter to confirm, or Tab to move to the next field."
        elif "Button" in widget_type:
            return "Click this button to perform the displayed action, or use the associated keyboard shortcut if available."
        elif "Combobox" in widget_type or "OptionMenu" in widget_type:
            return "Click to open a dropdown menu and select from available options."
        elif area == "sidebar":
            return "The sidebar shows your recent files, project structure, and quick actions. Double-click files to open them."
        elif area == "status_bar":
            return "The status bar shows current application state, progress, and messages."
        else:
            return ""

    def _get_general_shortcuts(self) -> str:
        """Get general keyboard shortcuts help."""
        return """Common Shortcuts:
• F1 - Show this help
• Ctrl+N - New file
• Ctrl+O - Open file
• Ctrl+S - Save file
• Ctrl+Z - Undo
• Ctrl+Y - Redo
• Ctrl+T - Toggle theme
• Ctrl+0 - Reset zoom
• Ctrl+Plus/Minus - Zoom in/out
• Ctrl+Q - Quit application

Tab Navigation:
• Ctrl+1-4 - Switch to specific tabs
• Ctrl+Tab - Next tab
• Ctrl+Shift+Tab - Previous tab"""

    def _show_general_help(self, help_text_widget) -> None:
        """Show general help in the existing dialog."""
        try:
            general_help = """APGI Framework GUI Help

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
    Ctrl+Shift+Z     - Redo (alternative)
    Ctrl+Y           - Redo
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
    Ctrl+1-4         - Switch to tabs
    Ctrl+Tab         - Next tab
    Ctrl+Shift+Tab   - Previous tab
    
  Application:
    Ctrl+R           - Run analysis
    F5               - Refresh
    F1               - Show help

For more information, visit the project documentation."""

            help_text_widget.configure(state="normal")
            help_text_widget.delete("1.0", "end")
            help_text_widget.insert("1.0", general_help)
            help_text_widget.configure(state="disabled")

        except Exception as e:
            self.logger.error(f"Error showing general help: {e}")

    def _show_general_help_fallback(self) -> None:
        """Show general help as fallback when context help fails."""
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
    Ctrl+1-4         - Switch to tabs
    Ctrl+Tab         - Next tab
    Ctrl+Shift+Tab   - Previous tab
    
  Application:
    Ctrl+R           - Run analysis
    F5               - Refresh
    F1               - Show help

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
        except (AttributeError, TclError) as e:
            self.logger.warning(f"Failed to select all text: {e}")

    def copy(self) -> None:
        """Copy selected content."""
        try:
            focused = self.focus_get()
            if hasattr(focused, "selection_get"):
                self.clipboard_clear()
                self.clipboard_append(focused.selection_get())
                self.update_status("Copied to clipboard")
        except (AttributeError, TclError) as e:
            self.logger.warning(f"Nothing to copy: {e}")
            self.update_status("Nothing to copy", "warning")

    def paste(self) -> None:
        """Paste content from clipboard."""
        try:
            focused = self.focus_get()
            if hasattr(focused, "insert"):
                clipboard_content = self.clipboard_get()
                focused.insert("insert", clipboard_content)
                self.update_status("Pasted from clipboard")
        except (AttributeError, TclError) as e:
            self.logger.warning(f"Nothing to paste: {e}")
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
        except (AttributeError, TclError) as e:
            self.logger.warning(f"Nothing to cut: {e}")
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
        self.zoom_level = 1.0
        self._apply_zoom()
        self.update_status("Zoom reset to 100%")

    def zoom_in(self) -> None:
        """Zoom in."""
        new_zoom = self.zoom_level + self.zoom_step
        if new_zoom <= self.max_zoom:
            self.zoom_level = new_zoom
            self._apply_zoom()
            self.update_status(f"Zoomed in to {int(self.zoom_level * 100)}%")
        else:
            self.update_status(
                f"Maximum zoom ({int(self.max_zoom * 100)}%) reached", "warning"
            )

    def zoom_out(self) -> None:
        """Zoom out."""
        new_zoom = self.zoom_level - self.zoom_step
        if new_zoom >= self.min_zoom:
            self.zoom_level = new_zoom
            self._apply_zoom()
            self.update_status(f"Zoomed out to {int(self.zoom_level * 100)}%")
        else:
            self.update_status(
                f"Minimum zoom ({int(self.min_zoom * 100)}%) reached", "warning"
            )

    def _apply_zoom(self) -> None:
        """Apply current zoom level to all UI elements."""
        try:
            # Update font sizes
            zoom_factor = self.zoom_level

            # Base font sizes
            base_sizes = {
                "default": 12,
                "title": 16,
                "button": 11,
                "small": 10,
                "large": 14,
            }

            # Apply zoom to all tracked text widgets
            self._update_all_text_widgets(zoom_factor)

            # Apply zoom to font sizes for specific element types
            for element, base_size in base_sizes.items():
                zoomed_size = int(base_size * zoom_factor)
                # Apply to CustomTkinter widgets
                self._update_widget_fonts(element, zoomed_size)

            # Apply comprehensive zoom scaling to all widgets
            self._apply_zoom_to_all_widgets(zoom_factor)

            # Update status bar with zoom level
            if hasattr(self, "status_bar"):
                self.status_bar.set_zoom_level(int(self.zoom_level * 100))

            # Update window size if needed
            self._update_window_size()

            self.logger.debug(f"Applied zoom level: {int(self.zoom_level * 100)}%")

        except Exception as e:
            self.logger.error(f"Error applying zoom: {e}")
            self.update_status("Error applying zoom", "error")

    def _update_all_text_widgets(self, zoom_factor: float) -> None:
        """Update font sizes for all tracked text widgets."""
        for widget in list(self._text_widgets):
            try:
                if widget.winfo_exists():
                    if hasattr(widget, "cget") and "font" in widget.keys():
                        current_font = widget.cget("font")
                        if hasattr(current_font, "actual"):
                            # Get current font properties
                            current_size = current_font.actual()["size"] or 12
                            new_size = int(current_size * zoom_factor)

                            # Create new font with zoomed size
                            if hasattr(current_font, "copy"):
                                new_font = current_font.copy()
                                new_font.configure(size=new_size)
                            else:
                                # Fallback for simple font objects
                                new_font = ctk.CTkFont(size=new_size)

                            widget.configure(font=new_font)
                else:
                    # Remove widgets that no longer exist
                    self._text_widgets.discard(widget)
                    self._tracked_widgets.discard(widget)
            except Exception as e:
                self.logger.debug(f"Error updating widget font: {e}")
                # Remove problematic widgets
                self._text_widgets.discard(widget)

    def _update_widget_fonts(self, element_type: str, size: int) -> None:
        """Update font sizes for specific widget types."""
        try:
            # This is a simplified implementation
            # In a full implementation, we would track all widgets and update them
            font = ctk.CTkFont(size=size)

            # Update main area fonts
            if hasattr(self, "main_area"):
                # Update tab fonts
                if hasattr(self.main_area, "tabview"):
                    self.main_area.tabview.configure(font=font)

                # Update label fonts in main area
                for widget in self.main_area.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(font=font)

        except Exception as e:
            self.logger.warning(f"Error updating widget fonts: {e}")

    def _update_window_size(self) -> None:
        """Update window size based on zoom level."""
        try:
            # Get current window dimensions
            current_width = self.winfo_width()
            current_height = self.winfo_height()

            # Calculate new dimensions (simplified approach)
            if self.zoom_level != 1.0:
                # For zoom > 1.0, increase window size slightly
                scale_factor = 0.1 * (self.zoom_level - 1.0)
                new_width = int(current_width * (1 + scale_factor))
                new_height = int(current_height * (1 + scale_factor))

                # Apply new size
                self.geometry(f"{new_width}x{new_height}")

        except Exception as e:
            self.logger.warning(f"Error updating window size: {e}")

    def _apply_zoom_to_all_widgets(self, zoom_factor: float) -> None:
        """Apply zoom scaling to all widgets recursively."""
        try:
            # Store original sizes on first zoom application
            if not hasattr(self, "_original_widget_sizes"):
                self._original_widget_sizes = {}
                self._collect_original_sizes(self)

            # Apply zoom to all widgets starting from root
            self._scale_widget_recursive(self, zoom_factor)

        except Exception as e:
            self.logger.warning(f"Error applying zoom to widgets: {e}")

    def _collect_original_sizes(self, widget) -> None:
        """Collect original sizes of all widgets for zoom calculations."""
        try:
            widget_id = str(id(widget))

            # Store original size properties
            original_props = {}

            # Width and height
            if hasattr(widget, "cget"):
                try:
                    width = widget.cget("width")
                    if width and isinstance(width, (int, str)) and str(width).isdigit():
                        original_props["width"] = int(width)
                except (AttributeError, TclError) as e:
                    self.logger.debug(f"Could not get width for widget: {e}")

                try:
                    height = widget.cget("height")
                    if (
                        height
                        and isinstance(height, (int, str))
                        and str(height).isdigit()
                    ):
                        original_props["height"] = int(height)
                except (AttributeError, TclError) as e:
                    self.logger.debug(f"Could not get height for widget: {e}")

            # Store padding if available
            if hasattr(widget, "cget"):
                for prop in ["padx", "pady", "ipadx", "ipady"]:
                    try:
                        value = widget.cget(prop)
                        if (
                            value
                            and isinstance(value, (int, str))
                            and str(value).isdigit()
                        ):
                            original_props[prop] = int(value)
                    except (AttributeError, TclError) as e:
                        self.logger.debug(f"Could not get {prop} for widget: {e}")

            if original_props:
                self._original_widget_sizes[widget_id] = original_props

            # Recursively collect for children
            for child in widget.winfo_children():
                self._collect_original_sizes(child)

        except Exception as e:
            self.logger.warning(f"Error collecting sizes for widget: {e}")

    def _scale_widget_recursive(self, widget, zoom_factor: float) -> None:
        """Recursively scale a widget and its children."""
        try:
            widget_id = str(id(widget))

            # Scale this widget if we have original sizes
            if widget_id in self._original_widget_sizes:
                original_props = self._original_widget_sizes[widget_id]
                new_props = {}

                # Scale width and height
                if "width" in original_props:
                    new_props["width"] = max(
                        1, int(original_props["width"] * zoom_factor)
                    )
                if "height" in original_props:
                    new_props["height"] = max(
                        1, int(original_props["height"] * zoom_factor)
                    )

                # Scale padding
                for prop in ["padx", "pady", "ipadx", "ipady"]:
                    if prop in original_props:
                        new_props[prop] = max(
                            0, int(original_props[prop] * zoom_factor)
                        )

                # Apply new properties if any
                if new_props and hasattr(widget, "configure"):
                    try:
                        widget.configure(**new_props)
                    except Exception as e:
                        self.logger.debug(f"Error configuring widget: {e}")

            # Recursively scale children
            for child in widget.winfo_children():
                self._scale_widget_recursive(child, zoom_factor)

        except Exception as e:
            self.logger.debug(f"Error scaling widget: {e}")

    def switch_to_tab(self, tab_name: str) -> None:
        """Switch to a specific tab."""
        try:
            self.main_area.tabview.set(tab_name)
            self.update_status(f"Switched to {tab_name} tab")
        except (AttributeError, KeyError, IndexError) as e:
            # Log specific error and fallback to configuration
            self.logger.error(f"Error [tab change]: {e}")
            self.create_configuration_content()
            self.update_status(f"Failed to switch to {tab_name} tab", "error")

    def next_tab(self) -> None:
        """Switch to the next tab."""
        try:
            current = self.main_area.tabview.get()
            tabs = ["Configuration", "Analysis", "Visualization", "Results"]
            current_index = tabs.index(current) if current in tabs else 0
            next_index = (current_index + 1) % len(tabs)
            self.switch_to_tab(tabs[next_index])
        except (AttributeError, IndexError) as e:
            self.logger.warning(f"Failed to switch to next tab: {e}")

    def previous_tab(self) -> None:
        """Switch to the previous tab."""
        try:
            current = self.main_area.tabview.get()
            tabs = ["Configuration", "Analysis", "Visualization", "Results"]
            current_index = tabs.index(current) if current in tabs else 0
            prev_index = (current_index - 1) % len(tabs)
            self.switch_to_tab(tabs[prev_index])
        except (AttributeError, IndexError) as e:
            self.logger.warning(f"Failed to switch to previous tab: {e}")

    def run_analysis(self) -> None:
        """Run the current analysis."""
        self.main_area.run_analysis()

    def refresh(self) -> None:
        """Refresh the current view."""
        self.sidebar.refresh()
        self.update_status("Refreshed")

    def find(self) -> None:
        """Open find dialog."""
        raise NotImplementedError("Find functionality not yet implemented")

    def find_next(self) -> None:
        """Find next occurrence."""
        raise NotImplementedError("Find next not yet implemented")

    def find_previous(self) -> None:
        """Find previous occurrence."""
        raise NotImplementedError("Find previous not yet implemented")

    def toggle_debug_mode(self) -> None:
        """Toggle debug mode."""
        raise NotImplementedError("Debug mode not yet implemented")

    def show_log(self) -> None:
        """Show application log viewer with pagination."""
        try:
            # Import the paginated log viewer
            from .components.paginated_log_viewer import PaginatedLogViewer

            # Get log file path
            log_file_path = self.config.log_dir / "apgi_gui.log"

            # Create and show paginated log viewer
            log_viewer = PaginatedLogViewer(self, str(log_file_path))
            log_viewer.show()

            self.update_status("Paginated log viewer opened")

        except Exception as e:
            self.logger.error(f"Error opening log viewer: {e}")
            self.update_status("Error opening log viewer", "error")

            # Fallback to old log viewer if paginated viewer fails
            self._show_fallback_log_viewer()

    def _show_fallback_log_viewer(self) -> None:
        """Show a basic fallback log viewer with text widget."""
        try:
            # Create fallback log viewer window
            log_window = ctk.CTkToplevel(self)
            log_window.title("Application Log (Fallback)")
            log_window.geometry("800x600")
            log_window.transient(self)
            log_window.grab_set()

            # Configure grid
            log_window.grid_columnconfigure(0, weight=1)
            log_window.grid_rowconfigure(0, weight=1)

            # Create text widget for log display
            log_text = ctk.CTkTextbox(log_window, wrap="none")
            log_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            # Create button frame
            button_frame = ctk.CTkFrame(log_window)
            button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
            button_frame.grid_columnconfigure((0, 1, 2), weight=1)

            # Refresh button
            refresh_btn = ctk.CTkButton(
                button_frame,
                text="Refresh",
                command=lambda: self._refresh_log(log_text, "ALL"),
            )
            refresh_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

            # Export button
            export_btn = ctk.CTkButton(
                button_frame,
                text="Export",
                command=lambda: self._export_log(log_text),
            )
            export_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            # Close button
            close_btn = ctk.CTkButton(
                button_frame, text="Close", command=log_window.destroy
            )
            close_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

            # Load initial log content
            self._refresh_log(log_text, "ALL")

            self.update_status("Fallback log viewer opened")

        except Exception as e:
            self.logger.error(f"Error opening fallback log viewer: {e}")
            self.update_status("Error opening fallback log viewer", "error")

    def _refresh_log(self, log_text, level_filter: str, search_term: str = "") -> None:
        """Refresh log content with filtering and search."""
        try:
            log_text.delete("1.0", "end")

            # Get log file path
            log_file_path = self.config.log_dir / "apgi_gui.log"

            if not log_file_path.exists():
                log_text.insert("1.0", "No log file found.")
                return

            # Read log file
            with open(log_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Filter by level
            if level_filter != "ALL":
                filtered_lines = []
                for line in lines:
                    if level_filter.lower() in line.lower():
                        filtered_lines.append(line)
                lines = filtered_lines

            # Filter by search term
            if search_term:
                search_lines = []
                for line in lines:
                    if search_term.lower() in line.lower():
                        search_lines.append(line)
                lines = search_lines

            # Display last 1000 lines to prevent memory issues
            if len(lines) > 1000:
                original_count = len(lines)
                lines = lines[-1000:]
                log_text.insert(
                    "1.0",
                    f"Showing last 1000 lines of {original_count} total lines\n\n",
                )

            # Insert lines
            for line in lines:
                log_text.insert("end", line)

            # Scroll to bottom
            log_text.see("end")

        except Exception as e:
            self.logger.error(f"Error refreshing log: {e}")
            log_text.insert("1.0", f"Error loading log: {e}")

    def _export_log(self, log_text) -> None:
        """Export log content to file."""
        try:
            file_path = tk.filedialog.asksaveasfilename(
                title="Export Log",
                defaultextension=".log",
                filetypes=[
                    ("Log Files", "*.log"),
                    ("Text Files", "*.txt"),
                    ("All Files", "*.*"),
                ],
                initialdir=self.config.data_dir,
            )

            if file_path:
                content = log_text.get("1.0", "end")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.update_status(f"Log exported to {Path(file_path).name}")

        except Exception as e:
            self.logger.error(f"Error exporting log: {e}")
            self.update_status("Error exporting log", "error")

    def show_preferences(self) -> None:
        """Show preferences dialog."""
        try:
            # Create preferences window
            pref_window = ctk.CTkToplevel(self)
            pref_window.title("Preferences")
            pref_window.geometry("700x600")
            pref_window.transient(self)
            pref_window.grab_set()

            # Configure grid
            pref_window.grid_columnconfigure(0, weight=1)
            pref_window.grid_rowconfigure(1, weight=1)

            # Create notebook for tabs
            notebook = ctk.CTkTabview(pref_window)
            notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            # General Settings Tab
            general_tab = notebook.add("General")

            # Default save location
            save_frame = ctk.CTkFrame(general_tab)
            save_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(save_frame, text="Default Save Location:").pack(
                anchor="w", pady=5
            )
            save_location_var = tk.StringVar(value=str(self.config.data_dir))
            save_entry = ctk.CTkEntry(save_frame, textvariable=save_location_var)
            save_entry.pack(fill="x", pady=5)

            browse_save_btn = ctk.CTkButton(
                save_frame,
                text="Browse",
                command=lambda: self._browse_save_location(save_location_var),
            )
            browse_save_btn.pack(pady=5)

            # Auto-save interval
            autosave_frame = ctk.CTkFrame(general_tab)
            autosave_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(autosave_frame, text="Auto-save Interval:").pack(
                anchor="w", pady=5
            )
            autosave_var = tk.StringVar(value="off")
            autosave_menu = ctk.CTkOptionMenu(
                autosave_frame,
                variable=autosave_var,
                values=["off", "5min", "10min", "30min"],
            )
            autosave_menu.pack(fill="x", pady=5)

            # Recent files limit
            recent_frame = ctk.CTkFrame(general_tab)
            recent_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(recent_frame, text="Recent Files Limit:").pack(
                anchor="w", pady=5
            )
            recent_var = tk.StringVar(value="10")
            recent_menu = ctk.CTkOptionMenu(
                recent_frame, variable=recent_var, values=["10", "20", "50", "100"]
            )
            recent_menu.pack(fill="x", pady=5)

            # Appearance Settings Tab
            appearance_tab = notebook.add("Appearance")

            # Theme
            theme_frame = ctk.CTkFrame(appearance_tab)
            theme_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(theme_frame, text="Theme:").pack(anchor="w", pady=5)
            theme_var = tk.StringVar(value=self.config.theme)
            theme_menu = ctk.CTkOptionMenu(
                theme_frame, variable=theme_var, values=["light", "dark", "system"]
            )
            theme_menu.pack(fill="x", pady=5)

            # Font size
            font_frame = ctk.CTkFrame(appearance_tab)
            font_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(font_frame, text="Font Size:").pack(anchor="w", pady=5)
            font_var = tk.StringVar(value="12")
            font_menu = ctk.CTkOptionMenu(
                font_frame,
                variable=font_var,
                values=["8", "10", "12", "14", "16", "18", "20"],
            )
            font_menu.pack(fill="x", pady=5)

            # UI Scale
            scale_frame = ctk.CTkFrame(appearance_tab)
            scale_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(scale_frame, text="UI Scale:").pack(anchor="w", pady=5)
            scale_var = tk.StringVar(value="100%")
            scale_menu = ctk.CTkOptionMenu(
                scale_frame,
                variable=scale_var,
                values=["50%", "75%", "100%", "125%", "150%", "175%", "200%"],
            )
            scale_menu.pack(fill="x", pady=5)

            # Performance Settings Tab
            performance_tab = notebook.add("Performance")

            # Thread pool size
            thread_frame = ctk.CTkFrame(performance_tab)
            thread_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(thread_frame, text="Thread Pool Size:").pack(
                anchor="w", pady=5
            )
            thread_var = tk.StringVar(value="4")
            thread_menu = ctk.CTkOptionMenu(
                thread_frame, variable=thread_var, values=["1", "2", "4", "8", "16"]
            )
            thread_menu.pack(fill="x", pady=5)

            # Log retention days
            log_frame = ctk.CTkFrame(performance_tab)
            log_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(log_frame, text="Log Retention (days):").pack(
                anchor="w", pady=5
            )
            log_var = tk.StringVar(value="7")
            log_menu = ctk.CTkOptionMenu(
                log_frame, variable=log_var, values=["1", "3", "7", "14", "30"]
            )
            log_menu.pack(fill="x", pady=5)

            # Memory limits
            memory_frame = ctk.CTkFrame(performance_tab)
            memory_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(memory_frame, text="Memory Limit (MB):").pack(
                anchor="w", pady=5
            )
            memory_var = tk.StringVar(value="1024")
            memory_entry = ctk.CTkEntry(memory_frame, textvariable=memory_var)
            memory_entry.pack(fill="x", pady=5)

            # Experiment Settings Tab
            experiment_tab = notebook.add("Experiment")

            # Default parameters
            params_frame = ctk.CTkFrame(experiment_tab)
            params_frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(
                params_frame,
                text="Default Parameters:",
                font=ctk.CTkFont(size=14, weight="bold"),
            ).pack(anchor="w", pady=5)

            # Add some example parameter settings
            param1_frame = ctk.CTkFrame(params_frame)
            param1_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(param1_frame, text="θ₀ (Ignition Threshold):").pack(
                anchor="w", pady=2
            )
            theta0_var = tk.StringVar(value="0.5")
            theta0_entry = ctk.CTkEntry(param1_frame, textvariable=theta0_var)
            theta0_entry.pack(fill="x", pady=2)

            param2_frame = ctk.CTkFrame(params_frame)
            param2_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(param2_frame, text="Πᵢ (Interoceptive Precision):").pack(
                anchor="w", pady=2
            )
            pi_var = tk.StringVar(value="1.0")
            pi_entry = ctk.CTkEntry(param2_frame, textvariable=pi_var)
            pi_entry.pack(fill="x", pady=2)

            # Button frame
            button_frame = ctk.CTkFrame(pref_window)
            button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
            button_frame.grid_columnconfigure((0, 1, 2), weight=1)

            save_btn = ctk.CTkButton(
                button_frame,
                text="Save",
                command=lambda: self._save_preferences(
                    pref_window,
                    {
                        "save_location": save_location_var.get(),
                        "autosave": autosave_var.get(),
                        "recent_limit": recent_var.get(),
                        "theme": theme_var.get(),
                        "font_size": font_var.get(),
                        "ui_scale": scale_var.get(),
                        "thread_pool": thread_var.get(),
                        "log_retention": log_var.get(),
                        "memory_limit": memory_var.get(),
                        "theta0": theta0_var.get(),
                        "pi_i": pi_var.get(),
                    },
                ),
            )
            save_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

            reset_btn = ctk.CTkButton(
                button_frame,
                text="Reset to Defaults",
                command=lambda: self._reset_preferences(pref_window),
            )
            reset_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            cancel_btn = ctk.CTkButton(
                button_frame, text="Cancel", command=pref_window.destroy
            )
            cancel_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

            self.update_status("Preferences dialog opened")

        except Exception as e:
            self.logger.error(f"Error opening preferences: {e}")
            self.update_status("Error opening preferences", "error")

    def _browse_save_location(self, save_location_var: tk.StringVar) -> None:
        """Browse for save location and update the variable."""
        directory = tk.filedialog.askdirectory(
            title="Select Default Save Location", initialdir=self.config.data_dir
        )
        if directory:
            save_location_var.set(directory)

    def _save_preferences(self, window, prefs: dict) -> None:
        """Save preferences to config."""
        try:
            # Save to config file (simplified)
            import json

            config_file = self.config.config_dir / "preferences.json"

            with open(config_file, "w") as f:
                json.dump(prefs, f, indent=2)

            # Apply some settings immediately
            if prefs.get("theme") != self.config.theme:
                self.config.theme = prefs["theme"]
                ctk.set_appearance_mode(prefs["theme"])

            self.update_status("Preferences saved")
            window.destroy()

        except Exception as e:
            self.logger.error(f"Error saving preferences: {e}")
            self.update_status("Error saving preferences", "error")

    def _reset_preferences(self, window) -> None:
        """Reset preferences to defaults."""
        try:
            # Reset to default values
            defaults = {
                "save_location": str(self.config.data_dir),
                "autosave": "off",
                "recent_limit": "10",
                "theme": "dark",
                "font_size": "12",
                "ui_scale": "100%",
                "thread_pool": "4",
                "log_retention": "7",
                "memory_limit": "1024",
                "theta0": "0.5",
                "pi_i": "1.0",
            }

            # Update the config
            import json

            config_file = self.config.config_dir / "preferences.json"

            with open(config_file, "w") as f:
                json.dump(defaults, f, indent=2)

            # Apply theme immediately
            self.config.theme = defaults["theme"]
            ctk.set_appearance_mode(defaults["theme"])

            self.update_status("Preferences reset to defaults")
            window.destroy()

        except Exception as e:
            self.logger.error(f"Error resetting preferences: {e}")
            self.update_status("Error resetting preferences", "error")

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
