"""
Unified Theme Manager for APGI Framework GUI Applications
=========================================================

This module provides backward compatibility while consolidating all theme management
functionality into the advanced theme manager from apgi_gui.components.theme_manager.

LEGACY NOTICE: This module provides compatibility wrappers for the old theme managers.
New code should import directly from apgi_gui.components.theme_manager.
"""

import warnings
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

# Import the advanced theme manager as the canonical implementation
try:
    from apgi_gui.components.theme_manager import (
        AdvancedThemeManager,
        ThemeColors,
        ThemeFonts,
        create_theme_manager,
    )
except ImportError as e:
    raise ImportError(
        "Failed to import advanced theme manager. Please ensure apgi_gui.components.theme_manager is available."
    ) from e

if TYPE_CHECKING:
    import tkinter as tk


class ThemeManager:
    """
    Backward compatibility wrapper for the legacy ThemeManager interface.

    This class provides the same API as the old theme managers but delegates
    to the advanced theme manager internally.

    DEPRECATED: Use apgi_gui.components.theme_manager.AdvancedThemeManager directly.
    """

    def __init__(
        self, app_instance: Union["tk.Tk", "tk.Toplevel"], initial_theme: str = "normal"
    ):
        warnings.warn(
            "ThemeManager is deprecated. Use AdvancedThemeManager from apgi_gui.components.theme_manager instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Map old theme names to new theme names
        theme_mapping = {
            "normal": "light",
            "light": "light",
            "dark": "dark",
            "high_contrast": "high_contrast",
        }

        mapped_theme = theme_mapping.get(initial_theme.lower(), "light")

        # Create the advanced theme manager
        self._advanced_manager = AdvancedThemeManager(app_instance)
        self._advanced_manager.set_theme(mapped_theme, save_preference=False)

        # Store legacy compatibility data
        self.app = app_instance
        self.theme_callbacks: List[Callable[..., Any]] = []
        self.font_scale = 1.0
        self.custom_themes: Dict[str, Dict[str, Any]] = {}

    def _define_themes(self) -> Dict[str, Dict[str, str]]:
        """Define legacy theme colors for backward compatibility."""
        return {
            "normal": {
                "bg": "#ffffff",
                "fg": "#000000",
                "select_bg": "#0078d4",
                "select_fg": "#ffffff",
                "button_bg": "#f0f0f0",
                "button_fg": "#000000",
                "border": "#cccccc",
            },
            "dark": {
                "bg": "#2d2d2d",
                "fg": "#ffffff",
                "select_bg": "#404040",
                "select_fg": "#ffffff",
                "button_bg": "#404040",
                "button_fg": "#ffffff",
                "border": "#555555",
            },
            "high_contrast": {
                "bg": "#000000",
                "fg": "#ffffff",
                "select_bg": "#ffffff",
                "select_fg": "#000000",
                "button_bg": "#ffffff",
                "button_fg": "#000000",
                "border": "#ffffff",
            },
        }

    def get_available_themes(self) -> List[str]:
        """Get list of available theme names (legacy format)."""
        # Map new theme names back to legacy names
        new_to_legacy = {
            "light": "normal",
            "dark": "dark",
            "blue": "normal",  # Map blue theme to normal for compatibility
            "high_contrast": "high_contrast",
        }

        new_themes = self._advanced_manager.get_available_themes()
        legacy_themes = []
        for theme in new_themes:
            legacy_theme = new_to_legacy.get(theme, theme)
            if legacy_theme not in legacy_themes:
                legacy_themes.append(legacy_theme)

        return legacy_themes

    def set_theme(self, theme_name: str, apply_immediately: bool = True) -> bool:
        """Set the current theme (legacy interface)."""
        # Map legacy theme names to new ones
        theme_mapping = {
            "normal": "light",
            "light": "light",
            "dark": "dark",
            "high_contrast": "high_contrast",
            "blue": "light",  # Map blue to light for compatibility
            "system": "light",  # Map system to light for now
        }

        mapped_theme = theme_mapping.get(theme_name.lower(), "light")

        success = self._advanced_manager.set_theme(mapped_theme, save_preference=True)

        # Notify callbacks using legacy interface
        if success:
            for callback in self.theme_callbacks:
                try:
                    callback(theme_name, self._get_legacy_theme_config(theme_name))
                except Exception as e:
                    print(f"Error in theme callback: {e}")

        return success

    def _get_legacy_theme_config(self, theme_name: str) -> Dict[str, Any]:
        """Get legacy theme configuration for compatibility."""
        themes = self._define_themes()
        base_config = themes.get(theme_name.lower(), themes["normal"])

        return {
            "name": theme_name.title(),
            "colors": base_config,
            "description": f"Legacy {theme_name} theme",
        }

    def get_theme_color(self, color_type: str) -> str:
        """Get a color value from the current theme."""
        current_colors = self._advanced_manager.get_theme_colors()

        # Map new color names to legacy ones
        color_mapping = {
            "bg": "background",
            "fg": "foreground",
            "select_bg": "select_bg",
            "select_fg": "select_fg",
            "button_bg": "button_bg",
            "button_fg": "button_fg",
            "border": "frame_border",
        }

        new_color_type = color_mapping.get(color_type, color_type)

        if hasattr(current_colors, new_color_type):
            return getattr(current_colors, new_color_type)
        elif hasattr(current_colors, color_type):
            return getattr(current_colors, color_type)
        else:
            return "#000000"  # Default fallback

    def get_current_theme(self) -> str:
        """Get the name of the current theme (legacy format)."""
        current = self._advanced_manager.current_theme

        # Map new theme names back to legacy
        new_to_legacy = {
            "light": "normal",
            "dark": "dark",
            "blue": "normal",
            "high_contrast": "high_contrast",
        }

        return new_to_legacy.get(current, current)

    def apply_theme_to_widget(self, widget: "tk.Widget", **overrides):
        """Apply the current theme to a tkinter widget."""
        self._advanced_manager.register_widget(widget)

    def create_theme_selector(self, parent) -> Any:
        """Create a theme selector widget."""
        return self._advanced_manager.create_theme_selector(parent)

    def add_theme_callback(self, callback: Callable[..., Any]) -> None:
        """Add a callback to be called when theme changes."""
        self.theme_callbacks.append(callback)
        # Also add to advanced manager
        self._advanced_manager.add_theme_callback(callback)

    def remove_theme_callback(self, callback: Callable[..., Any]) -> None:
        """Remove a theme callback."""
        if callback in self.theme_callbacks:
            self.theme_callbacks.remove(callback)
        self._advanced_manager.remove_theme_callback(callback)

    # Additional compatibility methods for the utils theme manager interface
    def get_theme_info(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific theme."""
        return self._get_legacy_theme_config(theme_name)

    def toggle_dark_mode(self) -> str:
        """Toggle between light and dark mode."""
        current = self.get_current_theme()
        if current == "normal":
            self.set_theme("dark")
            return "dark"
        else:
            self.set_theme("normal")
            return "normal"

    def get_current_colors(self) -> Dict[str, str]:
        """Get colors for the current theme."""
        themes = self._define_themes()
        return themes.get(self.get_current_theme(), themes["normal"])

    def set_font_scale(self, scale: float) -> None:
        """Set font scaling factor (no-op in compatibility mode)."""
        self.font_scale = max(0.5, min(3.0, scale))
        # Font scaling not implemented in compatibility mode

    def get_font_scale(self) -> float:
        """Get current font scaling factor."""
        return self.font_scale

    def create_custom_theme(
        self, name: str, base_theme: str = "normal", **customizations
    ) -> bool:
        """Create a custom theme (limited compatibility)."""
        # For now, just return False as custom themes aren't fully supported in compatibility mode
        warnings.warn(
            "Custom theme creation is limited in compatibility mode.", UserWarning
        )
        return False

    def save_theme_preference(self, filepath: str) -> None:
        """Save current theme preference to file."""
        try:
            import json
            from datetime import datetime

            preference = {
                "current_theme": self.get_current_theme(),
                "last_updated": str(datetime.now()),
            }

            with open(filepath, "w") as f:
                json.dump(preference, f, indent=2)
        except Exception as e:
            print(f"Error saving theme preference: {e}")

    def load_theme_preference(self, filepath: str) -> Optional[str]:
        """Load theme preference from file."""
        try:
            import json

            with open(filepath, "r") as f:
                preference = json.load(f)
                return preference.get("current_theme")
        except Exception as e:
            print(f"Error loading theme preference: {e}")
            return None


def get_system_theme_preference() -> str:
    """Get system theme preference (light/dark)."""
    return "light"  # Simplified for compatibility


def create_theme_dialog(parent, theme_manager: ThemeManager) -> "tk.Toplevel":
    """Create a theme selection dialog (compatibility wrapper)."""
    import tkinter as tk
    from tkinter import ttk

    dialog = tk.Toplevel(parent)
    dialog.title("Select Theme")
    dialog.geometry("400x300")
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

    # Theme selection
    theme_var = tk.StringVar(value=theme_manager.get_current_theme())

    for theme_name in theme_manager.get_available_themes():
        radio = ttk.Radiobutton(
            main_frame,
            text=theme_name.title(),
            value=theme_name,
            variable=theme_var,
            command=lambda t=theme_name: theme_manager.set_theme(t),
        )
        radio.pack(anchor=tk.W, pady=2)

    # Close button
    close_button = ttk.Button(main_frame, text="Close", command=dialog.destroy)
    close_button.pack(pady=(20, 0))

    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

    return dialog


# Export the main classes for backward compatibility
__all__ = [
    "ThemeManager",
    "AdvancedThemeManager",
    "ThemeColors",
    "ThemeFonts",
    "create_theme_manager",
    "get_system_theme_preference",
    "create_theme_dialog",
]
