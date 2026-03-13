"""
Tooltip utility for APGI Framework GUIs.

Provides consistent tooltip implementation across all GUI applications.
"""

import tkinter as tk
from typing import Optional


class Tooltip:
    """Tooltip widget for tkinter GUIs."""

    def __init__(self, widget: tk.Widget, text: str, delay: float = 0.5):
        """
        Initialize tooltip.

        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text
            delay: Delay in seconds before showing tooltip
        """
        self.widget = widget
        self.text = text
        self.delay = delay * 1000  # Convert to milliseconds
        self.tip_window: Optional[tk.Toplevel] = None
        self.tip_id: Optional[str] = None

        # Bind events
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None) -> None:
        """Show tooltip when mouse enters widget."""
        self._schedule_tooltip()

    def _on_leave(self, event=None) -> None:
        """Hide tooltip when mouse leaves widget."""
        self._hide_tooltip()
        if self.tip_id:
            self.widget.after_cancel(self.tip_id)
            self.tip_id = None

    def _schedule_tooltip(self) -> None:
        """Schedule tooltip to appear after delay."""
        if self.tip_id:
            self.widget.after_cancel(self.tip_id)
        self.tip_id = self.widget.after(int(self.delay), self._show_tooltip)

    def _show_tooltip(self) -> None:
        """Show the tooltip window."""
        if self.tip_window or not self.text:
            return

        # Get widget position
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            padx=5,
            pady=2,
            font=("tahoma", 8, "normal"),
        )
        label.pack(ipadx=1)

    def _hide_tooltip(self) -> None:
        """Hide the tooltip window."""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def add_tooltip(widget: tk.Widget, text: str, delay: float = 0.5) -> Tooltip:
    """
    Add a tooltip to a widget.

    Args:
        widget: Widget to add tooltip to
        text: Tooltip text
        delay: Delay in seconds before showing tooltip

    Returns:
        Tooltip instance
    """
    return Tooltip(widget, text, delay)


def add_tooltips_to_widgets(widgets: dict) -> None:
    """
    Add tooltips to multiple widgets.

    Args:
        widgets: Dictionary mapping widgets to tooltip texts
    """
    for widget, text in widgets.items():
        if text:
            add_tooltip(widget, text)


# Common tooltip texts for UI elements
TOOLTIP_TEXTS = {
    # Buttons
    "run": "Run the selected experiment",
    "stop": "Stop the current experiment",
    "save": "Save current results",
    "load": "Load saved results",
    "export": "Export results to file",
    "settings": "Open settings dialog",
    "help": "Show help documentation",
    "quit": "Exit the application",
    # Menu items
    "file_new": "Create new experiment",
    "file_open": "Open existing experiment",
    "file_save": "Save current experiment",
    "file_export": "Export experiment data",
    # Parameters
    "trials": "Number of trials to run",
    "participants": "Number of participants",
    "threshold": "Ignition threshold value",
    "precision": "Precision parameter",
    # Actions
    "analyze": "Analyze experiment results",
    "visualize": "Visualize data",
    "report": "Generate report",
}
