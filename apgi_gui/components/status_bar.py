"""Status bar component for the APGI Framework GUI."""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from typing import Optional


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
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the status bar UI components."""
        # Configure frame
        self.configure(height=40)
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)
        
        # Status message label
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Progress bar (hidden by default)
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()  # Hide initially
        
        # Current file label
        self.file_label = ctk.CTkLabel(
            self,
            text="No file loaded",
            anchor="e",
            font=ctk.CTkFont(size=12)
        )
        self.file_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")
        
        # Time label
        self.time_label = ctk.CTkLabel(
            self,
            text="",
            anchor="e",
            font=ctk.CTkFont(size=12)
        )
        self.time_label.grid(row=0, column=3, padx=10, pady=5, sticky="e")
        
        # Start time updates
        self.update_time()
    
    def set_status(self, message: str, level: str = "info") -> None:
        """Set the status message with optional level indicator.
        
        Args:
            message: Status message to display
            level: Message level (info, warning, error, success)
        """
        # Add level indicator if specified
        if level == "warning":
            prefix = "⚠️ "
            color = "orange"
        elif level == "error":
            prefix = "❌ "
            color = "red"
        elif level == "success":
            prefix = "✅ "
            color = "green"
        else:
            prefix = ""
            color = "gray"
        
        full_message = f"{prefix}{message}"
        self.status_label.configure(text=full_message)
        
        # Set text color if specified
        if color and color != "gray":
            try:
                self.status_label.configure(text_color=color)
            except:
                pass  # Fallback if color not supported
    
    def set_file(self, file_path: Optional[str]) -> None:
        """Update the current file display.
        
        Args:
            file_path: Path to current file, or None if no file
        """
        if file_path:
            # Show just the filename if path is long
            if len(file_path) > 50:
                parts = file_path.split('/')
                if len(parts) > 3:
                    display_name = f".../{parts[-2]}/{parts[-1]}"
                else:
                    display_name = file_path
            else:
                display_name = file_path
            
            self.file_label.configure(text=f"📄 {display_name}")
        else:
            self.file_label.configure(text="No file loaded")
    
    def show_progress(self, value: float = 0.0) -> None:
        """Show and update the progress bar.
        
        Args:
            value: Progress value between 0.0 and 1.0
        """
        self.progress_bar.grid()
        self.progress_bar.set(value)
    
    def hide_progress(self) -> None:
        """Hide the progress bar."""
        self.progress_bar.grid_remove()
    
    def update_time(self) -> None:
        """Update the time display."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=f"🕐 {current_time}")
        
        # Schedule next update
        self.after(1000, self.update_time)
    
    def clear_status(self) -> None:
        """Clear the status message."""
        self.status_label.configure(text="Ready")
        try:
            self.status_label.configure(text_color="gray")
        except:
            pass
