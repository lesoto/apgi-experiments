"""
Advanced theme management system for APGI Framework GUI applications.

Provides comprehensive theming support for both tkinter and customtkinter
with automatic theme detection, widget tracking, and consistent styling.
"""

import json
import logging
import tkinter as tk
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

try:
    import customtkinter as ctk

    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None

logger = logging.getLogger(__name__)


@dataclass
class ThemeColors:
    """Color scheme definition for a theme."""

    name: str
    background: str
    foreground: str
    button_bg: str
    button_fg: str
    button_hover: str
    button_active: str
    entry_bg: str
    entry_fg: str
    entry_border: str
    frame_bg: str
    frame_border: str
    select_bg: str
    select_fg: str
    disabled_bg: str
    disabled_fg: str
    accent: str
    success: str
    warning: str
    error: str
    info: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ThemeFonts:
    """Font definitions for a theme."""

    family: str = "Segoe UI"
    size_small: int = 9
    size_normal: int = 11
    size_large: int = 13
    size_xlarge: int = 16
    weight_normal: str = "normal"
    weight_bold: str = "bold"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class AdvancedThemeManager:
    """
    Advanced theme management system with widget tracking and automatic updates.

    Supports both tkinter and customtkinter with comprehensive theme definitions
    and real-time theme switching.
    """

    def __init__(self, root_widget: tk.Widget):
        self.root = root_widget
        self.current_theme = "light"
        self.widget_registry: Dict[str, tk.Widget] = {}
        self.theme_callbacks: List[Callable] = []

        # Define built-in themes
        self.themes = self._create_builtin_themes()

        # Theme settings
        self.settings = {
            "auto_detect_system": True,
            "save_user_preferences": True,
            "animate_transitions": False,
            "track_all_widgets": True,
        }

        # Load user preferences
        self._load_user_preferences()

        # Detect system theme if enabled
        if self.settings["auto_detect_system"]:
            self._detect_and_apply_system_theme()

        logger.info(
            f"Advanced theme manager initialized with theme: {self.current_theme}"
        )

    def _create_builtin_themes(self) -> Dict[str, ThemeColors]:
        """Create built-in theme definitions."""
        return {
            "light": ThemeColors(
                name="Light",
                background="#ffffff",
                foreground="#000000",
                button_bg="#f0f0f0",
                button_fg="#000000",
                button_hover="#e0e0e0",
                button_active="#d0d0d0",
                entry_bg="#ffffff",
                entry_fg="#000000",
                entry_border="#cccccc",
                frame_bg="#fafafa",
                frame_border="#e0e0e0",
                select_bg="#0078d4",
                select_fg="#ffffff",
                disabled_bg="#f5f5f5",
                disabled_fg="#999999",
                accent="#0078d4",
                success="#107c10",
                warning="#ff8c00",
                error="#d13438",
                info="#0078d4",
            ),
            "dark": ThemeColors(
                name="Dark",
                background="#2d2d2d",
                foreground="#ffffff",
                button_bg="#404040",
                button_fg="#ffffff",
                button_hover="#505050",
                button_active="#606060",
                entry_bg="#2d2d2d",
                entry_fg="#ffffff",
                entry_border="#555555",
                frame_bg="#333333",
                frame_border="#555555",
                select_bg="#0078d4",
                select_fg="#ffffff",
                disabled_bg="#1e1e1e",
                disabled_fg="#666666",
                accent="#0078d4",
                success="#107c10",
                warning="#ff8c00",
                error="#d13438",
                info="#0078d4",
            ),
            "blue": ThemeColors(
                name="Blue",
                background="#f0f8ff",
                foreground="#000080",
                button_bg="#e6f3ff",
                button_fg="#000080",
                button_hover="#cce7ff",
                button_active="#b3daff",
                entry_bg="#ffffff",
                entry_fg="#000080",
                entry_border="#4169e1",
                frame_bg="#f5faff",
                frame_border="#b3daff",
                select_bg="#4169e1",
                select_fg="#ffffff",
                disabled_bg="#f0f0f0",
                disabled_fg="#999999",
                accent="#4169e1",
                success="#228b22",
                warning="#ff8c00",
                error="#dc143c",
                info="#4169e1",
            ),
            "high_contrast": ThemeColors(
                name="High Contrast",
                background="#000000",
                foreground="#ffffff",
                button_bg="#ffffff",
                button_fg="#000000",
                button_hover="#ffff00",
                button_active="#00ff00",
                entry_bg="#ffffff",
                entry_fg="#000000",
                entry_border="#ffffff",
                frame_bg="#000000",
                frame_border="#ffffff",
                select_bg="#ffffff",
                select_fg="#000000",
                disabled_bg="#404040",
                disabled_fg="#808080",
                accent="#ffff00",
                success="#00ff00",
                warning="#ffff00",
                error="#ff0000",
                info="#00ffff",
            ),
        }

    def _detect_and_apply_system_theme(self):
        """Detect system theme and apply it."""
        try:
            system_theme = self._get_system_theme()
            if system_theme and system_theme in self.themes:
                self.set_theme(system_theme, save_preference=False)
                logger.info(f"Applied system theme: {system_theme}")
        except Exception as e:
            logger.warning(f"Failed to detect system theme: {e}")

    def _get_system_theme(self) -> Optional[str]:
        """Get the system theme preference."""
        try:
            import platform

            system = platform.system()

            if system == "Windows":
                # Check Windows registry for theme preference
                try:
                    import winreg

                    with winreg.OpenKey(  # type: ignore
                        winreg.HKEY_CURRENT_USER,  # type: ignore
                        r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                    ) as key:
                        apps_use_light_theme = winreg.QueryValueEx(  # type: ignore
                            key, "AppsUseLightTheme"
                        )[0]
                        return "light" if apps_use_light_theme else "dark"
                except ImportError:
                    # winreg not available on this platform
                    pass
                except OSError:
                    # Registry access failed
                    pass
                except Exception:
                    # Other registry errors
                    pass

            elif system == "Darwin":  # macOS
                # Check macOS appearance preference
                try:
                    import subprocess

                    result = subprocess.run(
                        ["defaults", "read", "-g", "AppleInterfaceStyle"],
                        capture_output=True,
                        text=True,
                    )
                    return "dark" if "Dark" in result.stdout else "light"
                except (FileNotFoundError, subprocess.SubprocessError):
                    pass

            elif system == "Linux":
                # Try to detect from desktop environment
                try:
                    import subprocess

                    result = subprocess.run(
                        [
                            "gsettings",
                            "get",
                            "org.gnome.desktop.interface",
                            "gtk-theme",
                        ],
                        capture_output=True,
                        text=True,
                    )
                    if "dark" in result.stdout.lower():
                        return "dark"
                except (FileNotFoundError, subprocess.SubprocessError):
                    pass

            # Default to light theme
            return "light"

        except Exception as e:
            logger.warning(f"Failed to detect system theme: {e}")
            return "light"

    def register_widget(self, widget: tk.Widget, widget_id: Optional[str] = None):
        """
        Register a widget for theme tracking.

        Args:
            widget: Widget to register
            widget_id: Optional custom ID for the widget
        """
        if not self.settings["track_all_widgets"]:
            return

        if widget_id is None:
            widget_id = f"widget_{len(self.widget_registry)}"

        self.widget_registry[widget_id] = widget

        # Apply current theme to the widget
        self._apply_theme_to_widget(widget)

        # Recursively register child widgets
        for child in widget.winfo_children():
            self.register_widget(child, f"{widget_id}_child")

    def set_theme(self, theme_name: str, save_preference: bool = True):
        """
        Set the current theme.

        Args:
            theme_name: Name of the theme to apply
            save_preference: Whether to save this preference
        """
        if theme_name not in self.themes:
            logger.error(f"Unknown theme: {theme_name}")
            return False

        old_theme = self.current_theme
        self.current_theme = theme_name

        # Apply theme to all registered widgets
        self._apply_theme_to_all_widgets()

        # Apply theme to customtkinter if available
        if CUSTOMTKINTER_AVAILABLE:
            self._apply_customtkinter_theme()

        # Notify callbacks
        for callback in self.theme_callbacks:
            try:
                callback(old_theme, theme_name)
            except Exception as e:
                logger.error(f"Theme callback error: {e}")

        # Save preference if enabled
        if save_preference and self.settings["save_user_preferences"]:
            self._save_user_preferences()

        logger.info(f"Theme changed from {old_theme} to {theme_name}")
        return True

    def _apply_theme_to_all_widgets(self):
        """Apply current theme to all registered widgets."""
        colors = self.themes[self.current_theme]

        for widget_id, widget in self.widget_registry.items():
            try:
                self._apply_theme_to_widget(widget, colors)
            except Exception as e:
                logger.warning(f"Failed to apply theme to widget {widget_id}: {e}")

    def _apply_theme_to_widget(
        self, widget: tk.Widget, colors: Optional[ThemeColors] = None
    ):
        """Apply theme to a specific widget and its children."""
        if colors is None:
            colors = self.themes[self.current_theme]

        try:
            # Apply theme based on widget type
            if isinstance(widget, (tk.Frame, ttk.Frame)):
                widget.configure(bg=colors.background)  # type: ignore
            elif isinstance(widget, (tk.Label, ttk.Label)):
                widget.configure(bg=colors.background, fg=colors.foreground)  # type: ignore
            elif isinstance(widget, (tk.Button, ttk.Button)):
                widget.configure(
                    bg=colors.button_bg,
                    fg=colors.button_fg,
                    activebackground=colors.button_active,
                    activeforeground=colors.button_fg,
                )  # type: ignore
            elif isinstance(widget, (tk.Entry, ttk.Entry)):
                widget.configure(
                    bg=colors.entry_bg,
                    fg=colors.entry_fg,
                    insertbackground=colors.foreground,
                    selectbackground=colors.select_bg,
                    selectforeground=colors.select_fg,
                )  # type: ignore
            elif isinstance(widget, (tk.Text,)):
                widget.configure(
                    bg=colors.entry_bg,
                    fg=colors.entry_fg,
                    insertbackground=colors.foreground,
                    selectbackground=colors.select_bg,
                    selectforeground=colors.select_fg,
                )  # type: ignore
            elif isinstance(widget, (tk.Checkbutton, ttk.Checkbutton)):
                widget.configure(
                    bg=colors.background,
                    fg=colors.foreground,
                    selectcolor=colors.select_bg,
                    activebackground=colors.background,
                    activeforeground=colors.foreground,
                )  # type: ignore
            elif isinstance(widget, (tk.Radiobutton, ttk.Radiobutton)):
                widget.configure(
                    bg=colors.background,
                    fg=colors.foreground,
                    selectcolor=colors.select_bg,
                    activebackground=colors.background,
                    activeforeground=colors.foreground,
                )  # type: ignore
            elif isinstance(widget, (tk.Scale, ttk.Scale)):
                widget.configure(
                    bg=colors.background,
                    fg=colors.foreground,
                    troughcolor=colors.frame_bg,
                    activebackground=colors.accent,
                )  # type: ignore
            elif isinstance(widget, (tk.Listbox,)):
                widget.configure(
                    bg=colors.entry_bg,
                    fg=colors.entry_fg,
                    selectbackground=colors.select_bg,
                    selectforeground=colors.select_fg,
                )  # type: ignore
            elif isinstance(widget, (tk.Canvas,)):
                widget.configure(bg=colors.background)  # type: ignore

            # Apply to children recursively
            for child in widget.winfo_children():
                self._apply_theme_to_widget(child, colors)

        except Exception as e:
            logger.warning(f"Failed to apply theme to widget: {e}")

    def _apply_customtkinter_theme(self):
        """Apply theme to customtkinter components."""
        if not CUSTOMTKINTER_AVAILABLE:
            return

        try:
            if self.current_theme == "dark":
                ctk.set_appearance_mode("dark")
            elif self.current_theme == "light":
                ctk.set_appearance_mode("light")
            else:
                # For custom themes, default to light
                ctk.set_appearance_mode("light")

            # Set custom color theme if available
            self.themes[self.current_theme]  # Access to use the variable
            ctk.set_default_color_theme("blue")  # Use blue as base

        except Exception as e:
            logger.warning(f"Failed to apply customtkinter theme: {e}")

    def get_theme_colors(self) -> ThemeColors:
        """Get the current theme colors."""
        return self.themes[self.current_theme]

    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self.themes.keys())

    def add_theme_callback(self, callback: Callable):
        """Add a callback to be called when theme changes."""
        self.theme_callbacks.append(callback)

    def remove_theme_callback(self, callback: Callable):
        """Remove a theme change callback."""
        if callback in self.theme_callbacks:
            self.theme_callbacks.remove(callback)

    def create_custom_theme(self, name: str, colors: ThemeColors) -> bool:
        """
        Create a custom theme.

        Args:
            name: Name for the new theme
            colors: ThemeColors object with color definitions

        Returns:
            True if successful, False otherwise
        """
        try:
            self.themes[name] = colors
            logger.info(f"Created custom theme: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create custom theme {name}: {e}")
            return False

    def export_theme(self, theme_name: str, file_path: Path) -> bool:
        """
        Export a theme to a JSON file.

        Args:
            theme_name: Name of theme to export
            file_path: Path to save the theme file

        Returns:
            True if successful, False otherwise
        """
        try:
            if theme_name not in self.themes:
                logger.error(f"Theme not found: {theme_name}")
                return False

            theme_data = {
                "name": theme_name,
                "colors": self.themes[theme_name].to_dict(),
                "exported_at": datetime.now().isoformat(),
            }

            with open(file_path, "w") as f:
                json.dump(theme_data, f, indent=2)

            logger.info(f"Theme exported to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export theme {theme_name}: {e}")
            return False

    def import_theme(self, file_path: Path) -> bool:
        """
        Import a theme from a JSON file.

        Args:
            file_path: Path to the theme file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "r") as f:
                theme_data = json.load(f)

            colors = ThemeColors(**theme_data["colors"])
            theme_name = theme_data["name"]

            self.themes[theme_name] = colors
            logger.info(f"Theme imported from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to import theme from {file_path}: {e}")
            return False

    def _save_user_preferences(self):
        """Save user preferences to file."""
        try:
            preferences = {
                "current_theme": self.current_theme,
                "settings": self.settings,
                "saved_at": datetime.now().isoformat(),
            }

            # Save to user's home directory
            config_dir = Path.home() / ".apgi_framework"
            config_dir.mkdir(exist_ok=True)

            pref_file = config_dir / "theme_preferences.json"
            with open(pref_file, "w") as f:
                json.dump(preferences, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to save user preferences: {e}")

    def _load_user_preferences(self):
        """Load user preferences from file."""
        try:
            config_dir = Path.home() / ".apgi_framework"
            pref_file = config_dir / "theme_preferences.json"

            if pref_file.exists():
                with open(pref_file, "r") as f:
                    preferences = json.load(f)

                self.current_theme = preferences.get("current_theme", "light")
                self.settings.update(preferences.get("settings", {}))

                logger.info("User preferences loaded successfully")

        except Exception as e:
            logger.warning(f"Failed to load user preferences: {e}")

    def create_theme_selector(self, parent: tk.Widget) -> tk.Frame:
        """
        Create a theme selector widget.

        Args:
            parent: Parent widget

        Returns:
            Frame containing theme selector
        """
        frame = tk.Frame(parent)
        colors = self.get_theme_colors()
        frame.configure(bg=colors.background)

        tk.Label(frame, text="Theme:", bg=colors.background, fg=colors.foreground).pack(
            side=tk.LEFT, padx=5
        )

        theme_var = tk.StringVar(value=self.current_theme)
        theme_menu = ttk.Combobox(
            frame,
            textvariable=theme_var,
            values=self.get_available_themes(),
            state="readonly",
        )
        theme_menu.pack(side=tk.LEFT, padx=5)

        def on_theme_change(event=None):
            selected_theme = theme_var.get()
            if selected_theme != self.current_theme:
                self.set_theme(selected_theme)

        theme_menu.bind("<<ComboboxSelected>>", on_theme_change)

        # Auto-detect checkbox
        auto_var = tk.BooleanVar(value=self.settings["auto_detect_system"])
        auto_check = tk.Checkbutton(
            frame,
            text="Auto-detect system theme",
            variable=auto_var,
            bg=colors.background,
            fg=colors.foreground,
            command=lambda: self.update_setting("auto_detect_system", auto_var.get()),
        )
        auto_check.pack(side=tk.LEFT, padx=10)

        return frame

    def update_setting(self, setting_name: str, value: Any):
        """
        Update a theme setting and save preferences.

        Args:
            setting_name: Name of the setting to update
            value: New value for the setting
        """
        if setting_name in self.settings:
            self.settings[setting_name] = value
            self._save_user_preferences()
            logger.info(f"Updated theme setting {setting_name} = {value}")


def create_theme_manager(root_widget: tk.Widget) -> AdvancedThemeManager:
    """
    Convenience function to create an advanced theme manager.

    Args:
        root_widget: Root widget for the application

    Returns:
        AdvancedThemeManager instance
    """
    return AdvancedThemeManager(root_widget)
