"""
Common GUI components for APGI Framework applications.

Extracts shared functionality to reduce duplication across GUI files.
Provides standardized error handling, file operations, tooltips, and more.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Dict, List, Callable, Optional, Any, Union
import logging
import json
import os
from pathlib import Path
import traceback
from dataclasses import dataclass
from datetime import datetime

try:
    import customtkinter as ctk

    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    FigureCanvasTkAgg = None

logger = logging.getLogger(__name__)


@dataclass
class ErrorInfo:
    """Structure for error information."""

    title: str
    message: str
    technical_details: Optional[str] = None
    error_type: str = "error"  # error, warning, info
    timestamp: Optional[datetime] = None


class ErrorHandler:
    """
    Centralized error handling for GUI applications.

    Provides user-friendly error messages with optional technical details.
    """

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.error_queue: List[ErrorInfo] = []
        self.show_technical_details = False

    def show_error(
        self,
        title: str,
        message: str,
        technical_details: Optional[str] = None,
        error_type: str = "error",
    ):
        """
        Show an error message to the user.

        Args:
            title: Error title
            message: User-friendly error message
            technical_details: Optional technical details for debugging
            error_type: Type of error (error, warning, info)
        """
        error_info = ErrorInfo(
            title=title,
            message=message,
            technical_details=technical_details,
            error_type=error_type,
            timestamp=datetime.now(),
        )

        self.error_queue.append(error_info)

        # Show the error dialog
        self._show_error_dialog(error_info)

    def _show_error_dialog(self, error_info: ErrorInfo):
        """Show the actual error dialog."""
        try:
            if error_info.error_type == "error":
                messagebox.showerror(error_info.title, error_info.message)
            elif error_info.error_type == "warning":
                messagebox.showwarning(error_info.title, error_info.message)
            else:
                messagebox.showinfo(error_info.title, error_info.message)

            # Show technical details if available and enabled
            if error_info.technical_details and self.show_technical_details:
                self._show_technical_details_dialog(error_info)

        except Exception as e:
            logger.error(f"Failed to show error dialog: {e}")
            # Fallback to print
            print(f"ERROR: {error_info.title} - {error_info.message}")
            if error_info.technical_details:
                print(f"Technical details: {error_info.technical_details}")

    def _show_technical_details_dialog(self, error_info: ErrorInfo):
        """Show technical details in a separate dialog."""
        try:
            details_window = tk.Toplevel(self.parent)
            details_window.title(f"Technical Details - {error_info.title}")
            details_window.geometry("600x400")

            # Create text widget with scrollbar
            text_frame = tk.Frame(details_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            text_widget = tk.Text(
                text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set
            )
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=text_widget.yview)

            # Insert technical details
            text_widget.insert(tk.END, f"Error: {error_info.title}\n")
            text_widget.insert(tk.END, f"Message: {error_info.message}\n")
            text_widget.insert(tk.END, f"Timestamp: {error_info.timestamp}\n")
            text_widget.insert(tk.END, "\n" + "=" * 50 + "\n")
            text_widget.insert(tk.END, "Technical Details:\n")
            text_widget.insert(tk.END, error_info.technical_details)

            text_widget.config(state=tk.DISABLED)

            # Close button
            close_btn = tk.Button(
                details_window, text="Close", command=details_window.destroy
            )
            close_btn.pack(pady=5)

        except Exception as e:
            logger.error(f"Failed to show technical details dialog: {e}")

    def toggle_technical_details(self):
        """Toggle whether to show technical details."""
        self.show_technical_details = not self.show_technical_details

    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of errors by type."""
        summary = {"error": 0, "warning": 0, "info": 0}
        for error in self.error_queue:
            if error.error_type in summary:
                summary[error.error_type] += 1
        return summary

    def clear_errors(self):
        """Clear the error queue."""
        self.error_queue.clear()


class FileManager:
    """
    Centralized file operations for GUI applications.

    Provides consistent file dialogs, validation, and operations.
    """

    def __init__(self, parent: tk.Widget, error_handler: ErrorHandler):
        self.parent = parent
        self.error_handler = error_handler
        self.last_directory = Path.home()
        self.file_filters = {
            "json": [("JSON files", "*.json"), ("All files", "*.*")],
            "csv": [("CSV files", "*.csv"), ("All files", "*.*")],
            "data": [("Data files", "*.json *.csv *.txt"), ("All files", "*.*")],
            "config": [("Config files", "*.json *.yaml *.yml"), ("All files", "*.*")],
            "all": [("All files", "*.*")],
        }

    def open_file(
        self, file_type: str = "all", title: str = "Open File"
    ) -> Optional[Path]:
        """
        Open a file dialog and return the selected file path.

        Args:
            file_type: Type of file filter to use
            title: Dialog title

        Returns:
            Selected file path or None if cancelled
        """
        try:
            filetypes = self.file_filters.get(file_type, self.file_filters["all"])

            filename = filedialog.askopenfilename(
                parent=self.parent,
                title=title,
                initialdir=str(self.last_directory),
                filetypes=filetypes,
            )

            if filename:
                path = Path(filename)
                self.last_directory = path.parent
                return path

            return None

        except Exception as e:
            self.error_handler.show_error(
                "File Open Error",
                f"Failed to open file dialog: {str(e)}",
                traceback.format_exc(),
            )
            return None

    def save_file(
        self,
        file_type: str = "all",
        title: str = "Save File",
        default_extension: str = "",
    ) -> Optional[Path]:
        """
        Save a file dialog and return the selected file path.

        Args:
            file_type: Type of file filter to use
            title: Dialog title
            default_extension: Default file extension

        Returns:
            Selected file path or None if cancelled
        """
        try:
            filetypes = self.file_filters.get(file_type, self.file_filters["all"])

            filename = filedialog.asksaveasfilename(
                parent=self.parent,
                title=title,
                initialdir=str(self.last_directory),
                filetypes=filetypes,
                defaultextension=default_extension,
            )

            if filename:
                path = Path(filename)
                self.last_directory = path.parent
                return path

            return None

        except Exception as e:
            self.error_handler.show_error(
                "File Save Error",
                f"Failed to save file dialog: {str(e)}",
                traceback.format_exc(),
            )
            return None

    def load_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load JSON data from file.

        Args:
            file_path: Path to JSON file

        Returns:
            Loaded data or None if failed
        """
        try:
            if not file_path.exists():
                self.error_handler.show_error(
                    "File Not Found", f"File not found: {file_path}"
                )
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.info(f"Successfully loaded JSON from {file_path}")
            return data

        except json.JSONDecodeError as e:
            self.error_handler.show_error(
                "JSON Parse Error", f"Invalid JSON format in file: {file_path}", str(e)
            )
            return None
        except Exception as e:
            self.error_handler.show_error(
                "File Load Error",
                f"Failed to load file: {file_path}",
                traceback.format_exc(),
            )
            return None

    def save_json(self, data: Dict[str, Any], file_path: Path) -> bool:
        """
        Save data to JSON file.

        Args:
            data: Data to save
            file_path: Path to save file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Successfully saved JSON to {file_path}")
            return True

        except Exception as e:
            self.error_handler.show_error(
                "File Save Error",
                f"Failed to save file: {file_path}",
                traceback.format_exc(),
            )
            return False


class ThemeManager:
    """
    Centralized theme management for GUI applications.

    Provides consistent theming across different GUI implementations.
    """

    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "select_bg": "#0078d4",
                "select_fg": "#ffffff",
                "button_bg": "#f0f0f0",
                "button_fg": "#000000",
            },
            "dark": {
                "bg": "#2d2d2d",
                "fg": "#ffffff",
                "select_bg": "#404040",
                "select_fg": "#ffffff",
                "button_bg": "#404040",
                "button_fg": "#ffffff",
            },
            "system": None,  # Will be determined based on system
        }

        # Detect system theme if needed
        if self.themes["system"] is None:
            self._detect_system_theme()

    def _detect_system_theme(self):
        """Detect system theme preference."""
        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()  # Hide the window

            # Try to get system theme
            try:
                system_theme = root.tk.call("tk", "windowingsystem")
                if system_theme == "win32":
                    # Windows: check registry
                    import winreg

                    with winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                    ) as key:
                        apps_use_light_theme = winreg.QueryValueEx(
                            key, "AppsUseLightTheme"
                        )[0]
                        self.themes["system"] = self.themes[
                            "light" if apps_use_light_theme else "dark"
                        ]
                else:
                    # Default to light for other systems
                    self.themes["system"] = self.themes["light"]
            except:
                self.themes["system"] = self.themes["light"]

            root.destroy()

        except Exception:
            self.themes["system"] = self.themes["light"]

    def set_theme(self, theme_name: str):
        """Set the current theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            logger.info(f"Theme set to: {theme_name}")
        else:
            logger.warning(f"Unknown theme: {theme_name}")

    def get_theme_colors(self) -> Dict[str, str]:
        """Get colors for the current theme."""
        theme = self.themes.get(self.current_theme, self.themes["light"])
        return theme.copy() if theme else self.themes["light"].copy()

    def apply_theme_to_widget(self, widget: tk.Widget):
        """Apply theme to a widget and its children."""
        colors = self.get_theme_colors()

        try:
            if hasattr(widget, "configure"):
                # Configure basic colors
                widget.configure(bg=colors["bg"])

                # Handle different widget types
                if isinstance(widget, (tk.Label, tk.Button)):
                    widget.configure(fg=colors["fg"])
                elif isinstance(widget, tk.Entry):
                    widget.configure(
                        fg=colors["fg"],
                        insertbackground=colors["fg"],
                        selectbackground=colors["select_bg"],
                        selectforeground=colors["select_fg"],
                    )
                elif isinstance(widget, tk.Frame):
                    widget.configure(bg=colors["bg"])

            # Recursively apply to children
            for child in widget.winfo_children():
                self.apply_theme_to_widget(child)

        except Exception as e:
            logger.warning(f"Failed to apply theme to widget: {e}")


class PlotManager:
    """
    Centralized plotting functionality for GUI applications.

    Provides consistent matplotlib integration and plot management.
    """

    def __init__(self, parent: tk.Widget, error_handler: ErrorHandler):
        self.parent = parent
        self.error_handler = error_handler
        self.plots: Dict[str, Any] = {}

        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Matplotlib not available - plotting functionality disabled")

    def create_plot_canvas(self, figure_size: tuple = (8, 6)) -> Optional[Any]:
        """
        Create a matplotlib canvas for plotting.

        Args:
            figure_size: Tuple of (width, height) for the figure

        Returns:
            Canvas widget or None if matplotlib not available
        """
        if not MATPLOTLIB_AVAILABLE:
            self.error_handler.show_error(
                "Matplotlib Not Available",
                "Matplotlib is not installed. Install it to use plotting functionality.",
            )
            return None

        try:
            fig, ax = plt.subplots(figsize=figure_size)
            canvas = FigureCanvasTkAgg(fig, master=self.parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            return {"figure": fig, "axis": ax, "canvas": canvas}

        except Exception as e:
            self.error_handler.show_error(
                "Plot Creation Error",
                "Failed to create plot canvas",
                traceback.format_exc(),
            )
            return None

    def update_plot(self, plot_id: str, data: Dict[str, Any]):
        """
        Update an existing plot with new data.

        Args:
            plot_id: ID of the plot to update
            data: Data to plot
        """
        if plot_id not in self.plots:
            logger.error(f"Plot not found: {plot_id}")
            return

        try:
            plot_info = self.plots[plot_id]
            ax = plot_info["axis"]
            canvas = plot_info["canvas"]

            # Clear previous plot
            ax.clear()

            # Plot new data
            if "x" in data and "y" in data:
                ax.plot(data["x"], data["y"])

            if "title" in data:
                ax.set_title(data["title"])
            if "xlabel" in data:
                ax.set_xlabel(data["xlabel"])
            if "ylabel" in data:
                ax.set_ylabel(data["ylabel"])

            canvas.draw()

        except Exception as e:
            self.error_handler.show_error(
                "Plot Update Error",
                f"Failed to update plot: {plot_id}",
                traceback.format_exc(),
            )


class CommonGUIComponents:
    """
    Main class that provides access to all common GUI components.

    This is the main entry point for GUI applications to access
    shared functionality and reduce code duplication.
    """

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.error_handler = ErrorHandler(parent)
        self.file_manager = FileManager(parent, self.error_handler)
        self.theme_manager = ThemeManager()
        self.plot_manager = PlotManager(parent, self.error_handler)

        logger.info("Common GUI components initialized")

    def setup_error_handling(self):
        """Setup global error handling for the application."""

        def handle_exception(exc_type, exc_value, exc_traceback):
            error_msg = "".join(
                traceback.format_exception(exc_type, exc_value, exc_traceback)
            )
            self.error_handler.show_error(
                "Unhandled Exception",
                f"An unexpected error occurred: {exc_type.__name__}: {exc_value}",
                error_msg,
            )

        # Set global exception handler
        import sys

        sys.excepthook = handle_exception

    def create_standard_buttons(
        self, parent_frame: tk.Widget, callbacks: Dict[str, Callable]
    ) -> Dict[str, tk.Button]:
        """
        Create standard buttons with consistent styling.

        Args:
            parent_frame: Frame to add buttons to
            callbacks: Dictionary of button names to callback functions

        Returns:
            Dictionary of button widgets
        """
        buttons = {}
        colors = self.theme_manager.get_theme_colors()

        button_configs = {
            "OK": {"text": "OK", "default": "active"},
            "Cancel": {"text": "Cancel"},
            "Save": {"text": "Save"},
            "Load": {"text": "Load"},
            "Run": {"text": "Run", "default": "active"},
            "Stop": {"text": "Stop"},
            "Clear": {"text": "Clear"},
            "Reset": {"text": "Reset"},
        }

        for button_name, callback in callbacks.items():
            config = button_configs.get(button_name, {"text": button_name})

            btn = tk.Button(
                parent_frame,
                text=config["text"],
                command=callback,
                bg=colors["button_bg"],
                fg=colors["button_fg"],
            )

            if config.get("default") == "active":
                btn.configure(relief=tk.SUNKEN, borderwidth=2)

            btn.pack(side=tk.LEFT, padx=5, pady=5)
            buttons[button_name] = btn

        return buttons


def create_common_components(parent: tk.Widget) -> CommonGUIComponents:
    """
    Convenience function to create common GUI components.

    Args:
        parent: Parent widget

    Returns:
        CommonGUIComponents instance
    """
    return CommonGUIComponents(parent)
