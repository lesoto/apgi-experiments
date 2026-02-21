"""
Keyboard Shortcuts Manager for APGI Framework GUI

Provides comprehensive keyboard shortcut functionality for all GUI applications.
Supports both tkinter and customtkinter applications.
"""

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, Optional, Union

import customtkinter as ctk


class KeyboardManager:
    """Manages keyboard shortcuts for GUI applications."""

    def __init__(self, root_widget: Union[tk.Tk, tk.Toplevel, ctk.CTk]):
        self.root = root_widget
        self.shortcuts = {}
        self.active = True
        self._load_default_shortcuts()

    def _load_default_shortcuts(self):
        """Load default keyboard shortcuts."""
        self.default_shortcuts = {
            # File operations
            "Ctrl+O": {"action": "open_file", "description": "Open file"},
            "Ctrl+S": {"action": "save_file", "description": "Save file"},
            "Ctrl+Shift+S": {"action": "save_as", "description": "Save as"},
            "Ctrl+Q": {"action": "quit", "description": "Quit application"},
            "Ctrl+W": {"action": "close_window", "description": "Close window"},
            # Edit operations
            "Ctrl+Z": {"action": "undo", "description": "Undo"},
            "Ctrl+Y": {"action": "redo", "description": "Redo"},
            "Ctrl+C": {"action": "copy", "description": "Copy"},
            "Ctrl+V": {"action": "paste", "description": "Paste"},
            "Ctrl+X": {"action": "cut", "description": "Cut"},
            "Ctrl+A": {"action": "select_all", "description": "Select all"},
            "Delete": {"action": "delete", "description": "Delete"},
            # Application operations
            "Ctrl+R": {"action": "run_experiment", "description": "Run experiment"},
            "Ctrl+Shift+R": {"action": "run_all", "description": "Run all experiments"},
            "Ctrl+E": {"action": "export_data", "description": "Export data"},
            "Ctrl+L": {"action": "load_config", "description": "Load configuration"},
            "Ctrl+Shift+C": {"action": "clear_results", "description": "Clear results"},
            # View operations
            "Ctrl+F": {"action": "search", "description": "Search"},
            "Ctrl+Shift+F": {
                "action": "find_replace",
                "description": "Find and replace",
            },
            "F5": {"action": "refresh", "description": "Refresh"},
            "F11": {"action": "toggle_fullscreen", "description": "Toggle fullscreen"},
            # Navigation
            "Ctrl+Tab": {"action": "next_tab", "description": "Next tab"},
            "Ctrl+Shift+Tab": {"action": "previous_tab", "description": "Previous tab"},
            "Ctrl+1": {"action": "focus_sidebar", "description": "Focus sidebar"},
            "Ctrl+2": {"action": "focus_main", "description": "Focus main area"},
            "Ctrl+3": {"action": "focus_status", "description": "Focus status bar"},
            # Help
            "F1": {"action": "help", "description": "Show help"},
            "Ctrl+H": {
                "action": "show_shortcuts",
                "description": "Show keyboard shortcuts",
            },
            # Theme operations
            "Ctrl+D": {"action": "toggle_dark_mode", "description": "Toggle dark mode"},
            "Ctrl+Plus": {"action": "zoom_in", "description": "Zoom in"},
            "Ctrl+Minus": {"action": "zoom_out", "description": "Zoom out"},
            "Ctrl+0": {"action": "reset_zoom", "description": "Reset zoom"},
        }

        # Initialize with defaults
        self.shortcuts = self.default_shortcuts.copy()

    def bind_shortcut(
        self, key_combination: str, callback: Callable, description: str = ""
    ) -> None:
        """Bind a keyboard shortcut to a callback function."""
        # Store shortcut info
        self.shortcuts[key_combination] = {
            "action": callback.__name__ if hasattr(callback, "__name__") else "custom",
            "description": description or "Custom action",
            "callback": callback,
        }

        # Bind the key combination
        try:
            self.root.bind_all(
                key_combination, lambda e: self._execute_shortcut(key_combination, e)
            )
        except Exception as e:
            print(f"Error binding shortcut {key_combination}: {e}")

    def bind_shortcuts(self, shortcuts_dict: Dict[str, Dict[str, Any]]) -> None:
        """Bind multiple shortcuts at once."""
        for key_combo, info in shortcuts_dict.items():
            if "callback" in info:
                self.bind_shortcut(
                    key_combo, info["callback"], info.get("description", "")
                )

    def _execute_shortcut(self, key_combination: str, event) -> None:
        """Execute a shortcut callback."""
        if not self.active:
            return

        if key_combination in self.shortcuts:
            shortcut_info = self.shortcuts[key_combination]

            # Call the callback if it exists
            if "callback" in shortcut_info:
                try:
                    shortcut_info["callback"](event)
                except Exception as e:
                    print(f"Error executing shortcut {key_combination}: {e}")

            # Prevent default behavior
            return "break"

    def unbind_shortcut(self, key_combination: str) -> None:
        """Unbind a keyboard shortcut."""
        if key_combination in self.shortcuts:
            try:
                self.root.unbind_all(key_combination)
                del self.shortcuts[key_combination]
            except Exception as e:
                print(f"Error unbinding shortcut {key_combination}: {e}")

    def disable_shortcuts(self) -> None:
        """Temporarily disable all shortcuts."""
        self.active = False

    def enable_shortcuts(self) -> None:
        """Re-enable all shortcuts."""
        self.active = True

    def get_shortcuts_list(self) -> Dict[str, str]:
        """Get a dictionary of shortcuts and their descriptions."""
        return {combo: info["description"] for combo, info in self.shortcuts.items()}

    def show_shortcuts_dialog(self) -> None:
        """Show a dialog displaying all available shortcuts."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Keyboard Shortcuts")
        dialog.geometry("600x500")
        dialog.resizable(True, True)

        # Create scrollable frame
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, text="Keyboard Shortcuts", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Create treeview for shortcuts
        columns = ("Shortcut", "Description")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

        # Define headings
        tree.heading("Shortcut", text="Shortcut")
        tree.heading("Description", text="Description")

        # Configure column widths
        tree.column("Shortcut", width=200)
        tree.column("Description", width=350)

        # Add shortcuts to tree
        for shortcut, info in sorted(self.shortcuts.items()):
            tree.insert("", tk.END, values=(shortcut, info["description"]))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Close button
        close_button = ttk.Button(main_frame, text="Close", command=dialog.destroy)
        close_button.pack(pady=(10, 0))

        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()

    def save_shortcuts(self, filepath: str) -> None:
        """Save current shortcuts to a JSON file."""
        shortcuts_to_save = {}
        for combo, info in self.shortcuts.items():
            if "callback" not in info:  # Don't save callback functions
                shortcuts_to_save[combo] = info

        with open(filepath, "w") as f:
            json.dump(shortcuts_to_save, f, indent=2)

    def load_shortcuts(self, filepath: str) -> None:
        """Load shortcuts from a JSON file (descriptions only)."""
        try:
            with open(filepath, "r") as f:
                loaded_shortcuts = json.load(f)
                for combo, info in loaded_shortcuts.items():
                    if combo in self.shortcuts:
                        self.shortcuts[combo]["description"] = info.get(
                            "description", ""
                        )
        except Exception as e:
            print(f"Error loading shortcuts from {filepath}: {e}")


class StandardKeyboardShortcuts:
    """Standard keyboard shortcut implementations for common actions."""

    def __init__(self, app_instance):
        self.app = app_instance

    def open_file(self, event=None):
        """Standard open file action."""
        if hasattr(self.app, "open_file"):
            self.app.open_file()
        elif hasattr(self.app, "load_config"):
            self.app.load_config()

    def save_file(self, event=None):
        """Standard save file action."""
        if hasattr(self.app, "save_file"):
            self.app.save_file()
        elif hasattr(self.app, "export_data"):
            self.app.export_data()

    def save_as(self, event=None):
        """Standard save as action."""
        if hasattr(self.app, "save_as"):
            self.app.save_as()

    def quit(self, event=None):
        """Standard quit action."""
        if hasattr(self.app, "quit"):
            self.app.quit()
        elif hasattr(self.app, "on_closing"):
            self.app.on_closing()
        else:
            self.app.root.destroy()

    def undo(self, event=None):
        """Standard undo action."""
        if hasattr(self.app, "undo"):
            self.app.undo()

    def redo(self, event=None):
        """Standard redo action."""
        if hasattr(self.app, "redo"):
            self.app.redo()

    def copy(self, event=None):
        """Standard copy action."""
        try:
            # Try to copy from focused widget
            focused = self.app.root.focus_get()
            if hasattr(focused, "selection_get"):
                focused.clipboard_clear()
                focused.clipboard_append(focused.selection_get())
        except:
            pass

    def paste(self, event=None):
        """Standard paste action."""
        try:
            # Try to paste to focused widget
            focused = self.app.root.focus_get()
            if hasattr(focused, "insert"):
                text = focused.clipboard_get()
                focused.insert(tk.INSERT, text)
        except:
            pass

    def run_experiment(self, event=None):
        """Run experiment action."""
        if hasattr(self.app, "run_experiment"):
            self.app.run_experiment()

    def clear_results(self, event=None):
        """Clear results action."""
        if hasattr(self.app, "clear_results"):
            self.app.clear_results()

    def export_data(self, event=None):
        """Export data action."""
        if hasattr(self.app, "export_data"):
            self.app.export_data()

    def load_config(self, event=None):
        """Load configuration action."""
        if hasattr(self.app, "load_config"):
            self.app.load_config()

    def show_help(self, event=None):
        """Show help action."""
        if hasattr(self.app, "show_help"):
            self.app.show_help()
        else:
            self.show_about_dialog()

    def show_about_dialog(self):
        """Show basic about dialog."""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("About")
        dialog.geometry("400x200")
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="APGI Framework GUI", font=("Arial", 14, "bold")).pack(
            pady=(0, 10)
        )
        ttk.Label(frame, text="Comprehensive Testing System").pack()
        ttk.Label(frame, text="").pack()
        ttk.Label(frame, text="Press Ctrl+H for keyboard shortcuts").pack()
        ttk.Label(frame, text="").pack()
        ttk.Button(frame, text="Close", command=dialog.destroy).pack()

        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.focus_set()


def setup_standard_shortcuts(app_instance, keyboard_manager: KeyboardManager) -> None:
    """Setup standard keyboard shortcuts for an application."""
    standard = StandardKeyboardShortcuts(app_instance)

    # File operations
    keyboard_manager.bind_shortcut("Ctrl+O", standard.open_file, "Open file")
    keyboard_manager.bind_shortcut("Ctrl+S", standard.save_file, "Save file")
    keyboard_manager.bind_shortcut("Ctrl+Shift+S", standard.save_as, "Save as")
    keyboard_manager.bind_shortcut("Ctrl+Q", standard.quit, "Quit application")

    # Edit operations
    keyboard_manager.bind_shortcut("Ctrl+Z", standard.undo, "Undo")
    keyboard_manager.bind_shortcut("Ctrl+Y", standard.redo, "Redo")
    keyboard_manager.bind_shortcut("Ctrl+C", standard.copy, "Copy")
    keyboard_manager.bind_shortcut("Ctrl+V", standard.paste, "Paste")

    # Application operations
    keyboard_manager.bind_shortcut("Ctrl+R", standard.run_experiment, "Run experiment")
    keyboard_manager.bind_shortcut("Ctrl+E", standard.export_data, "Export data")
    keyboard_manager.bind_shortcut("Ctrl+L", standard.load_config, "Load configuration")
    keyboard_manager.bind_shortcut(
        "Ctrl+Shift+C", standard.clear_results, "Clear results"
    )

    # Help
    keyboard_manager.bind_shortcut("F1", standard.show_help, "Show help")
    keyboard_manager.bind_shortcut(
        "Ctrl+H", keyboard_manager.show_shortcuts_dialog, "Show keyboard shortcuts"
    )
