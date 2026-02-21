"""Paginated Log Viewer for APGI Framework to improve performance with large log files."""

import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import List

import customtkinter as ctk  # type: ignore[import]

from apgi_framework.logging.standardized_logging import get_logger


class PaginatedLogViewer:
    """A paginated log viewer that loads log files in chunks for better performance."""

    def __init__(self, parent_window, log_file_path: str):
        """Initialize the paginated log viewer.

        Args:
            parent_window: Parent tkinter window
            log_file_path: Path to the log file
        """
        self.parent = parent_window
        self.log_file_path = Path(log_file_path)
        self.logger = get_logger(__name__)

        # Pagination settings
        self.lines_per_page = 500  # Number of lines per page
        self.current_page = 0
        self.total_lines = 0
        self.filtered_lines: List[str] = []

        # Filtering and search
        self.level_filter = "ALL"
        self.search_term = ""

        # UI components
        self.window = None
        self.log_text = None
        self.page_label = None
        self.prev_btn = None
        self.next_btn = None

        # Load log file
        self._load_log_file()

    def _load_log_file(self):
        """Load the log file and count total lines."""
        try:
            if self.log_file_path.exists():
                with open(
                    self.log_file_path, "r", encoding="utf-8", errors="ignore"
                ) as f:
                    self.total_lines = sum(1 for _ in f)
                self.logger.info(f"Loaded log file with {self.total_lines} lines")
            else:
                self.total_lines = 0
                self.logger.warning(f"Log file not found: {self.log_file_path}")
        except Exception as e:
            self.logger.error(f"Error loading log file: {e}")
            self.total_lines = 0

    def show(self):
        """Show the paginated log viewer window."""
        # Create window
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Paginated Log Viewer")
        self.window.geometry("1000x700")
        self.window.transient(self.parent)
        self.window.grab_set()

        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(2, weight=1)

        # Create UI
        self._create_header()
        self._create_controls()
        self._create_log_display()
        self._create_pagination_controls()

        # Load initial content
        self._refresh_display()

        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

    def _create_header(self):
        """Create the header section."""
        header_frame = ctk.CTkFrame(self.window)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"Log Viewer: {self.log_file_path.name}",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # File info
        info_label = ctk.CTkLabel(
            header_frame,
            text=f"Total lines: {self.total_lines:,}",
            font=ctk.CTkFont(size=12),
        )
        info_label.grid(row=0, column=1, padx=10, pady=10, sticky="e")

    def _create_controls(self):
        """Create the control section with filters and search."""
        control_frame = ctk.CTkFrame(self.window)
        control_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        control_frame.grid_columnconfigure((1, 3), weight=1)

        # Log level filter
        level_label = ctk.CTkLabel(control_frame, text="Log Level:")
        level_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.level_var = tk.StringVar(value="ALL")
        level_menu = ctk.CTkOptionMenu(
            control_frame,
            variable=self.level_var,
            values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            command=self._on_filter_change,
        )
        level_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Search box
        search_label = ctk.CTkLabel(control_frame, text="Search:")
        search_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(control_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())

        # Lines per page
        lines_label = ctk.CTkLabel(control_frame, text="Lines per page:")
        lines_label.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        self.lines_var = tk.StringVar(value=str(self.lines_per_page))
        lines_menu = ctk.CTkOptionMenu(
            control_frame,
            variable=self.lines_var,
            values=["100", "250", "500", "1000", "2000"],
            command=self._on_lines_per_page_change,
        )
        lines_menu.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

    def _create_log_display(self):
        """Create the log text display area."""
        # Log display frame
        display_frame = ctk.CTkFrame(self.window)
        display_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_rowconfigure(0, weight=1)

        # Create scrollable text widget
        self.log_text = ctk.CTkTextbox(display_frame, wrap="word")
        self.log_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Add scrollbar
        scrollbar = ctk.CTkScrollbar(display_frame, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, padx=5, pady=5, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _create_pagination_controls(self):
        """Create pagination controls."""
        pagination_frame = ctk.CTkFrame(self.window)
        pagination_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        pagination_frame.grid_columnconfigure((1, 2, 3, 4, 5, 6, 7), weight=1)

        # First page button
        first_btn = ctk.CTkButton(
            pagination_frame, text="|<", width=40, command=self._first_page
        )
        first_btn.grid(row=0, column=0, padx=2, pady=5)

        # Previous page button
        self.prev_btn = ctk.CTkButton(
            pagination_frame, text="<", width=40, command=self._prev_page
        )
        self.prev_btn.grid(row=0, column=1, padx=2, pady=5)

        # Page info
        self.page_label = ctk.CTkLabel(
            pagination_frame, text="Page 0 of 0", font=ctk.CTkFont(size=12)
        )
        self.page_label.grid(row=0, column=2, padx=10, pady=5)

        # Current page input
        self.page_var = tk.StringVar(value="1")
        page_entry = ctk.CTkEntry(
            pagination_frame, textvariable=self.page_var, width=60
        )
        page_entry.grid(row=0, column=3, padx=2, pady=5)
        page_entry.bind("<Return>", lambda e: self._go_to_page())

        # Total pages label
        self.total_pages_label = ctk.CTkLabel(
            pagination_frame, text="of 0", font=ctk.CTkFont(size=12)
        )
        self.total_pages_label.grid(row=0, column=4, padx=2, pady=5)

        # Next page button
        self.next_btn = ctk.CTkButton(
            pagination_frame, text=">", width=40, command=self._next_page
        )
        self.next_btn.grid(row=0, column=5, padx=2, pady=5)

        # Last page button
        last_btn = ctk.CTkButton(
            pagination_frame, text=">|", width=40, command=self._last_page
        )
        last_btn.grid(row=0, column=6, padx=2, pady=5)

        # Action buttons
        refresh_btn = ctk.CTkButton(
            pagination_frame, text="Refresh", command=self._refresh_display
        )
        refresh_btn.grid(row=0, column=7, padx=5, pady=5)

        export_btn = ctk.CTkButton(
            pagination_frame,
            text="Export Current Page",
            command=self._export_current_page,
        )
        export_btn.grid(row=0, column=8, padx=5, pady=5)

        close_btn = ctk.CTkButton(
            pagination_frame, text="Close", command=self.window.destroy
        )
        close_btn.grid(row=0, column=9, padx=5, pady=5)

    def _apply_filters(self) -> List[str]:
        """Apply level and search filters to log lines."""
        filtered_lines = []

        try:
            if not self.log_file_path.exists():
                return ["Log file not found."]

            with open(self.log_file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.rstrip("\n\r")

                    # Apply level filter
                    if self.level_filter != "ALL":
                        if self.level_filter not in line:
                            continue

                    # Apply search filter
                    if self.search_term:
                        if self.search_term.lower() not in line.lower():
                            continue

                    filtered_lines.append(line)

        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")
            return [f"Error reading log file: {e}"]

        return filtered_lines

    def _get_page_lines(self) -> List[str]:
        """Get the lines for the current page."""
        if not self.filtered_lines:
            self.filtered_lines = self._apply_filters()

        start_idx = self.current_page * self.lines_per_page
        end_idx = start_idx + self.lines_per_page

        return self.filtered_lines[start_idx:end_idx]

    def _refresh_display(self):
        """Refresh the log display."""
        # Apply filters
        self.filtered_lines = self._apply_filters()

        # Reset to first page if current page is out of bounds
        total_pages = max(
            1,
            (len(self.filtered_lines) + self.lines_per_page - 1) // self.lines_per_page,
        )
        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)

        # Get current page lines
        page_lines = self._get_page_lines()

        # Update text widget
        self.log_text.delete("1.0", "end")
        if page_lines:
            self.log_text.insert("1.0", "\n".join(page_lines))
        else:
            self.log_text.insert("1.0", "No log lines match the current filters.")

        # Update pagination info
        self._update_pagination_info()

    def _update_pagination_info(self):
        """Update pagination controls and info."""
        total_pages = max(
            1,
            (len(self.filtered_lines) + self.lines_per_page - 1) // self.lines_per_page,
        )

        # Update labels
        self.page_label.configure(text=f"Page {self.current_page + 1} of {total_pages}")
        self.total_pages_label.configure(text=f"of {total_pages}")
        self.page_var.set(str(self.current_page + 1))

        # Update button states
        self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.configure(
            state="normal" if self.current_page < total_pages - 1 else "disabled"
        )

    def _first_page(self):
        """Go to first page."""
        self.current_page = 0
        self._refresh_display()

    def _prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._refresh_display()

    def _next_page(self):
        """Go to next page."""
        total_pages = max(
            1,
            (len(self.filtered_lines) + self.lines_per_page - 1) // self.lines_per_page,
        )
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._refresh_display()

    def _last_page(self):
        """Go to last page."""
        total_pages = max(
            1,
            (len(self.filtered_lines) + self.lines_per_page - 1) // self.lines_per_page,
        )
        self.current_page = total_pages - 1
        self._refresh_display()

    def _go_to_page(self):
        """Go to specific page number."""
        try:
            page_num = int(self.page_var.get()) - 1
            total_pages = max(
                1,
                (len(self.filtered_lines) + self.lines_per_page - 1)
                // self.lines_per_page,
            )

            if 0 <= page_num < total_pages:
                self.current_page = page_num
                self._refresh_display()
            else:
                messagebox.showwarning(
                    "Invalid Page",
                    f"Page number must be between 1 and {total_pages}",
                )
                self.page_var.set(str(self.current_page + 1))
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid page number")
            self.page_var.set(str(self.current_page + 1))

    def _on_filter_change(self, *args):
        """Handle filter change."""
        self.level_filter = self.level_var.get()
        self.current_page = 0  # Reset to first page
        self._refresh_display()

    def _on_search_change(self):
        """Handle search change."""
        self.search_term = self.search_var.get()
        self.current_page = 0  # Reset to first page
        self._refresh_display()

    def _on_lines_per_page_change(self, *args):
        """Handle lines per page change."""
        try:
            self.lines_per_page = int(self.lines_var.get())
            self.current_page = 0  # Reset to first page
            self._refresh_display()
        except ValueError:
            pass

    def _export_current_page(self):
        """Export current page to a file."""
        try:
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                title="Export Log Page",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                initialfile=f"log_page_{self.current_page + 1}.txt",
            )

            if filename:
                page_lines = self._get_page_lines()
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(
                        f"Log Page {self.current_page + 1} - {len(page_lines)} lines\n"
                    )
                    f.write("=" * 50 + "\n\n")
                    f.write("\n".join(page_lines))

                messagebox.showinfo("Export Complete", f"Page exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export page: {e}")
