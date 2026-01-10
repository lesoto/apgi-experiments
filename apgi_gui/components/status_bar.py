"""Status bar component for the APGI Framework GUI."""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from typing import Optional
import logging


class StatusBar(ctk.CTkFrame):
    """Status bar component displaying application status and information."""

    def __init__(self, parent, app):
        """Initialize the status bar.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent)
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.setup_ui()

    def setup_ui(self):
        """Set up the status bar UI components."""
        self.logger.debug("Setting up status bar UI")

        # Configure frame
        self.configure(height=40)
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)

        # Status message label
        self.status_label = ctk.CTkLabel(
            self, text="Ready", anchor="w", font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Progress bar (hidden by default)
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()  # Hide initially

        # Current file label
        self.file_label = ctk.CTkLabel(
            self, text="No file loaded", anchor="e", font=ctk.CTkFont(size=12)
        )
        self.file_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        # Time label
        self.time_label = ctk.CTkLabel(
            self, text="", anchor="e", font=ctk.CTkFont(size=12)
        )
        self.time_label.grid(row=0, column=3, padx=10, pady=5, sticky="e")

        # Start time updates
        self.update_time()

        self.logger.debug("Status bar UI setup completed")

    def set_status(
        self, message: str, level: str = "info", color: Optional[str] = None
    ) -> None:
        """Set the status message with optional level indicator.

        Args:
            message: Status message to display
            level: Message level (info, warning, error, success)
            color: Optional explicit color override
        """
        self.logger.debug(f"Setting status: {message} (level: {level})")

        # Add level indicator if specified
        if level == "warning":
            prefix = "⚠️ "
            text_color = color or "#FFA500"  # Orange
        elif level == "error":
            prefix = "❌ "
            text_color = color or "#FF4444"  # Red
        elif level == "success":
            prefix = "✅ "
            text_color = color or "#44FF44"  # Green
        else:
            prefix = ""
            text_color = color or None

        full_message = f"{prefix}{message}"

        # Update status label with proper color handling
        try:
            if text_color:
                # Try to set text color for customtkinter
                self.status_label.configure(text=full_message, text_color=text_color)
            else:
                # Just set text without color
                self.status_label.configure(text=full_message)

            self.logger.debug(f"Status updated successfully: {full_message}")

        except Exception as e:
            # Fallback: just set text without color
            try:
                self.status_label.configure(text=full_message)
                self.logger.warning(f"Failed to set status color: {e}")
            except Exception as e2:
                # Ultimate fallback: print to console
                print(f"Status: {full_message}")
                self.logger.error(f"Failed to set status text: {e2}")

    def reset_status_color(self) -> None:
        """Reset status label color to default."""
        try:
            # Reset to default theme color
            self.status_label.configure(text_color=None)
            self.logger.debug("Status color reset to default")
        except Exception as e:
            # If reset fails, set to a neutral color
            try:
                self.status_label.configure(text_color="gray")
                self.logger.warning(f"Failed to reset status color, using gray: {e}")
            except Exception as e2:
                self.logger.error(f"Failed to set fallback status color: {e2}")
                pass

    def set_file(self, file_path: Optional[str]) -> None:
        """Update the current file display.

        Args:
            file_path: Path to current file, or None if no file
        """
        if file_path:
            self.logger.debug(f"Setting file display: {file_path}")

            # Show just the filename if path is long
            if len(file_path) > 50:
                parts = file_path.split("/")
                if len(parts) > 3:
                    display_name = f".../{parts[-2]}/{parts[-1]}"
                else:
                    display_name = file_path
            else:
                display_name = file_path

            self.file_label.configure(text=f"📄 {display_name}")
        else:
            self.logger.debug("Clearing file display")
            self.file_label.configure(text="No file loaded")

    def show_progress(self, value: float = 0.0) -> None:
        """Show and update the progress bar.

        Args:
            value: Progress value between 0.0 and 1.0
        """
        self.logger.debug(f"Showing progress: {value}")
        self.progress_bar.grid()
        self.progress_bar.set(value)

    def hide_progress(self) -> None:
        """Hide the progress bar."""
        self.logger.debug("Hiding progress bar")
        self.progress_bar.grid_remove()

    def update_time(self) -> None:
        """Update the time display."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=f"🕐 {current_time}")

        # Schedule next update
        self.after(1000, self.update_time)

    def clear_status(self) -> None:
        """Clear the status message."""
        self.logger.debug("Clearing status message")
        self.status_label.configure(text="Ready")
        self.reset_status_color()
