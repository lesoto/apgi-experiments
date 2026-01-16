"""
Theme Manager for APGI Framework GUI

Provides comprehensive theme support including dark mode, light mode, and custom themes.
Supports both tkinter and customtkinter applications.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, Any, Optional, List, Union
import json
from pathlib import Path
import os


class ThemeManager:
    """Manages themes for GUI applications."""

    def __init__(self, app_instance: Union[tk.Tk, tk.Toplevel, ctk.CTk]):
        self.app = app_instance
        self.current_theme = "light"
        self.theme_configs = self._load_default_themes()
        self.theme_callbacks = []

    def _load_default_themes(self) -> Dict[str, Dict[str, Any]]:
        """Load default theme configurations."""
        return {
            "light": {
                "name": "Light Mode",
                "ctk_appearance": "light",
                "ctk_color_theme": "blue",
                "tkinter_theme": "clam",
                "colors": {
                    "bg": "#ffffff",
                    "fg": "#000000",
                    "select_bg": "#0078d4",
                    "select_fg": "#ffffff",
                    "button_bg": "#e1e1e1",
                    "button_fg": "#000000",
                    "entry_bg": "#ffffff",
                    "entry_fg": "#000000",
                    "frame_bg": "#f0f0f0",
                    "text_bg": "#ffffff",
                    "text_fg": "#000000",
                },
                "matplotlib_style": "seaborn-v0_8-whitegrid",
                "description": "Light theme with bright colors",
            },
            "dark": {
                "name": "Dark Mode",
                "ctk_appearance": "dark",
                "ctk_color_theme": "blue",
                "tkinter_theme": "clam",
                "colors": {
                    "bg": "#2b2b2b",
                    "fg": "#ffffff",
                    "select_bg": "#404040",
                    "select_fg": "#ffffff",
                    "button_bg": "#404040",
                    "button_fg": "#ffffff",
                    "entry_bg": "#3c3c3c",
                    "entry_fg": "#ffffff",
                    "frame_bg": "#333333",
                    "text_bg": "#2b2b2b",
                    "text_fg": "#ffffff",
                },
                "matplotlib_style": "dark_background",
                "description": "Dark theme with reduced eye strain",
            },
            "system": {
                "name": "System Theme",
                "ctk_appearance": "system",
                "ctk_color_theme": "blue",
                "tkinter_theme": "clam",
                "colors": {
                    "bg": "#f0f0f0",
                    "fg": "#000000",
                    "select_bg": "#0078d4",
                    "select_fg": "#ffffff",
                    "button_bg": "#e1e1e1",
                    "button_fg": "#000000",
                    "entry_bg": "#ffffff",
                    "entry_fg": "#000000",
                    "frame_bg": "#f0f0f0",
                    "text_bg": "#ffffff",
                    "text_fg": "#000000",
                },
                "matplotlib_style": "seaborn-v0_8-whitegrid",
                "description": "Follows system theme preference",
            },
            "high_contrast": {
                "name": "High Contrast",
                "ctk_appearance": "dark",
                "ctk_color_theme": "blue",
                "tkinter_theme": "clam",
                "colors": {
                    "bg": "#000000",
                    "fg": "#ffffff",
                    "select_bg": "#ffffff",
                    "select_fg": "#000000",
                    "button_bg": "#333333",
                    "button_fg": "#ffffff",
                    "entry_bg": "#111111",
                    "entry_fg": "#ffffff",
                    "frame_bg": "#1a1a1a",
                    "text_bg": "#000000",
                    "text_fg": "#ffffff",
                },
                "matplotlib_style": "dark_background",
                "description": "High contrast theme for accessibility",
            },
            "blue": {
                "name": "Blue Theme",
                "ctk_appearance": "dark",
                "ctk_color_theme": "blue",
                "tkinter_theme": "clam",
                "colors": {
                    "bg": "#1e3a8a",
                    "fg": "#ffffff",
                    "select_bg": "#3b82f6",
                    "select_fg": "#ffffff",
                    "button_bg": "#2563eb",
                    "button_fg": "#ffffff",
                    "entry_bg": "#1e40af",
                    "entry_fg": "#ffffff",
                    "frame_bg": "#1e3a8a",
                    "text_bg": "#1e3a8a",
                    "text_fg": "#ffffff",
                },
                "matplotlib_style": "dark_background",
                "description": "Blue-tinted dark theme",
            },
        }

    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self.theme_configs.keys())

    def get_theme_info(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific theme."""
        return self.theme_configs.get(theme_name)

    def set_theme(self, theme_name: str, apply_immediately: bool = True) -> bool:
        """Set the current theme."""
        if theme_name not in self.theme_configs:
            return False

        self.current_theme = theme_name

        if apply_immediately:
            self._apply_theme(theme_name)

        # Notify callbacks
        for callback in self.theme_callbacks:
            try:
                callback(theme_name, self.theme_configs[theme_name])
            except Exception as e:
                print(f"Error in theme callback: {e}")

        return True

    def _apply_theme(self, theme_name: str) -> None:
        """Apply theme to the application."""
        theme_config = self.theme_configs[theme_name]

        # Apply CustomTkinter theme if available
        try:
            import customtkinter as ctk

            if hasattr(ctk, "set_appearance_mode") and hasattr(self.app, "configure"):
                ctk.set_appearance_mode(theme_config.get("ctk_appearance", "light"))
                ctk.set_default_color_theme(theme_config.get("ctk_color_theme", "blue"))
        except ImportError:
            pass
        except Exception as e:
            print(f"Error applying CustomTkinter theme: {e}")

        # Apply tkinter theme for standard widgets
        if hasattr(self.app, "tk") or isinstance(self.app, (tk.Tk, tk.Toplevel)):
            try:
                style = ttk.Style()
                style.theme_use(theme_config.get("tkinter_theme", "clam"))

                # Configure colors
                colors = theme_config.get("colors", {})
                style.configure(
                    "TLabel",
                    background=colors.get("bg", "#ffffff"),
                    foreground=colors.get("fg", "#000000"),
                )
                style.configure(
                    "TButton",
                    background=colors.get("button_bg", "#e1e1e1"),
                    foreground=colors.get("button_fg", "#000000"),
                )
                style.configure(
                    "TEntry",
                    fieldbackground=colors.get("entry_bg", "#ffffff"),
                    foreground=colors.get("entry_fg", "#000000"),
                )
                style.configure("TFrame", background=colors.get("frame_bg", "#f0f0f0"))
                style.configure(
                    "TLabelframe", background=colors.get("frame_bg", "#f0f0f0")
                )
                style.configure(
                    "TLabelframe.Label", background=colors.get("frame_bg", "#f0f0f0")
                )

            except Exception as e:
                print(f"Error applying tkinter theme: {e}")

        # Apply matplotlib style if available
        try:
            import matplotlib.pyplot as plt

            matplotlib_style = theme_config.get("matplotlib_style", "default")
            plt.style.use(matplotlib_style)
        except ImportError:
            pass
        except Exception as e:
            print(f"Error applying matplotlib style: {e}")

    def toggle_dark_mode(self) -> str:
        """Toggle between light and dark mode."""
        if self.current_theme == "light":
            self.set_theme("dark")
        elif self.current_theme == "dark":
            self.set_theme("light")
        else:
            # If using a custom theme, toggle to light
            self.set_theme("light")

        return self.current_theme

    def get_current_theme(self) -> str:
        """Get the current theme name."""
        return self.current_theme

    def get_current_colors(self) -> Dict[str, str]:
        """Get colors for the current theme."""
        return self.theme_configs.get(self.current_theme, {}).get("colors", {})

    def add_theme_callback(self, callback: callable) -> None:
        """Add a callback to be called when theme changes."""
        self.theme_callbacks.append(callback)

    def remove_theme_callback(self, callback: callable) -> None:
        """Remove a theme callback."""
        if callback in self.theme_callbacks:
            self.theme_callbacks.remove(callback)

    def save_theme_preference(self, filepath: str) -> None:
        """Save current theme preference to file."""
        preference = {
            "current_theme": self.current_theme,
            "last_updated": str(datetime.now()) if "datetime" in globals() else None,
        }

        try:
            with open(filepath, "w") as f:
                json.dump(preference, f, indent=2)
        except Exception as e:
            print(f"Error saving theme preference: {e}")

    def load_theme_preference(self, filepath: str) -> Optional[str]:
        """Load theme preference from file."""
        try:
            with open(filepath, "r") as f:
                preference = json.load(f)
                return preference.get("current_theme")
        except Exception as e:
            print(f"Error loading theme preference: {e}")
            return None

    def create_theme_menu(self, menu_bar: tk.Menu) -> None:
        """Create a theme menu in the menu bar."""
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=theme_menu)
        theme_menu.add_command(label="Theme", state="disabled")
        theme_menu.add_separator()

        # Add theme options
        for theme_name, theme_config in self.theme_configs.items():
            theme_menu.add_radiobutton(
                label=theme_config["name"],
                value=theme_name,
                variable=tk.StringVar(value=self.current_theme),
                command=lambda t=theme_name: self.set_theme(t),
            )

        theme_menu.add_separator()
        theme_menu.add_command(
            label="Toggle Dark Mode",
            command=self.toggle_dark_mode,
            accelerator="Ctrl+D",
        )

    def create_theme_selector(
        self, parent: Union[tk.Widget, ctk.CTkWidget]
    ) -> Union[tk.Widget, ctk.CTkWidget]:
        """Create a theme selector widget."""
        try:
            import customtkinter as ctk
        except ImportError:
            ctk = None

        if ctk and (hasattr(parent, "_ctk_tk") or isinstance(parent, ctk.CTkBaseClass)):
            # CustomTkinter combobox
            import customtkinter as ctk

            theme_names = [config["name"] for config in self.theme_configs.values()]
            theme_values = list(self.theme_configs.keys())

            current_index = (
                theme_values.index(self.current_theme)
                if self.current_theme in theme_values
                else 0
            )

            combobox = ctk.CTkComboBox(
                parent, values=theme_names, command=self._on_combobox_change
            )
            combobox.set(theme_names[current_index])
            combobox.theme_values = theme_values  # Store mapping

            return combobox
        else:
            # tkinter combobox
            import tkinter as tk
            from tkinter import ttk

            theme_names = [config["name"] for config in self.theme_configs.values()]
            theme_values = list(self.theme_configs.keys())

            current_index = (
                theme_values.index(self.current_theme)
                if self.current_theme in theme_values
                else 0
            )

            combobox = ttk.Combobox(parent, values=theme_names, state="readonly")
            combobox.current(current_index)
            combobox.theme_values = theme_values  # Store mapping
            combobox.bind("<<ComboboxSelected>>", self._on_combobox_change)

            return combobox

    def _on_combobox_change(self, event_or_value) -> None:
        """Handle combobox selection change."""
        if hasattr(event_or_value, "get"):  # CustomTkinter
            selected_name = event_or_value.get()
            theme_values = event_or_value.theme_values
        else:  # tkinter
            combobox = event_or_value.widget
            selected_name = combobox.get()
            theme_values = combobox.theme_values

        # Find corresponding theme value
        theme_names = [config["name"] for config in self.theme_configs.values()]
        if selected_name in theme_names:
            index = theme_names.index(selected_name)
            theme_name = theme_values[index]
            self.set_theme(theme_name)

    def apply_theme_to_widget(
        self, widget: Union[tk.Widget, ctk.CTkWidget], widget_type: str = "default"
    ) -> None:
        """Apply current theme colors to a specific widget."""
        colors = self.get_current_colors()

        try:
            import customtkinter as ctk
        except ImportError:
            ctk = None

        if ctk and isinstance(widget, ctk.CTkBaseClass):
            # CustomTkinter widgets are automatically themed
            pass
        else:
            # tkinter widgets need manual color application
            try:
                if widget_type == "label":
                    widget.config(
                        bg=colors.get("bg", "#ffffff"), fg=colors.get("fg", "#000000")
                    )
                elif widget_type == "button":
                    widget.config(
                        bg=colors.get("button_bg", "#e1e1e1"),
                        fg=colors.get("button_fg", "#000000"),
                    )
                elif widget_type == "entry":
                    widget.config(
                        bg=colors.get("entry_bg", "#ffffff"),
                        fg=colors.get("entry_fg", "#000000"),
                    )
                elif widget_type == "frame":
                    widget.config(bg=colors.get("frame_bg", "#f0f0f0"))
                elif widget_type == "text":
                    widget.config(
                        bg=colors.get("text_bg", "#ffffff"),
                        fg=colors.get("text_fg", "#000000"),
                    )
                else:
                    # Default styling
                    widget.config(
                        bg=colors.get("bg", "#ffffff"), fg=colors.get("fg", "#000000")
                    )
            except Exception as e:
                print(f"Error applying theme to widget: {e}")


def get_system_theme_preference() -> str:
    """Get system theme preference (light/dark)."""
    try:
        import platform

        system = platform.system()

        if system == "Darwin":  # macOS
            import subprocess

            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
            )
            return "dark" if "Dark" in result.stdout else "light"

        elif system == "Windows":  # Windows
            try:
                import winreg

                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                ) as key:
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    return "dark" if value == 0 else "light"
            except:
                pass

        # Linux/other - check environment variables
        if os.environ.get("GTK_THEME", "").lower().find("dark") != -1:
            return "dark"

    except Exception:
        pass

    return "light"  # Default to light


def create_theme_dialog(
    parent: Union[tk.Widget, ctk.CTkWidget], theme_manager: ThemeManager
) -> tk.Toplevel:
    """Create a theme selection dialog."""
    dialog = tk.Toplevel(parent)
    dialog.title("Select Theme")
    dialog.geometry("500x400")
    dialog.resizable(False, False)

    # Make dialog modal
    dialog.transient(
        parent.winfo_toplevel() if hasattr(parent, "winfo_toplevel") else parent
    )
    dialog.grab_set()

    # Main frame
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="Select Theme", font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 20))

    # Theme descriptions
    theme_frame = ttk.Frame(main_frame)
    theme_frame.pack(fill=tk.BOTH, expand=True)

    # Create radio buttons for each theme
    theme_var = tk.StringVar(value=theme_manager.get_current_theme())

    for theme_name, theme_config in theme_manager.theme_configs.items():
        # Create frame for this theme
        theme_option_frame = ttk.Frame(theme_frame)
        theme_option_frame.pack(fill=tk.X, pady=5)

        # Radio button
        radio = ttk.Radiobutton(
            theme_option_frame,
            text=theme_config["name"],
            value=theme_name,
            variable=theme_var,
            command=lambda t=theme_name: theme_manager.set_theme(t),
        )
        radio.pack(side=tk.LEFT)

        # Description
        desc_label = ttk.Label(theme_option_frame, text=theme_config["description"])
        desc_label.pack(side=tk.LEFT, padx=(20, 0))

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=(20, 0))

    close_button = ttk.Button(button_frame, text="Close", command=dialog.destroy)
    close_button.pack()

    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

    return dialog
