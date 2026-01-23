"""
Theme Toggle UI Component for APGI Framework

Provides a user-friendly interface for runtime theme switching with preview capabilities.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path

try:
    from ..utils.theme_manager import ThemeManager

    THEME_MANAGER_AVAILABLE = True
except ImportError:
    THEME_MANAGER_AVAILABLE = False
    ThemeManager = None


class ThemeToggleWidget:
    """A widget for switching themes with preview capabilities."""

    def __init__(
        self,
        parent,
        theme_manager: Optional[ThemeManager] = None,
        on_theme_change: Optional[Callable[[str], None]] = None,
    ):
        self.parent = parent
        self.theme_manager = theme_manager
        self.on_theme_change = on_theme_change
        self.current_theme = theme_manager.current_theme if theme_manager else "light"

        # Create the toggle widget
        self.frame = None
        self.theme_var = tk.StringVar(value=self.current_theme)
        self.create_widget()

    def create_widget(self):
        """Create the theme toggle widget."""
        if not THEME_MANAGER_AVAILABLE or not self.theme_manager:
            # Fallback simple toggle
            self.frame = ttk.Frame(self.parent)
            ttk.Label(self.frame, text="Theme:").pack(side=tk.LEFT, padx=5)

            self.simple_toggle = ttk.Checkbutton(
                self.frame, text="Dark Mode", command=self._simple_toggle_theme
            )
            self.simple_toggle.pack(side=tk.LEFT, padx=5)
            return

        # Full theme selector
        self.frame = ttk.LabelFrame(self.parent, text="Theme Selection", padding=10)

        # Theme dropdown
        theme_frame = ttk.Frame(self.frame)
        theme_frame.pack(fill=tk.X, pady=5)

        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=(0, 5))

        self.theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=self.theme_manager.get_available_themes(),
            state="readonly",
            width=15,
        )
        self.theme_combo.pack(side=tk.LEFT, padx=5)
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_selected)

        # Quick toggle buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="☀️ Light",
            command=lambda: self._set_theme("light"),
            width=10,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="🌙 Dark",
            command=lambda: self._set_theme("dark"),
            width=10,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="🔵 Blue",
            command=lambda: self._set_theme("blue"),
            width=10,
        ).pack(side=tk.LEFT, padx=2)

        # Theme preview
        self._create_preview_area()

        # Apply button
        ttk.Button(
            self.frame, text="Apply Theme", command=self._apply_current_theme
        ).pack(pady=10)

    def _create_preview_area(self):
        """Create a small preview area showing theme colors."""
        preview_frame = ttk.LabelFrame(self.frame, text="Preview", padding=5)
        preview_frame.pack(fill=tk.X, pady=5)

        self.preview_canvas = tk.Canvas(preview_frame, height=60, bg="white")
        self.preview_canvas.pack(fill=tk.X, pady=2)

        self._update_preview()

    def _update_preview(self):
        """Update the theme preview."""
        if not self.theme_manager:
            return

        theme_info = self.theme_manager.get_theme_info(self.current_theme)
        if not theme_info:
            return

        colors = theme_info.get("colors", {})

        # Clear canvas
        self.preview_canvas.delete("all")

        # Draw color swatches
        width = self.preview_canvas.winfo_reqwidth() or 300
        swatch_width = width // 4

        color_keys = ["bg", "fg", "button_bg", "select_bg"]
        for i, key in enumerate(color_keys):
            color = colors.get(key, "#ffffff")
            x1 = i * swatch_width
            x2 = (i + 1) * swatch_width

            self.preview_canvas.create_rectangle(
                x1, 10, x2, 50, fill=color, outline="gray"
            )

            # Add label
            text_color = "white" if self._is_dark_color(color) else "black"
            self.preview_canvas.create_text(
                x1 + swatch_width // 2,
                30,
                text=key.replace("_", " ").title(),
                fill=text_color,
                font=("Arial", 8),
            )

    def _is_dark_color(self, color: str) -> bool:
        """Check if a color is dark (for text contrast)."""
        try:
            # Remove # if present
            color = color.lstrip("#")
            # Convert to RGB
            r, g, b = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
            # Calculate luminance
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return luminance < 0.5
        except:
            return False

    def _on_theme_selected(self, event=None):
        """Handle theme selection from dropdown."""
        new_theme = self.theme_var.get()
        self._set_theme(new_theme, apply=False)

    def _set_theme(self, theme_name: str, apply: bool = False):
        """Set the current theme."""
        if (
            not self.theme_manager
            or theme_name not in self.theme_manager.get_available_themes()
        ):
            return

        self.current_theme = theme_name
        self.theme_var.set(theme_name)
        self._update_preview()

        if apply:
            self._apply_current_theme()

    def _apply_current_theme(self):
        """Apply the currently selected theme."""
        if self.theme_manager:
            success = self.theme_manager.set_theme(self.current_theme)
            if success and self.on_theme_change:
                self.on_theme_change(self.current_theme)

    def _simple_toggle_theme(self):
        """Simple theme toggle for fallback mode."""
        # This is a basic implementation for when theme manager is not available
        if self.on_theme_change:
            current = "dark" if self.current_theme == "light" else "light"
            self.current_theme = current
            self.on_theme_change(current)

    def get_widget(self):
        """Get the main widget frame."""
        return self.frame

    def pack(self, **kwargs):
        """Pack the widget."""
        if self.frame:
            self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the widget."""
        if self.frame:
            self.frame.grid(**kwargs)


class ThemeToggleDialog:
    """A dialog window for theme selection."""

    def __init__(self, parent, theme_manager: Optional[ThemeManager] = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.result = None

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Theme Settings")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)

        # Make it modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self._center_dialog()

        # Create content
        self._create_content()

        # Handle close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()

        # Get parent position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        # Calculate center position
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.dialog.geometry(f"+{x}+{y}")

    def _create_content(self):
        """Create the dialog content."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, text="Choose Theme", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Theme toggle widget
        self.theme_toggle = ThemeToggleWidget(
            main_frame,
            theme_manager=self.theme_manager,
            on_theme_change=self._on_theme_change,
        )
        self.theme_toggle.pack(fill=tk.X, pady=10)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(
            side=tk.RIGHT
        )

    def _on_theme_change(self, theme_name: str):
        """Handle theme change."""
        self.result = theme_name

    def _on_ok(self):
        """Handle OK button."""
        if self.theme_toggle:
            self.theme_toggle._apply_current_theme()
        self.dialog.destroy()

    def _on_cancel(self):
        """Handle Cancel button."""
        self.result = None
        self.dialog.destroy()

    def show(self) -> Optional[str]:
        """Show the dialog and return the selected theme."""
        self.dialog.wait_window()
        return self.result


# Convenience functions
def create_theme_toggle(parent, theme_manager=None, **kwargs) -> ThemeToggleWidget:
    """Create a theme toggle widget."""
    return ThemeToggleWidget(parent, theme_manager, **kwargs)


def show_theme_dialog(parent, theme_manager=None) -> Optional[str]:
    """Show a theme selection dialog."""
    dialog = ThemeToggleDialog(parent, theme_manager)
    return dialog.show()
