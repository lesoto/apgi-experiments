"""
Loading Indicator for APGI Framework GUI

Provides loading indicators for slow async operations in the GUI.
Prevents UI freezing and provides visual feedback to users.
"""

import threading
import tkinter as tk
from tkinter import ttk, TclError
from typing import Callable, Optional


class LoadingIndicator:
    """Manages loading indicators for slow operations."""

    def __init__(self, parent: tk.Widget):
        """Initialize loading indicator.

        Args:
            parent: Parent widget for the loading indicator
        """
        self.parent = parent
        self.loading_window: Optional[tk.Toplevel] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.status_label: Optional[ttk.Label] = None
        self._cancel_requested = False

    def show_loading(
        self,
        message: str = "Processing...",
        title: str = "Please Wait",
        show_progress: bool = False,
        cancelable: bool = False,
    ) -> None:
        """Show loading indicator window.

        Args:
            message: Status message to display
            title: Window title
            show_progress: Whether to show a progress bar
            cancelable: Whether to allow cancellation
        """
        # Don't create multiple loading windows
        if self.loading_window is not None:
            return

        # Create loading window
        self.loading_window = tk.Toplevel(self.parent)
        self.loading_window.title(title)  # type: ignore
        self.loading_window.resizable(False, False)  # type: ignore
        self.loading_window.transient(self.parent)  # type: ignore
        self.loading_window.grab_set()  # type: ignore

        # Center the window
        self.loading_window.update_idletasks()  # type: ignore
        width = 300
        height = 100 if not show_progress else 120
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - height) // 2
        self.loading_window.geometry(f"{width}x{height}+{x}+{y}")  # type: ignore

        # Status label
        self.status_label = ttk.Label(  # type: ignore
            self.loading_window,
            text=message,
            wraplength=280,
            justify=tk.CENTER,
        )
        self.status_label.pack(pady=10, padx=10)  # type: ignore

        # Progress bar (optional)
        if show_progress:
            self.progress_bar = ttk.Progressbar(  # type: ignore
                self.loading_window,
                mode="indeterminate",
                length=250,
            )
            self.progress_bar.pack(pady=5)  # type: ignore
            self.progress_bar.start(10)  # type: ignore

        # Cancel button (optional)
        if cancelable:
            cancel_btn = ttk.Button(
                self.loading_window,
                text="Cancel",
                command=self._on_cancel,
            )
            cancel_btn.pack(pady=5)

        # Make window modal
        self.loading_window.protocol(
            "WM_DELETE_WINDOW", self._on_cancel if cancelable else None
        )

        # Reset cancel flag
        self._cancel_requested = False

    def update_message(self, message: str) -> None:
        """Update the status message.

        Args:
            message: New status message
        """
        if self.status_label:
            self.status_label.config(text=message)
            self.loading_window.update_idletasks()  # type: ignore

    def update_progress(self, value: float, maximum: float = 100) -> None:
        """Update progress bar (if in determinate mode).

        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        if self.progress_bar:
            self.progress_bar["mode"] = "determinate"
            self.progress_bar["maximum"] = maximum
            self.progress_bar["value"] = value
            self.loading_window.update_idletasks()  # type: ignore

    def is_cancelled(self) -> bool:
        """Check if operation was cancelled.

        Returns:
            True if cancellation was requested
        """
        return self._cancel_requested

    def _on_cancel(self) -> None:
        """Handle cancel request."""
        self._cancel_requested = True
        self.hide_loading()

    def hide_loading(self) -> None:
        """Hide loading indicator window."""
        if self.loading_window:
            try:
                self.loading_window.destroy()
            except (AttributeError, TclError):
                pass  # Window might already be destroyed
            finally:
                self.loading_window = None
                self.progress_bar = None
                self.status_label = None

    def run_with_loading(
        self,
        func: Callable,
        message: str = "Processing...",
        title: str = "Please Wait",
        show_progress: bool = False,
        cancelable: bool = False,
        callback: Optional[Callable] = None,
    ) -> threading.Thread:
        """Run a function with loading indicator.

        Args:
            func: Function to run in background thread
            message: Status message to display
            title: Window title
            show_progress: Whether to show a progress bar
            cancelable: Whether to allow cancellation
            callback: Optional callback function to run after completion

        Returns:
            Thread object running the function
        """

        def run_func():
            try:
                result = func()
                if callback:
                    callback(result, None)
            except Exception as e:
                if callback:
                    callback(None, e)
                else:
                    raise
            finally:
                # Hide loading on main thread
                self.parent.after(0, self.hide_loading)

        # Show loading indicator
        self.show_loading(message, title, show_progress, cancelable)

        # Run function in background thread
        thread = threading.Thread(target=run_func, daemon=True)
        thread.start()

        return thread


# Global loading indicator instances
_loading_indicators = {}


def get_loading_indicator(parent: tk.Widget) -> LoadingIndicator:
    """Get or create loading indicator for a widget.

    Args:
        parent: Parent widget

    Returns:
        LoadingIndicator instance
    """
    widget_id = id(parent)
    if widget_id not in _loading_indicators:
        _loading_indicators[widget_id] = LoadingIndicator(parent)
    return _loading_indicators[widget_id]


def show_loading(
    parent: tk.Widget,
    message: str = "Processing...",
    title: str = "Please Wait",
    show_progress: bool = False,
    cancelable: bool = False,
) -> None:
    """Convenience function to show loading indicator.

    Args:
        parent: Parent widget
        message: Status message to display
        title: Window title
        show_progress: Whether to show a progress bar
        cancelable: Whether to allow cancellation
    """
    indicator = get_loading_indicator(parent)
    indicator.show_loading(message, title, show_progress, cancelable)


def hide_loading(parent: tk.Widget) -> None:
    """Convenience function to hide loading indicator.

    Args:
        parent: Parent widget
    """
    indicator = get_loading_indicator(parent)
    indicator.hide_loading()


def run_with_loading(
    parent: tk.Widget,
    func: Callable,
    message: str = "Processing...",
    title: str = "Please Wait",
    show_progress: bool = False,
    cancelable: bool = False,
    callback: Optional[Callable] = None,
) -> threading.Thread:
    """Convenience function to run function with loading indicator.

    Args:
        parent: Parent widget
        func: Function to run in background thread
        message: Status message to display
        title: Window title
        show_progress: Whether to show a progress bar
        cancelable: Whether to allow cancellation
        callback: Optional callback function to run after completion

    Returns:
        Thread object running the function
    """
    indicator = get_loading_indicator(parent)
    return indicator.run_with_loading(
        func, message, title, show_progress, cancelable, callback
    )
