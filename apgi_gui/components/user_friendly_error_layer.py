"""
User-friendly error layer for APGI Framework GUI applications.

Provides comprehensive error handling with user-friendly messages,
technical details, error aggregation, and contextual help.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
import traceback
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization."""

    FILE_IO = "file_io"
    NETWORK = "network"
    VALIDATION = "validation"
    EXPERIMENT = "experiment"
    GUI = "gui"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for an error."""

    action: str
    component: str
    user_input: Optional[str] = None
    file_path: Optional[str] = None
    experiment_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class FriendlyError:
    """User-friendly error representation."""

    id: str
    title: str
    user_message: str
    technical_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: Optional[ErrorContext] = None
    timestamp: datetime = field(default_factory=datetime.now)
    suggestions: List[str] = field(default_factory=list)
    help_links: List[str] = field(default_factory=list)
    can_retry: bool = False
    retry_callback: Optional[Callable] = None


class ErrorAggregator:
    """Aggregates similar errors to prevent overwhelming the user."""

    def __init__(self, aggregation_window: int = 60):
        self.aggregation_window = aggregation_window  # seconds
        self.error_groups: Dict[str, List[FriendlyError]] = {}
        self.lock = threading.Lock()

    def _get_error_key(self, error: FriendlyError) -> str:
        """Generate a key for grouping similar errors."""
        # Group by title and category
        return f"{error.category.value}:{error.title}"

    def should_aggregate(self, error: FriendlyError) -> bool:
        """Check if error should be aggregated with existing errors."""
        key = self._get_error_key(error)

        with self.lock:
            if key not in self.error_groups:
                return False

            # Check if there are similar errors within the aggregation window
            cutoff_time = datetime.now() - timedelta(seconds=self.aggregation_window)
            recent_errors = [
                e for e in self.error_groups[key] if e.timestamp > cutoff_time
            ]

            return len(recent_errors) > 0

    def add_error(self, error: FriendlyError) -> List[FriendlyError]:
        """Add error and return list of errors to show (aggregated)."""
        key = self._get_error_key(error)

        with self.lock:
            if key not in self.error_groups:
                self.error_groups[key] = []

            self.error_groups[key].append(error)

            # Clean up old errors
            cutoff_time = datetime.now() - timedelta(seconds=self.aggregation_window)
            self.error_groups[key] = [
                e for e in self.error_groups[key] if e.timestamp > cutoff_time
            ]

            # Return aggregated error if there are multiple
            if len(self.error_groups[key]) > 1:
                return [self._create_aggregated_error(self.error_groups[key])]
            else:
                return [error]

    def _create_aggregated_error(self, errors: List[FriendlyError]) -> FriendlyError:
        """Create an aggregated error from multiple similar errors."""
        first_error = errors[0]
        count = len(errors)

        return FriendlyError(
            id=f"aggregated_{first_error.id}",
            title=first_error.title,
            user_message=f"This error has occurred {count} times in the last {self.aggregation_window} seconds. {first_error.user_message}",
            technical_message=f"Aggregated {count} occurrences:\n"
            + "\n".join([e.technical_message for e in errors[:3]]),
            severity=first_error.severity,
            category=first_error.category,
            context=first_error.context,
            timestamp=errors[-1].timestamp,
            suggestions=first_error.suggestions,
            help_links=first_error.help_links,
            can_retry=first_error.can_retry,
            retry_callback=first_error.retry_callback,
        )


class UserFriendlyErrorLayer:
    """
    Comprehensive user-friendly error handling system.

    Provides user-friendly error messages, technical details, error aggregation,
    contextual help, and retry mechanisms.
    """

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.error_queue = queue.Queue()
        self.aggregator = ErrorAggregator()
        self.error_history: List[FriendlyError] = []
        self.show_technical_details = False
        self.error_callbacks: List[Callable] = []

        # Error message templates
        self.message_templates = self._load_message_templates()

        # Start error processing thread
        self.processing_thread = threading.Thread(
            target=self._process_errors, daemon=True
        )
        self.processing_thread.start()

        logger.info("User-friendly error layer initialized")

    def _load_message_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load error message templates."""
        return {
            ErrorCategory.FILE_IO.value: {
                "file_not_found": {
                    "title": "File Not Found",
                    "user_message": "The file you're looking for couldn't be found. Please check if the file exists and you have permission to access it.",
                    "suggestions": [
                        "Check if the file path is correct",
                        "Verify the file exists",
                        "Ensure you have read permissions",
                        "Try using the file browser to locate the file",
                    ],
                    "help_links": ["File Management Guide"],
                },
                "permission_denied": {
                    "title": "Access Denied",
                    "user_message": "You don't have permission to access this file or location.",
                    "suggestions": [
                        "Check file permissions",
                        "Run the application as administrator",
                        "Choose a different location",
                        "Contact your system administrator",
                    ],
                    "help_links": ["Permissions Guide"],
                },
                "invalid_format": {
                    "title": "Invalid File Format",
                    "user_message": "The file format is not supported or the file is corrupted.",
                    "suggestions": [
                        "Check if the file is in the correct format",
                        "Try opening the file in a different application",
                        "Create a new file with the correct format",
                        "Check if the file is corrupted",
                    ],
                    "help_links": ["File Formats Guide"],
                },
            },
            ErrorCategory.EXPERIMENT.value: {
                "parameter_error": {
                    "title": "Parameter Error",
                    "user_message": "One or more experiment parameters are invalid or missing.",
                    "suggestions": [
                        "Check all required parameters are filled",
                        "Verify parameter values are within valid ranges",
                        "Review parameter documentation",
                        "Use default parameters if unsure",
                    ],
                    "help_links": ["Parameter Guide", "Experiment Documentation"],
                },
                "execution_failed": {
                    "title": "Experiment Failed",
                    "user_message": "The experiment couldn't be completed due to an error.",
                    "suggestions": [
                        "Check experiment configuration",
                        "Verify input data is valid",
                        "Review error details for more information",
                        "Try running with simplified parameters",
                    ],
                    "help_links": ["Troubleshooting Guide", "Experiment FAQ"],
                },
            },
            ErrorCategory.NETWORK.value: {
                "connection_failed": {
                    "title": "Connection Failed",
                    "user_message": "Unable to connect to the server or remote resource.",
                    "suggestions": [
                        "Check your internet connection",
                        "Verify server is accessible",
                        "Check firewall settings",
                        "Try again later",
                    ],
                    "help_links": ["Network Troubleshooting"],
                }
            },
            ErrorCategory.VALIDATION.value: {
                "invalid_input": {
                    "title": "Invalid Input",
                    "user_message": "The input you provided is not valid.",
                    "suggestions": [
                        "Check input format requirements",
                        "Remove special characters if not allowed",
                        "Ensure all required fields are filled",
                        "Review input examples",
                    ],
                    "help_links": ["Input Validation Guide"],
                }
            },
        }

    def show_error(
        self,
        title: str,
        message: str,
        technical_message: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[ErrorContext] = None,
        suggestions: Optional[List[str]] = None,
        help_links: Optional[List[str]] = None,
        can_retry: bool = False,
        retry_callback: Optional[Callable] = None,
    ):
        """
        Show a user-friendly error message.

        Args:
            title: Error title
            message: User-friendly error message
            technical_message: Technical details for debugging
            severity: Error severity level
            category: Error category
            context: Error context information
            suggestions: List of suggestions for the user
            help_links: List of help links
            can_retry: Whether the operation can be retried
            retry_callback: Callback for retry operation
        """
        # Generate error ID
        error_id = f"error_{int(time.time() * 1000)}"

        # Get template-based suggestions if none provided
        if suggestions is None:
            template = self._get_template(category, title.lower().replace(" ", "_"))
            if template:
                suggestions = template.get("suggestions", [])
                help_links = help_links or template.get("help_links", [])

        # Create friendly error
        error = FriendlyError(
            id=error_id,
            title=title,
            user_message=message,
            technical_message=technical_message or traceback.format_exc(),
            severity=severity,
            category=category,
            context=context,
            suggestions=suggestions or [],
            help_links=help_links or [],
            can_retry=can_retry,
            retry_callback=retry_callback,
        )

        # Add to queue for processing
        self.error_queue.put(error)

    def _get_template(
        self, category: ErrorCategory, key: str
    ) -> Optional[Dict[str, Any]]:
        """Get message template for category and key."""
        category_templates = self.message_templates.get(category.value, {})
        return category_templates.get(key)

    def _process_errors(self):
        """Process errors from the queue."""
        while True:
            try:
                # Get error from queue
                error = self.error_queue.get(timeout=1)

                # Check if should be aggregated
                if self.aggregator.should_aggregate(error):
                    errors_to_show = self.aggregator.add_error(error)
                else:
                    errors_to_show = self.aggregator.add_error(error)

                # Show errors in main thread
                for error_to_show in errors_to_show:
                    self.parent.after(0, self._show_error_dialog, error_to_show)

                # Add to history
                self.error_history.append(error)

                # Notify callbacks
                for callback in self.error_callbacks:
                    try:
                        callback(error)
                    except Exception as e:
                        logger.error(f"Error callback failed: {e}")

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing failed: {e}")

    def _show_error_dialog(self, error: FriendlyError):
        """Show the error dialog to the user."""
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title(error.title)
        dialog.geometry("600x500")
        dialog.resizable(True, True)

        # Make dialog modal
        dialog.transient(self.parent)
        dialog.grab_set()

        # Configure dialog based on severity
        self._configure_dialog_style(dialog, error.severity)

        # Create main content
        self._create_error_dialog_content(dialog, error)

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Focus on dialog
        dialog.focus_set()

    def _configure_dialog_style(self, dialog: tk.Toplevel, severity: ErrorSeverity):
        """Configure dialog style based on severity."""
        colors = {
            ErrorSeverity.INFO: {"bg": "#e3f2fd", "fg": "#1976d2"},
            ErrorSeverity.WARNING: {"bg": "#fff3e0", "fg": "#f57c00"},
            ErrorSeverity.ERROR: {"bg": "#ffebee", "fg": "#d32f2f"},
            ErrorSeverity.CRITICAL: {"bg": "#ffcdd2", "fg": "#b71c1c"},
        }

        color_scheme = colors.get(severity, colors[ErrorSeverity.ERROR])

        # Configure title frame
        title_frame = ttk.Frame(dialog)
        title_frame.pack(fill=tk.X, padx=10, pady=10)

        # Add icon and title
        icon_label = tk.Label(
            title_frame,
            text=self._get_severity_icon(severity),
            font=("Arial", 16),
            fg=color_scheme["fg"],
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        title_label = tk.Label(
            title_frame,
            text=error.title,
            font=("Arial", 12, "bold"),
            fg=color_scheme["fg"],
        )
        title_label.pack(side=tk.LEFT)

    def _get_severity_icon(self, severity: ErrorSeverity) -> str:
        """Get icon for severity level."""
        icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨",
        }
        return icons.get(severity, "❌")

    def _create_error_dialog_content(self, dialog: tk.Toplevel, error: FriendlyError):
        """Create the main content of the error dialog."""
        # Create notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Main message tab
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Message")

        # Create main message content
        self._create_main_message_tab(main_frame, error)

        # Technical details tab
        if error.technical_message:
            tech_frame = ttk.Frame(notebook)
            notebook.add(tech_frame, text="Technical Details")
            self._create_technical_details_tab(tech_frame, error)

        # Suggestions tab
        if error.suggestions:
            suggestions_frame = ttk.Frame(notebook)
            notebook.add(suggestions_frame, text="Suggestions")
            self._create_suggestions_tab(suggestions_frame, error)

        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Add buttons
        self._create_dialog_buttons(button_frame, dialog, error)

    def _create_main_message_tab(self, parent: ttk.Frame, error: FriendlyError):
        """Create the main message tab content."""
        # Message text
        message_frame = ttk.Frame(parent)
        message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        message_text = tk.Text(message_frame, wrap=tk.WORD, height=8)
        message_text.pack(fill=tk.BOTH, expand=True)
        message_text.insert(tk.END, error.user_message)
        message_text.config(state=tk.DISABLED)

        # Context information
        if error.context:
            context_frame = ttk.LabelFrame(parent, text="Context", padding=10)
            context_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

            context_info = []
            context_info.append(f"Action: {error.context.action}")
            context_info.append(f"Component: {error.context.component}")

            if error.context.user_input:
                context_info.append(f"Input: {error.context.user_input}")
            if error.context.file_path:
                context_info.append(f"File: {error.context.file_path}")
            if error.context.experiment_id:
                context_info.append(f"Experiment: {error.context.experiment_id}")

            context_label = tk.Label(
                context_frame, text="\n".join(context_info), justify=tk.LEFT
            )
            context_label.pack(anchor=tk.W)

    def _create_technical_details_tab(self, parent: ttk.Frame, error: FriendlyError):
        """Create the technical details tab content."""
        # Technical details with scrollbar
        tech_frame = ttk.Frame(parent)
        tech_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(tech_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tech_text = tk.Text(tech_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        tech_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=tech_text.yview)

        # Insert technical details
        tech_text.insert(tk.END, f"Error ID: {error.id}\n")
        tech_text.insert(tk.END, f"Timestamp: {error.timestamp.isoformat()}\n")
        tech_text.insert(tk.END, f"Severity: {error.severity.value}\n")
        tech_text.insert(tk.END, f"Category: {error.category.value}\n")
        tech_text.insert(tk.END, "\n" + "=" * 50 + "\n")
        tech_text.insert(tk.END, "Technical Message:\n")
        tech_text.insert(tk.END, error.technical_message)

        tech_text.config(state=tk.DISABLED)

    def _create_suggestions_tab(self, parent: ttk.Frame, error: FriendlyError):
        """Create the suggestions tab content."""
        suggestions_frame = ttk.Frame(parent)
        suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Suggestions list
        for i, suggestion in enumerate(error.suggestions, 1):
            suggestion_frame = ttk.Frame(suggestions_frame)
            suggestion_frame.pack(fill=tk.X, pady=2)

            # Number label
            num_label = tk.Label(
                suggestion_frame, text=f"{i}.", font=("Arial", 10, "bold")
            )
            num_label.pack(side=tk.LEFT, padx=(0, 5))

            # Suggestion text
            suggestion_text = tk.Label(
                suggestion_frame, text=suggestion, wraplength=500, justify=tk.LEFT
            )
            suggestion_text.pack(side=tk.LEFT)

        # Help links
        if error.help_links:
            help_frame = ttk.LabelFrame(
                suggestions_frame, text="Help Resources", padding=10
            )
            help_frame.pack(fill=tk.X, pady=(20, 0))

            for link in error.help_links:
                link_label = tk.Label(
                    help_frame, text=f"📚 {link}", fg="blue", cursor="hand2"
                )
                link_label.pack(anchor=tk.W, pady=2)
                link_label.bind("<Button-1>", lambda e, l=link: self._open_help_link(l))

    def _create_dialog_buttons(
        self, parent: ttk.Frame, dialog: tk.Toplevel, error: FriendlyError
    ):
        """Create dialog buttons."""
        # Retry button
        if error.can_retry and error.retry_callback:
            retry_btn = ttk.Button(
                parent,
                text="Retry",
                command=lambda: self._retry_operation(dialog, error),
            )
            retry_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Copy details button
        copy_btn = ttk.Button(
            parent, text="Copy Details", command=lambda: self._copy_error_details(error)
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Close button
        close_btn = ttk.Button(parent, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT)

    def _retry_operation(self, dialog: tk.Toplevel, error: FriendlyError):
        """Retry the failed operation."""
        dialog.destroy()

        if error.retry_callback:
            try:
                error.retry_callback()
            except Exception as e:
                logger.error(f"Retry callback failed: {e}")
                self.show_error(
                    "Retry Failed",
                    "The retry operation failed. Please try again or contact support.",
                    str(e),
                    ErrorSeverity.ERROR,
                    ErrorCategory.UNKNOWN,
                )

    def _copy_error_details(self, error: FriendlyError):
        """Copy error details to clipboard."""
        try:
            details = f"""Error Details:
Title: {error.title}
Message: {error.user_message}
Severity: {error.severity.value}
Category: {error.category.value}
Timestamp: {error.timestamp.isoformat}

Technical Details:
{error.technical_message}

Suggestions:
{chr(10).join(f"- {s}" for s in error.suggestions)}
"""

            # Copy to clipboard
            self.parent.clipboard_clear()
            self.parent.clipboard_append(details)

            messagebox.showinfo("Success", "Error details copied to clipboard")

        except Exception as e:
            logger.error(f"Failed to copy error details: {e}")
            messagebox.showerror("Error", "Failed to copy error details")

    def _open_help_link(self, link: str):
        """Open help link (placeholder)."""
        messagebox.showinfo(
            "Help", f"Help link: {link}\n\nThis would open the help documentation."
        )

    def add_error_callback(self, callback: Callable):
        """Add a callback for error events."""
        self.error_callbacks.append(callback)

    def remove_error_callback(self, callback: Callable):
        """Remove an error callback."""
        if callback in self.error_callbacks:
            self.error_callbacks.remove(callback)

    def get_error_history(
        self,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None,
    ) -> List[FriendlyError]:
        """Get error history with optional filtering."""
        filtered_history = self.error_history

        if category:
            filtered_history = [e for e in filtered_history if e.category == category]

        if severity:
            filtered_history = [e for e in filtered_history if e.severity == severity]

        return filtered_history

    def clear_error_history(self):
        """Clear error history."""
        self.error_history.clear()

    def export_error_history(self, file_path: Path) -> bool:
        """Export error history to file."""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_errors": len(self.error_history),
                "errors": [],
            }

            for error in self.error_history:
                error_dict = {
                    "id": error.id,
                    "title": error.title,
                    "user_message": error.user_message,
                    "technical_message": error.technical_message,
                    "severity": error.severity.value,
                    "category": error.category.value,
                    "timestamp": error.timestamp.isoformat(),
                    "suggestions": error.suggestions,
                    "help_links": error.help_links,
                    "can_retry": error.can_retry,
                }

                if error.context:
                    error_dict["context"] = {
                        "action": error.context.action,
                        "component": error.context.component,
                        "user_input": error.context.user_input,
                        "file_path": error.context.file_path,
                        "experiment_id": error.context.experiment_id,
                    }

                export_data["errors"].append(error_dict)

            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Failed to export error history: {e}")
            return False


def create_error_layer(parent: tk.Widget) -> UserFriendlyErrorLayer:
    """
    Convenience function to create a user-friendly error layer.

    Args:
        parent: Parent widget

    Returns:
        UserFriendlyErrorLayer instance
    """
    return UserFriendlyErrorLayer(parent)
