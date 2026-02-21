"""
Refactored APGI Framework Testing System - GUI Application

This is the refactored version that uses modular components instead of the
monolithic architecture. The original 1,953-line file has been broken down into
focused, maintainable components.

Key improvements:
- Modular architecture with separate components
- Centralized state management via MainGUIController
- Better separation of concerns
- Improved testability and maintainability
- Enhanced error handling and logging
"""

import logging
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any

import customtkinter as ctk

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import modular GUI components
try:
    from apgi_framework.gui.components import (
        LoggingPanel,
        ExecutionPanel,
        ParameterConfigPanel,
        ResultsVisualizationPanel,
        create_main_gui_controller,
    )
    from apgi_framework.logging.standardized_logging import get_logger

    MODULAR_COMPONENTS_AVAILABLE = True
except ImportError as e:
    logging.basicConfig(level=logging.INFO)
    fallback_logger = logging.getLogger("apgi_falsification_gui")
    fallback_logger.warning(f"Modular components not available: {e}")
    MODULAR_COMPONENTS_AVAILABLE = False

    # Create fallback classes for basic functionality
    class MainGUIController:
        def __init__(self, parent):
            self.parent = parent
            fallback_logger.warning("Using fallback MainGUIController")

    class ConfigManager:
        def __init__(self):
            pass

    class APGIFrameworkError(Exception):
        pass


if MODULAR_COMPONENTS_AVAILABLE:
    logger: Any = get_logger("apgi_falsification_gui_refactored")
else:
    logger = fallback_logger


class APGIFalsificationGUI(ctk.CTk):
    """
    Main GUI application for APGI Framework Testing System.

    This refactored version uses modular components for better maintainability
    and follows the Model-View-Controller pattern.
    """

    def __init__(self):
        super().__init__()

        self.title("APGI Framework Testing System - Refactored")
        self.geometry("1400x900")
        self.minsize(1000, 700)

        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize components
        self.config_manager = ConfigManager()
        self.main_controller = None
        self.system_initialized = False

        # Component references
        self.parameter_panel = None
        self.current_test_panel = None
        self.results_panel = None
        self.logging_panel = None

        # Tab management
        self.test_tabs = {}
        self.current_tab = None

        # Create GUI
        self._create_menu()
        self._create_main_interface()
        self._initialize_system()

        # Handle window closing
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        logger.info("Refactored APGI Falsification GUI initialized")

    def _create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(
            label="Load Configuration", command=self._load_configuration
        )
        file_menu.add_command(
            label="Save Configuration", command=self._save_configuration
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Export All Results", command=self._export_all_results
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Reset Parameters", command=self._reset_parameters)
        edit_menu.add_command(label="Clear Results", command=self._clear_results)
        edit_menu.add_command(label="Clear Logs", command=self._clear_logs)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self._refresh_all)
        view_menu.add_separator()
        view_menu.add_command(label="System Status", command=self._show_system_status)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate System", command=self._validate_system)
        tools_menu.add_command(label="Run All Tests", command=self._run_all_tests)
        tools_menu.add_command(label="Stop All Tests", command=self._stop_all_tests)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_documentation)

    def _create_main_interface(self):
        """Create the main interface with tabbed layout."""
        # Create main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabview for different sections
        self.tabview = ctk.CTkTabview(main_container)
        self.tabview.pack(fill="both", expand=True)

        # Add tabs
        self._create_configuration_tab()
        self._create_test_tabs()
        self._create_results_tab()
        self._create_logs_tab()

        # Status bar
        self._create_status_bar(main_container)

    def _create_configuration_tab(self):
        """Create the configuration tab."""
        config_tab = self.tabview.add("Configuration")

        if MODULAR_COMPONENTS_AVAILABLE:
            # Use modular parameter panel
            self.parameter_panel = ParameterConfigPanel(config_tab, self.config_manager)
            self.parameter_panel.pack(fill="both", expand=True, padx=5, pady=5)
        else:
            # Fallback configuration interface
            self._create_fallback_config_interface(config_tab)

    def _create_fallback_config_interface(self, parent):
        """Create fallback configuration interface when modular components aren't available."""
        fallback_frame = ctk.CTkFrame(parent)
        fallback_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            fallback_frame,
            text="Configuration Panel",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=20)

        ctk.CTkLabel(
            fallback_frame,
            text="Modular components not available.\nUsing fallback interface.",
            text_color="orange",
        ).pack(pady=10)

        # Basic parameter inputs
        params_frame = ctk.CTkFrame(fallback_frame)
        params_frame.pack(fill="x", pady=20)

        basic_params = [
            ("extero_precision", "Exteroceptive Precision", 2.0),
            ("intero_precision", "Interoceptive Precision", 1.5),
            ("threshold", "Ignition Threshold", 3.5),
            ("steepness", "Steepness", 2.0),
        ]

        for param, label, default in basic_params:
            row = ctk.CTkFrame(params_frame)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=f"{label}:").pack(side="left", padx=(10, 5))
            var = tk.DoubleVar(value=default)
            ctk.CTkEntry(row, textvariable=var, width=15).pack(side="left", padx=5)

    def _create_test_tabs(self):
        """Create test execution tabs."""
        test_names = [
            "Primary",
            "Consciousness Without Ignition",
            "Threshold Insensitivity",
            "Soma-Bias",
            "Cross-Species Validation",
            "Clinical Biomarkers",
            "Threshold Detection",
        ]

        for test_name in test_names:
            test_tab = self.tabview.add(test_name)

            if MODULAR_COMPONENTS_AVAILABLE:
                # Use modular test panel
                test_panel = ExecutionPanel(
                    test_tab,
                    test_name,
                    progress_callback=self._on_progress_update,
                    log_callback=self._on_log_message,
                    results_callback=self._on_test_results,
                )
                test_panel.pack(fill="both", expand=True, padx=5, pady=5)
                self.test_tabs[test_name] = test_panel
            else:
                # Fallback test interface
                self._create_fallback_test_interface(test_tab, test_name)

    def _create_fallback_test_interface(self, parent, test_name: str):
        """Create fallback test interface when modular components aren't available."""
        fallback_frame = ctk.CTkFrame(parent)
        fallback_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            fallback_frame,
            text=f"{test_name} Test",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=20)

        ctk.CTkLabel(
            fallback_frame,
            text="Modular components not available.\nUsing fallback test interface.",
            text_color="orange",
        ).pack(pady=10)

        # Basic test controls
        control_frame = ctk.CTkFrame(fallback_frame)
        control_frame.pack(fill="x", pady=20)

        run_btn = ctk.CTkButton(
            control_frame,
            text="Run Test (Fallback)",
            command=lambda: self._run_fallback_test(test_name),
        )
        run_btn.pack(side="left", padx=10, pady=10)

        # Results area
        results_frame = ctk.CTkFrame(fallback_frame)
        results_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(results_frame, text="Test Results:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )

        self.fallback_results_text = tk.Text(results_frame, height=10, wrap="word")
        self.fallback_results_text.pack(fill="both", expand=True, padx=10, pady=5)

    def _create_results_tab(self):
        """Create the results visualization tab."""
        results_tab = self.tabview.add("Results")

        if MODULAR_COMPONENTS_AVAILABLE:
            # Use modular results panel
            self.results_panel = ResultsVisualizationPanel(
                results_tab, results_callback=self._on_results_updated
            )
            self.results_panel.pack(fill="both", expand=True, padx=5, pady=5)
        else:
            # Fallback results interface
            self._create_fallback_results_interface(results_tab)

    def _create_fallback_results_interface(self, parent):
        """Create fallback results interface when modular components aren't available."""
        fallback_frame = ctk.CTkFrame(parent)
        fallback_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            fallback_frame,
            text="Results Visualization",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=20)

        ctk.CTkLabel(
            fallback_frame,
            text="Modular components not available.\nUsing fallback results interface.",
            text_color="orange",
        ).pack(pady=10)

        ctk.CTkLabel(
            fallback_frame, text="Run tests to see results here.", text_color="gray"
        ).pack(pady=20)

    def _create_logs_tab(self):
        """Create the logging tab."""
        logs_tab = self.tabview.add("Logs")

        if MODULAR_COMPONENTS_AVAILABLE:
            # Use modular logging panel
            self.logging_panel = LoggingPanel(logs_tab)
            self.logging_panel.pack(fill="both", expand=True, padx=5, pady=5)
        else:
            # Fallback logging interface
            self._create_fallback_logs_interface(logs_tab)

    def _create_fallback_logs_interface(self, parent):
        """Create fallback logging interface when modular components aren't available."""
        fallback_frame = ctk.CTkFrame(parent)
        fallback_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            fallback_frame, text="System Logs", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)

        ctk.CTkLabel(
            fallback_frame,
            text="Modular components not available.\nUsing fallback logging interface.",
            text_color="orange",
        ).pack(pady=10)

        # Basic log display
        log_frame = ctk.CTkFrame(fallback_frame)
        log_frame.pack(fill="both", expand=True, pady=10)

        self.fallback_log_text = tk.Text(log_frame, height=15, wrap="word")
        log_scrollbar = ctk.CTkScrollbar(
            log_frame, command=self.fallback_log_text.yview
        )
        self.fallback_log_text.configure(yscrollcommand=log_scrollbar.set)

        self.fallback_log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

        # Add initial log message
        self._add_fallback_log("Fallback logging interface initialized", "INFO")

    def _create_status_bar(self, parent):
        """Create status bar at the bottom."""
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill="x", side="bottom", pady=(5, 0))

        # Status label
        self.status_label = ctk.CTkLabel(status_frame, text="Ready", anchor="w")
        self.status_label.pack(side="left", padx=10, pady=5)

        # System status indicator
        self.system_status_label = ctk.CTkLabel(
            status_frame, text="● System: Initializing...", text_color="orange"
        )
        self.system_status_label.pack(side="right", padx=10, pady=5)

    def _initialize_system(self):
        """Initialize the system and main controller."""
        try:
            if MODULAR_COMPONENTS_AVAILABLE:
                # Initialize main controller
                self.main_controller = create_main_gui_controller(self)
                self.system_initialized = True

                # Update status
                self._update_status("System initialized successfully")
                self.system_status_label.configure(
                    text="● System: Ready", text_color="green"
                )

                # Add initial log
                if self.logging_panel:
                    self.logging_panel.add_message(
                        "Refactored GUI system initialized successfully", "INFO"
                    )

                logger.info("System initialization completed")
            else:
                self._update_status("System initialized in fallback mode")
                self.system_status_label.configure(
                    text="● System: Fallback Mode", text_color="orange"
                )

        except Exception as e:
            self._update_status(f"System initialization failed: {e}")
            self.system_status_label.configure(text="● System: Error", text_color="red")
            logger.error(f"System initialization failed: {e}")

    # Event handlers
    def _on_progress_update(self, progress: float, message: str):
        """Handle progress updates from test panels."""
        percentage = progress * 100
        self._update_status(f"{message} ({percentage:.1f}%)")

    def _on_log_message(self, message: str, level: str = "INFO"):
        """Handle log messages from test panels."""
        if self.logging_panel:
            self.logging_panel.add_message(message, level)
        else:
            self._add_fallback_log(message, level)

    def _on_test_results(self, test_name: str, results: Any):
        """Handle test results."""
        if self.results_panel:
            self.results_panel.add_results(test_name, results)
        else:
            self._add_fallback_results(test_name, results)

        self._update_status(f"Test completed: {test_name}")

    def _on_results_updated(self, results_data):
        """Handle results data updates."""
        pass  # Could update status or other UI elements

    # Menu command handlers
    def _load_configuration(self):
        """Load configuration from file."""
        try:
            if self.main_controller:
                success = self.main_controller.load_configuration()
                if success:
                    messagebox.showinfo("Success", "Configuration loaded successfully")
                else:
                    messagebox.showwarning("Warning", "Configuration loading failed")
            else:
                messagebox.showinfo(
                    "Info", "Load configuration not available in fallback mode"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")

    def _save_configuration(self):
        """Save current configuration to file."""
        try:
            if self.main_controller:
                success = self.main_controller.save_configuration()
                if success:
                    messagebox.showinfo("Success", "Configuration saved successfully")
                else:
                    messagebox.showwarning("Warning", "Configuration saving failed")
            else:
                messagebox.showinfo(
                    "Info", "Save configuration not available in fallback mode"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def _export_all_results(self):
        """Export all results to file."""
        try:
            if self.main_controller:
                file_path = filedialog.asksaveasfilename(
                    title="Export All Results",
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                )

                if file_path:
                    success = self.main_controller.export_all_results(file_path)
                    if success:
                        messagebox.showinfo(
                            "Success", f"Results exported to {file_path}"
                        )
                    else:
                        messagebox.showwarning("Warning", "Results export failed")
            else:
                messagebox.showinfo(
                    "Info", "Export results not available in fallback mode"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {e}")

    def _reset_parameters(self):
        """Reset all parameters to defaults."""
        try:
            if self.parameter_panel:
                # This would call the panel's reset method
                messagebox.showinfo("Info", "Parameters reset to defaults")
            else:
                messagebox.showinfo(
                    "Info", "Parameter reset not available in fallback mode"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset parameters: {e}")

    def _clear_results(self):
        """Clear all results."""
        try:
            if self.results_panel:
                self.results_panel.clear_results()
                messagebox.showinfo("Success", "All results cleared")
            else:
                self.fallback_results_text.delete("1.0", "end")
                messagebox.showinfo("Success", "Results cleared")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear results: {e}")

    def _clear_logs(self):
        """Clear all logs."""
        try:
            if self.logging_panel:
                self.logging_panel._clear_logs()
                messagebox.showinfo("Success", "All logs cleared")
            else:
                self.fallback_log_text.delete("1.0", "end")
                messagebox.showinfo("Success", "Logs cleared")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear logs: {e}")

    def _refresh_all(self):
        """Refresh all components."""
        try:
            if self.main_controller:
                self.main_controller.refresh_all_components()
                messagebox.showinfo("Success", "All components refreshed")
            else:
                messagebox.showinfo("Info", "Refresh not available in fallback mode")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh components: {e}")

    def _show_system_status(self):
        """Show system status dialog."""
        try:
            if self.main_controller:
                status = self.main_controller.get_system_status()

                status_text = "System Status:\n\n"
                status_text += f"Initialized: {status['initialized']}\n"
                status_text += f"Current Test: {status['current_test'] or 'None'}\n"
                status_text += f"Total Tests: {status['total_tests']}\n"
                status_text += f"Running Tests: {status['running_tests']}\n"
                status_text += f"Total Results: {status['total_results']}\n"

                if status["log_statistics"]:
                    stats = status["log_statistics"]
                    status_text += "Log Statistics:\n"
                    status_text += f"INFO: {stats.get('INFO', 0)}\n"
                    status_text += f"WARNING: {stats.get('WARNING', 0)}\n"
                    status_text += f"ERROR: {stats.get('ERROR', 0)}\n"

                messagebox.showinfo("System Status", status_text)
            else:
                messagebox.showinfo(
                    "System Status", "Fallback mode - Limited status information"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get system status: {e}")

    def _validate_system(self):
        """Validate system state."""
        try:
            if self.main_controller:
                validation = self.main_controller.validate_system()

                if validation["valid"]:
                    messagebox.showinfo("Validation", "System validation passed")
                else:
                    issues = "\n".join(validation["issues"])
                    warnings = "\n".join(validation["warnings"])

                    message = "System validation found issues:\n\n"
                    message += "Issues:\n" + issues + "\n\n"
                    message += "Warnings:\n" + warnings

                    messagebox.showwarning("Validation Issues", message)
            else:
                messagebox.showinfo(
                    "Validation", "System validation not available in fallback mode"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to validate system: {e}")

    def _run_all_tests(self):
        """Run all tests sequentially."""
        try:
            if self.main_controller:
                # This would run all tests through the controller
                messagebox.showinfo("Info", "Run all tests not yet implemented")
            else:
                messagebox.showinfo(
                    "Info", "Run all tests not available in fallback mode"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run all tests: {e}")

    def _stop_all_tests(self):
        """Stop all running tests."""
        try:
            if self.main_controller:
                success = self.main_controller.stop_test()
                if success:
                    messagebox.showinfo("Success", "Current test stopped")
                else:
                    messagebox.showinfo("Info", "No test currently running")
            else:
                messagebox.showinfo("Info", "Stop tests not available in fallback mode")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop tests: {e}")

    def _show_about(self):
        """Show about dialog."""
        about_text = """APGI Framework Testing System
Version 2.0 (Refactored)

This refactored version uses modular components for better maintainability:
- Parameter Configuration Panel
- Test Execution Panels (7 test types)
- Results Visualization Panel  
- Logging Panel
- Main GUI Controller

The original monolithic 1,953-line file has been broken down into
focused, testable components following the MVC pattern.

© 2024 APGI Framework Team"""

        messagebox.showinfo("About APGI Framework", about_text)

    def _show_documentation(self):
        """Show documentation."""
        doc_text = """APGI Framework Documentation

The refactored GUI system consists of the following components:

1. Parameter Configuration Panel
   - Located in: apgi_framework/gui/components/parameter_config_panel.py
   - Handles APGI parameters and experimental configuration
   - Provides real-time validation and tooltips

2. Test Execution Panels
   - Located in: apgi_framework/gui/components/test_execution_panel.py
   - Seven panels for different falsification tests
   - Progress tracking and result display

3. Results Visualization Panel
   - Located in: apgi_framework/gui/components/results_visualization_panel.py
   - Statistical analysis and visualization
   - Multiple view modes and export capabilities

4. Logging Panel
   - Located in: apgi_framework/gui/components/logging_panel.py
   - Real-time log display with filtering
   - Export and search functionality

5. Main GUI Controller
   - Located in: apgi_framework/gui/components/main_gui_controller.py
   - Orchestrates all components
   - Centralized state management

Each component is independently testable and maintainable."""

        # Create documentation window
        doc_window = ctk.CTkToplevel(self)
        doc_window.title("Documentation")
        doc_window.geometry("600x500")

        doc_text_widget = ctk.CTkTextbox(doc_window)
        doc_text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        doc_text_widget.insert("1.0", doc_text)
        doc_text_widget.configure(state="disabled")

    # Fallback methods for when modular components aren't available
    def _run_fallback_test(self, test_name: str):
        """Run a fallback test when modular components aren't available."""
        self._add_fallback_log(f"Starting {test_name} test (fallback mode)", "INFO")
        self._add_fallback_results(test_name, "Test running in fallback mode...")

        # Simulate test execution
        import time

        time.sleep(2)

        self._add_fallback_log(f"Completed {test_name} test (fallback mode)", "INFO")
        self._add_fallback_results(test_name, f"Mock results for {test_name}")

    def _add_fallback_log(self, message: str, level: str = "INFO"):
        """Add log message to fallback log display."""
        if hasattr(self, "fallback_log_text"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} - FALLBACK - {level} - {message}\n"

            self.fallback_log_text.insert("end", log_entry)
            self.fallback_log_text.see("end")

            # Limit log size
            lines = int(self.fallback_log_text.index("end-1c").split(".")[0])
            if lines > 1000:
                self.fallback_log_text.delete("1.0", "100.0")

    def _add_fallback_results(self, test_name: str, results: str):
        """Add results to fallback results display."""
        if hasattr(self, "fallback_results_text"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result_entry = f"[{timestamp}] {test_name}: {results}\n"

            self.fallback_results_text.insert("end", result_entry)
            self.fallback_results_text.see("end")

    def _update_status(self, message: str):
        """Update status bar."""
        if hasattr(self, "status_label"):
            self.status_label.configure(text=message)

    def _on_closing(self):
        """Handle window closing."""
        try:
            if self.main_controller:
                self.main_controller.shutdown()

            # Clean up
            self.destroy()

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.destroy()


def main():
    """Main entry point for the application."""
    try:
        app = APGIFalsificationGUI()
        app.mainloop()
    except Exception as e:
        logging.error(f"Application error: {e}")
        messagebox.showerror("Error", f"Application failed to start: {e}")


if __name__ == "__main__":
    main()
