"""
Error Feedback UI Component for APGI Framework

Provides user-friendly error reporting, solution suggestions, and
feedback collection for improving error handling.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Optional, Any, Callable
import json
from pathlib import Path
import webbrowser

try:
    from apgi_framework.validation.enhanced_error_handling import (
        APGIError,
        ErrorSolution,
        get_error_handler,
    )

    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ERROR_HANDLING_AVAILABLE = False
    APGIError = None
    ErrorSolution = None


class ErrorReportDialog:
    """Dialog for displaying detailed error information and solutions."""

    def __init__(
        self, parent, apgi_error: APGIError = None, simple_error: Exception = None
    ):
        self.parent = parent
        self.apgi_error = apgi_error
        self.simple_error = simple_error

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Error Report")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)

        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self._center_dialog()

        # Create content
        self._create_content()

        # Handle close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)

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

        # Error icon and title
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Error icon (using text for simplicity)
        icon_label = ttk.Label(header_frame, text="⚠️", font=("Arial", 24))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # Title and basic info
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        if self.apgi_error:
            title_text = (
                f"Error: {self.apgi_error.category.value.replace('_', ' ').title()}"
            )
            severity_text = f"Severity: {self.apgi_error.severity.value.title()}"
            error_id_text = f"Error ID: {self.apgi_error.error_id}"
        else:
            title_text = f"Error: {type(self.simple_error).__name__}"
            severity_text = "Severity: Unknown"
            error_id_text = "Error ID: N/A"

        ttk.Label(info_frame, text=title_text, font=("Arial", 14, "bold")).pack(
            anchor=tk.W
        )
        ttk.Label(info_frame, text=severity_text).pack(anchor=tk.W)
        ttk.Label(info_frame, text=error_id_text, font=("Courier", 9)).pack(anchor=tk.W)

        # Create notebook for different sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Error details tab
        self._create_details_tab(notebook)

        # Solutions tab
        if self.apgi_error and self.apgi_error.solutions:
            self._create_solutions_tab(notebook)

        # Technical details tab
        self._create_technical_tab(notebook)

        # Feedback tab
        self._create_feedback_tab(notebook)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame, text="Copy Error Details", command=self._copy_error_details
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(button_frame, text="Save Report", command=self._save_report).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        ttk.Button(button_frame, text="Close", command=self._on_close).pack(
            side=tk.RIGHT
        )

    def _create_details_tab(self, notebook):
        """Create the error details tab."""
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="Error Details")

        # User-friendly message
        message_frame = ttk.LabelFrame(details_frame, text="What Happened", padding=10)
        message_frame.pack(fill=tk.X, pady=(0, 10))

        if self.apgi_error:
            message_text = self.apgi_error.user_message
        else:
            message_text = f"An error occurred: {str(self.simple_error)}"

        message_label = ttk.Label(message_frame, text=message_text, wraplength=600)
        message_label.pack(anchor=tk.W)

        # Context information
        if self.apgi_error and self.apgi_error.context.user_action:
            context_frame = ttk.LabelFrame(
                details_frame, text="When It Happened", padding=10
            )
            context_frame.pack(fill=tk.X, pady=(0, 10))

            context_text = f"User was: {self.apgi_error.context.user_action}"
            ttk.Label(context_frame, text=context_text, wraplength=600).pack(
                anchor=tk.W
            )

        # Quick actions
        actions_frame = ttk.LabelFrame(details_frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X)

        ttk.Button(actions_frame, text="Try Again", command=self._try_again).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        ttk.Button(
            actions_frame, text="Reset to Defaults", command=self._reset_defaults
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(actions_frame, text="Get Help", command=self._get_help).pack(
            side=tk.LEFT
        )

    def _create_solutions_tab(self, notebook):
        """Create the solutions tab."""
        solutions_frame = ttk.Frame(notebook)
        notebook.add(solutions_frame, text="Solutions")

        # Solutions list
        canvas = tk.Canvas(solutions_frame)
        scrollbar = ttk.Scrollbar(
            solutions_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add solutions
        for i, solution in enumerate(self.apgi_error.solutions):
            self._create_solution_widget(scrollable_frame, solution, i + 1)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_solution_widget(self, parent, solution: ErrorSolution, number: int):
        """Create a widget for displaying a solution."""
        solution_frame = ttk.LabelFrame(parent, text=f"Solution {number}", padding=10)
        solution_frame.pack(fill=tk.X, pady=(0, 10), padx=10)

        # Description
        desc_label = ttk.Label(
            solution_frame, text=solution.description, font=("Arial", 11, "bold")
        )
        desc_label.pack(anchor=tk.W, pady=(0, 5))

        # Action type
        action_label = ttk.Label(
            solution_frame,
            text=f"Type: {solution.action_type.replace('_', ' ').title()}",
        )
        action_label.pack(anchor=tk.W, pady=(0, 5))

        # Steps
        if solution.steps:
            steps_label = ttk.Label(
                solution_frame, text="Steps:", font=("Arial", 10, "bold")
            )
            steps_label.pack(anchor=tk.W, pady=(5, 2))

            for i, step in enumerate(solution.steps, 1):
                step_label = ttk.Label(
                    solution_frame, text=f"{i}. {step}", wraplength=550
                )
                step_label.pack(anchor=tk.W, padx=(20, 0), pady=1)

        # Code example
        if solution.code_example:
            code_label = ttk.Label(
                solution_frame, text="Code Example:", font=("Arial", 10, "bold")
            )
            code_label.pack(anchor=tk.W, pady=(10, 2))

            code_text = tk.Text(solution_frame, height=6, width=70, font=("Courier", 9))
            code_text.pack(anchor=tk.W, padx=(20, 0), pady=2)
            code_text.insert(tk.END, solution.code_example.strip())
            code_text.config(state=tk.DISABLED)

        # Success probability
        if solution.success_probability > 0:
            prob_text = f"Success Rate: {solution.success_probability:.0%}"
            prob_label = ttk.Label(solution_frame, text=prob_text, foreground="green")
            prob_label.pack(anchor=tk.W, pady=(5, 0))

    def _create_technical_tab(self, notebook):
        """Create the technical details tab."""
        technical_frame = ttk.Frame(notebook)
        notebook.add(technical_frame, text="Technical Details")

        # Technical information
        tech_text = scrolledtext.ScrolledText(
            technical_frame, wrap=tk.WORD, height=20, width=80
        )
        tech_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add technical details
        if self.apgi_error:
            tech_info = self._format_technical_details()
        else:
            tech_info = f"Exception Type: {type(self.simple_error).__name__}\n"
            tech_info += f"Message: {str(self.simple_error)}\n\n"
            tech_info += "Stack Trace:\n"
            import traceback

            tech_info += traceback.format_exc()

        tech_text.insert(tk.END, tech_info)
        tech_text.config(state=tk.DISABLED)

    def _create_feedback_tab(self, notebook):
        """Create the feedback tab."""
        feedback_frame = ttk.Frame(notebook)
        notebook.add(feedback_frame, text="Feedback")

        # Feedback form
        ttk.Label(
            feedback_frame,
            text="Help us improve error handling:",
            font=("Arial", 12, "bold"),
        ).pack(pady=(10, 5))

        # Was this helpful?
        helpful_frame = ttk.Frame(feedback_frame)
        helpful_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(helpful_frame, text="Was this error report helpful?").pack(
            side=tk.LEFT
        )

        self.helpful_var = tk.StringVar(value="")
        ttk.Radiobutton(
            helpful_frame, text="Yes", variable=self.helpful_var, value="yes"
        ).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(
            helpful_frame, text="No", variable=self.helpful_var, value="no"
        ).pack(side=tk.LEFT)

        # Additional comments
        ttk.Label(feedback_frame, text="Additional comments (optional):").pack(
            anchor=tk.W, padx=10, pady=(10, 5)
        )

        self.comments_text = tk.Text(feedback_frame, height=6, width=70)
        self.comments_text.pack(padx=10, pady=5)

        # Submit feedback button
        ttk.Button(
            feedback_frame, text="Submit Feedback", command=self._submit_feedback
        ).pack(pady=10)

    def _format_technical_details(self) -> str:
        """Format technical details for display."""
        details = []

        details.append(f"Error ID: {self.apgi_error.error_id}")
        details.append(f"Category: {self.apgi_error.category.value}")
        details.append(f"Severity: {self.apgi_error.severity.value}")
        details.append(f"Timestamp: {self.apgi_error.context.timestamp}")
        details.append("")

        details.append(f"Function: {self.apgi_error.context.function_name}")
        details.append(f"Module: {self.apgi_error.context.module_name}")
        details.append(f"Line: {self.apgi_error.context.line_number}")
        details.append("")

        details.append("Original Exception:")
        details.append(f"  Type: {type(self.apgi_error.original_exception).__name__}")
        details.append(f"  Message: {str(self.apgi_error.original_exception)}")
        details.append("")

        if self.apgi_error.context.local_variables:
            details.append("Local Variables:")
            for key, value in self.apgi_error.context.local_variables.items():
                details.append(f"  {key}: {value}")
            details.append("")

        if self.apgi_error.context.stack_trace:
            details.append("Stack Trace:")
            for line in self.apgi_error.context.stack_trace:
                details.append(f"  {line.strip()}")

        return "\n".join(details)

    def _copy_error_details(self):
        """Copy error details to clipboard."""
        if self.apgi_error:
            details = self._format_technical_details()
        else:
            details = (
                f"Error: {type(self.simple_error).__name__}\n{str(self.simple_error)}"
            )

        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(details)
        messagebox.showinfo("Copied", "Error details copied to clipboard")

    def _save_report(self):
        """Save error report to file."""
        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            title="Save Error Report",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
        )

        if filename:
            try:
                if filename.endswith(".json") and self.apgi_error:
                    # Save as JSON
                    with open(filename, "w") as f:
                        json.dump(self.apgi_error.to_dict(), f, indent=2)
                else:
                    # Save as text
                    with open(filename, "w") as f:
                        if self.apgi_error:
                            f.write(self._format_technical_details())
                        else:
                            f.write(
                                f"Error: {type(self.simple_error).__name__}\n{str(self.simple_error)}"
                            )

                messagebox.showinfo("Saved", f"Error report saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {str(e)}")

    def _try_again(self):
        """Close dialog and suggest trying the operation again."""
        messagebox.showinfo(
            "Try Again",
            "Please try the operation again. If the error persists, check the solutions tab for guidance.",
        )
        self._on_close()

    def _reset_defaults(self):
        """Suggest resetting to default settings."""
        if messagebox.askyesno(
            "Reset Defaults",
            "This will reset configuration to default values. Continue?",
        ):
            # This would trigger actual reset logic in the main application
            messagebox.showinfo(
                "Reset",
                "Configuration has been reset to defaults. Please restart the application.",
            )

    def _get_help(self):
        """Open help documentation."""
        # This would open the help system or documentation
        messagebox.showinfo("Help", "Opening help documentation...")

    def _submit_feedback(self):
        """Submit user feedback."""
        helpful = self.helpful_var.get()
        comments = self.comments_text.get(1.0, tk.END).strip()

        if not helpful:
            messagebox.showwarning(
                "Feedback", "Please indicate if this error report was helpful."
            )
            return

        # Here you would send feedback to a logging system or file
        feedback_data = {
            "error_id": self.apgi_error.error_id if self.apgi_error else "unknown",
            "helpful": helpful,
            "comments": comments,
            "timestamp": str(datetime.datetime.now()),
        }

        # Save feedback locally (in a real implementation, you might send to a server)
        try:
            feedback_file = Path("error_feedback.json")
            if feedback_file.exists():
                with open(feedback_file, "r") as f:
                    existing_feedback = json.load(f)
            else:
                existing_feedback = []

            existing_feedback.append(feedback_data)

            with open(feedback_file, "w") as f:
                json.dump(existing_feedback, f, indent=2)

            messagebox.showinfo(
                "Thank You",
                "Thank you for your feedback! It helps us improve the error handling system.",
            )
        except Exception as e:
            messagebox.showwarning("Feedback", f"Could not save feedback: {str(e)}")

    def _on_close(self):
        """Handle dialog close."""
        self.dialog.destroy()


class ErrorNotificationWidget:
    """Non-intrusive error notification widget."""

    def __init__(self, parent):
        self.parent = parent
        self.notifications = []
        self.notification_frame = None

    def show_notification(
        self, message: str, error_type: str = "error", duration: int = 5000
    ):
        """Show a non-intrusive error notification."""
        if not self.notification_frame:
            self._create_notification_area()

        # Create notification
        notification = ttk.Frame(
            self.notification_frame, relief="raised", borderwidth=1
        )
        notification.pack(fill=tk.X, pady=2)

        # Icon based on error type
        icons = {"error": "❌", "warning": "⚠️", "info": "ℹ️", "success": "✅"}
        icon = icons.get(error_type, "❌")

        # Content
        content_frame = ttk.Frame(notification)
        content_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(content_frame, text=icon, font=("Arial", 12)).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Label(content_frame, text=message, wraplength=400).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

        # Close button
        close_btn = ttk.Button(
            content_frame,
            text="×",
            width=3,
            command=lambda: self._close_notification(notification),
        )
        close_btn.pack(side=tk.RIGHT)

        # Auto-close after duration
        if duration > 0:
            self.parent.after(duration, lambda: self._close_notification(notification))

        self.notifications.append(notification)

    def _create_notification_area(self):
        """Create the notification area."""
        self.notification_frame = ttk.Frame(self.parent)
        self.notification_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

    def _close_notification(self, notification):
        """Close a specific notification."""
        if notification in self.notifications:
            notification.destroy()
            self.notifications.remove(notification)

        # Hide notification area if no notifications
        if not self.notifications and self.notification_frame:
            self.notification_frame.pack_forget()
            self.notification_frame = None


# Convenience functions
def show_error_dialog(parent, error: Exception, user_action: str = None):
    """Show an error dialog with enhanced information."""
    if ERROR_HANDLING_AVAILABLE:
        try:
            # Try to get enhanced error information
            error_handler = get_error_handler()
            apgi_error = error_handler.handle_error(error, user_action)
            ErrorReportDialog(parent, apgi_error=apgi_error)
        except Exception:
            # Fallback to simple error dialog
            ErrorReportDialog(parent, simple_error=error)
    else:
        # Simple error dialog
        ErrorReportDialog(parent, simple_error=error)


def create_error_notification_widget(parent) -> ErrorNotificationWidget:
    """Create an error notification widget."""
    return ErrorNotificationWidget(parent)
