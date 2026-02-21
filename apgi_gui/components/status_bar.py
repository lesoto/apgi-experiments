"""Status bar component for the APGI Framework GUI."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import customtkinter as ctk  # type: ignore[import]

# Import font manager for cross-platform compatibility
try:
    from apgi_framework.config.constants import GUIConstants, TimingConstants
    from apgi_framework.utils.font_manager import get_ui_font
except ImportError:
    # Fallback for direct execution
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from apgi_framework.config.constants import GUIConstants, TimingConstants
    from apgi_framework.utils.font_manager import get_ui_font


# Cross-platform status indicators - using text-based icons for consistency
STATUS_INDICATORS = {
    "success": "[OK] ",
    "warning": "[WARN] ",
    "error": "[ERR] ",
    "info": "[INFO] ",
}


class StatusBar(ctk.CTkFrame):
    """Status bar component displaying application status and information."""

    def __init__(self, parent, app):
        """Initialize status bar.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent)
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.setup_ui()

    def destroy(self):
        """Override destroy to prevent CustomTkinter font AttributeError."""
        try:
            super().destroy()
        except AttributeError as e:
            if "_font" in str(e):
                # Ignore CustomTkinter font attribute error - this is expected
                self.logger.debug(f"Ignoring expected CustomTkinter font error: {e}")
            else:
                # Log other attribute errors
                self.logger.warning(f"Unexpected AttributeError during destroy: {e}")
                raise

    def setup_ui(self):
        """Set up the status bar UI components."""
        self.logger.debug("Setting up status bar UI")

        # Configure frame
        self.configure(height=GUIConstants.DEFAULT_PADDING * 4)  # 40px
        # Configure grid columns for proper layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)

        # Status message label
        try:
            ui_font = get_ui_font(GUIConstants.DEFAULT_FONT_SIZE)
            self.status_label = ctk.CTkLabel(
                self, text="Ready", anchor="w", font=ui_font
            )
        except Exception:
            # Fallback to default font
            self.status_label = ctk.CTkLabel(
                self,
                text="Ready",
                anchor="w",
                font=ctk.CTkFont(size=GUIConstants.DEFAULT_FONT_SIZE),
            )
        # Store font reference to prevent AttributeError on destroy
        self.status_label._font = None
        self.status_label.grid(
            row=0,
            column=0,
            padx=GUIConstants.DEFAULT_PADDING,
            pady=GUIConstants.SMALL_PADDING,
            sticky="w",
        )

        # Progress bar (hidden by default)
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        # Don't grid initially to prevent visual flicker - will be gridded when shown

        # Current file label
        try:
            ui_font = get_ui_font(GUIConstants.DEFAULT_FONT_SIZE)
            self.file_label = ctk.CTkLabel(
                self, text="No file loaded", anchor="e", font=ui_font
            )
        except Exception:
            # Fallback to default font
            self.file_label = ctk.CTkLabel(
                self,
                text="No file loaded",
                anchor="e",
                font=ctk.CTkFont(size=GUIConstants.DEFAULT_FONT_SIZE),
            )
        # Store font reference to prevent AttributeError on destroy
        self.file_label._font = None
        self.file_label.grid(
            row=0,
            column=2,
            padx=GUIConstants.DEFAULT_PADDING,
            pady=GUIConstants.SMALL_PADDING,
            sticky="e",
        )

        # Time label
        try:
            ui_font = get_ui_font(GUIConstants.DEFAULT_FONT_SIZE)
            self.time_label = ctk.CTkLabel(self, text="", anchor="e", font=ui_font)
        except Exception:
            # Fallback to default font
            self.time_label = ctk.CTkLabel(
                self,
                text="",
                anchor="e",
                font=ctk.CTkFont(size=GUIConstants.DEFAULT_FONT_SIZE),
            )
        # Store font reference to prevent AttributeError on destroy
        self.time_label._font = None
        self.time_label.grid(
            row=0,
            column=3,
            padx=GUIConstants.DEFAULT_PADDING,
            pady=GUIConstants.SMALL_PADDING,
            sticky="e",
        )

        # Zoom level label
        try:
            ui_font = get_ui_font(GUIConstants.DEFAULT_FONT_SIZE)
            self.zoom_label = ctk.CTkLabel(self, text="100%", anchor="e", font=ui_font)
        except Exception:
            # Fallback to default font
            self.zoom_label = ctk.CTkLabel(
                self,
                text="100%",
                anchor="e",
                font=ctk.CTkFont(size=GUIConstants.DEFAULT_FONT_SIZE),
            )
        # Store font reference to prevent AttributeError on destroy
        self.zoom_label._font = None
        self.zoom_label.grid(
            row=0,
            column=4,
            padx=GUIConstants.DEFAULT_PADDING,
            pady=GUIConstants.SMALL_PADDING,
            sticky="e",
        )

        # Start time updates
        self.update_time()

        self.logger.debug("Status bar UI setup completed")

    def set_status(
        self, message: str, level: str = "info", color: Optional[str] = None
    ) -> None:
        """Set the status message with optional level indicator.

        Args:
            message: Status message to display.
            level: Message level (info, warning, error, success).
            color: Optional explicit color override.
        """
        self.logger.debug(f"Setting status: {message} (level: {level})")

        # Add level indicator if specified
        text_color: Optional[str] = None
        if level == "warning":
            prefix = STATUS_INDICATORS["warning"]
            text_color = color or "#FFA500"  # Orange
        elif level == "error":
            prefix = STATUS_INDICATORS["error"]
            text_color = color or "#FF4444"  # Red
        elif level == "success":
            prefix = STATUS_INDICATORS["success"]
            text_color = color or "#44FF44"  # Green
        elif level == "info":
            prefix = STATUS_INDICATORS["info"]
            text_color = color or "#4169E1"  # Blue
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
            # If reset fails, set to a neutral color and inform user
            try:
                self.status_label.configure(text_color="gray")
                self.logger.warning(f"Failed to reset status color, using gray: {e}")
                self.show_temporary_message(
                    "Status display error - using fallback color", "warning"
                )
            except Exception as e2:
                self.logger.error(f"Failed to set fallback status color: {e2}")
                self.show_temporary_message(
                    "Status display error - color reset failed", "error"
                )

    def set_file(self, file_path: Optional[str]) -> None:
        """Update the current file display.

        Args:
            file_path: Path to current file, or None if no file.
        """
        if file_path:
            self.logger.debug(f"Setting file display: {file_path}")

            # Convert to Path object for consistent handling
            path_obj = Path(file_path)

            # Show just the filename if path is long
            if len(str(path_obj)) > 50:
                parts = path_obj.parts
                if len(parts) > 3:
                    display_name = str(Path("...") / parts[-2] / parts[-1])
                else:
                    display_name = str(path_obj)
            else:
                display_name = str(path_obj)

            self.file_label.configure(text=f"File: {display_name}")
        else:
            self.logger.debug("Clearing file display")
            self.file_label.configure(text="No file loaded")

    def show_progress(self, value: float = 0.0) -> None:
        """Show and update the progress bar.

        Args:
            value: Progress value between 0.0 and 1.0.
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
        self.time_label.configure(text=f"Time: {current_time}")

        # Schedule next update
        self.after(TimingConstants.STATUS_UPDATE_INTERVAL, self.update_time)

    def set_zoom_level(self, zoom_percent: int) -> None:
        """Update the zoom level display.

        Args:
            zoom_percent: Zoom level as percentage (e.g., 100, 150, 200).
        """
        self.logger.debug(f"Setting zoom level display: {zoom_percent}%")
        self.zoom_label.configure(text=f"{zoom_percent}%")

    def clear_status(self) -> None:
        """Clear the status message."""
        self.logger.debug("Clearing status message")
        self.status_label.configure(text="Ready")
        self.reset_status_color()

    def show_temporary_message(self, message: str, level: str = "info") -> None:
        """Show a temporary status message that clears after a delay.

        Args:
            message: Message to display
            level: Message level (info, warning, error, success)
        """
        self.set_status(message, level)
        # Schedule to clear the message after 5 seconds
        self.after(5000, lambda: self.clear_status())
