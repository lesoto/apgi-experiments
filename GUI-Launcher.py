#!/usr/bin/env python3
"""
Comprehensive GUI Launcher for APGI Framework

This script provides a centralized launcher to access all GUI applications
and tools
in the APGI Framework, organized by category for easy navigation.
"""

import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


# Configuration constants
class UIConfig:
    """UI configuration constants."""

    # Window scaling factors for different screen sizes
    SCALE_4K = 0.6
    SCALE_QHD = 0.7
    SCALE_FHD = 0.8
    SCALE_SMALL = 0.85

    # Layout spacing (pixels)
    MAIN_CONTAINER_PADDING = 30
    HEADER_SPACING = 25
    BOTTOM_BUTTON_SPACING = 25
    CATEGORY_SPACING = (20, 15)
    CARD_CONTENT_PADDING = (20, 15)
    CARD_BUTTON_PADDING = (20, 0)

    # Button dimensions
    BUTTON_PADDING_LARGE = (20, 10)
    BUTTON_PADDING_LAUNCH = (25, 12)
    BUTTON_PADDING_CLOSE = (20, 8)

    # Font sizes
    FONT_ICON_SIZE = 20
    FONT_TITLE_SIZE = 36
    FONT_SUBTITLE_SIZE = 13

    # Text wrapping
    DESCRIPTION_WRAP_LENGTH = 1200  # Increased for better use of width

    # Window geometry for info dialog
    INFO_WINDOW_WIDTH = 600
    INFO_WINDOW_HEIGHT = 500


class ComprehensiveGUILauncher:
    """Comprehensive launcher for all APGI Framework GUI applications."""

    def __init__(self):
        """Initialize the comprehensive launcher."""
        self.root = tk.Tk()
        self.root.title("APGI Framework - Comprehensive GUI Launcher")

        # Adaptive window sizing based on screen resolution and DPI
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Use DPI-aware scaling without hard caps
        # Scale factor for different screen sizes
        if screen_width >= 3840:  # 4K displays
            scale_factor = UIConfig.SCALE_4K
        elif screen_width >= 2560:  # QHD/2K displays
            scale_factor = UIConfig.SCALE_QHD
        elif screen_width >= 1920:  # Full HD
            scale_factor = UIConfig.SCALE_FHD
        else:  # Smaller displays
            scale_factor = UIConfig.SCALE_SMALL

        window_width = int(screen_width * scale_factor)
        window_height = int(screen_height * scale_factor)

        # Center window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(True, True)

        # Set window icon and styling
        self.root.configure(bg="#ecf0f1")

        # Configure styles
        self.setup_styles()

        # Define GUI applications
        self.gui_apps = self.define_gui_applications()

        # Check application availability
        self.check_app_availability()

        # Create widgets
        self.create_widgets()

    def setup_styles(self):
        """Setup custom styles for better appearance."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure custom styles
        self.style.configure(
            "Title.TLabel",
            font=("Helvetica", 34, "bold"),
            background="#ecf0f1",
            foreground="#1f2d3d",
        )

        self.style.configure(
            "Subtitle.TLabel",
            font=("Helvetica", 12),
            background="#ecf0f1",
            foreground="#5c6b77",
        )

        self.style.configure(
            "Category.TLabel",
            font=("Helvetica", 18, "bold"),
            background="#ecf0f1",
            foreground="#22313f",
        )

        self.style.configure(
            "App.TLabel",
            font=("Helvetica", 13, "bold"),
            background="#ffffff",
            foreground="#1f2d3d",
        )

        self.style.configure(
            "Desc.TLabel",
            font=("Helvetica", 10),
            background="#ffffff",
            foreground="#4d5d6c",
        )

        self.style.configure(
            "Path.TLabel",
            font=("Courier", 9, "italic"),
            background="#ffffff",
            foreground="#6c7a89",
        )

        self.style.configure(
            "Launch.TButton",
            font=("Helvetica", 11, "bold"),
            padding=UIConfig.BUTTON_PADDING_LARGE,
        )

        # High-contrast ttk button styles
        self.style.configure(
            "Primary.TButton",
            font=("Helvetica", 11, "bold"),
            background="#3498db",
            foreground="#ffffff",
            padding=UIConfig.BUTTON_PADDING_LARGE,
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", "#2d86c5")],
            foreground=[("active", "#ffffff")],
        )
        self.style.configure(
            "Secondary.TButton",
            font=("Helvetica", 11, "bold"),
            background="#7f8c8d",
            foreground="#ffffff",
            padding=UIConfig.BUTTON_PADDING_LARGE,
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#6c7778")],
            foreground=[("active", "#ffffff")],
        )
        self.style.configure(
            "Danger.TButton",
            font=("Helvetica", 11, "bold"),
            background="#e74c3c",
            foreground="#ffffff",
            padding=UIConfig.BUTTON_PADDING_LARGE,
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", "#c0392b")],
            foreground=[("active", "#ffffff")],
        )

        self.style.configure(
            "Status.TLabel",
            font=("Helvetica", 9, "bold"),
            background="#ffffff",
        )

    def check_app_availability(self):
        """Check which applications are available."""
        self.app_status = {}
        current_dir = Path(__file__).parent

        for category, apps in self.gui_apps.items():
            for app in apps:
                script_path = current_dir / app["file"]
                self.app_status[app["file"]] = script_path.exists()

    def define_gui_applications(self):
        """Define all GUI applications organized by category."""
        return {
            "Main Applications": [
                {
                    "name": "Full-Featured GUI",
                    "file": "GUI.py",
                    "description": "Complete APGI Framework interface with all features",
                    "icon": "[Target]",
                    "command": self.launch_full_gui,
                },
                {
                    "name": "APGI Framework App",
                    "file": "apgi_gui/app.py",
                    "description": "Modern CustomTkinter-based framework application",
                    "icon": "[Rocket]",
                    "command": self.launch_apgi_gui_app,
                },
                {
                    "name": "Experiment Registry GUI",
                    "file": "GUI-Experiment-Registry.py",
                    "description": "Experiment registry and management interface",
                    "icon": "[Registry]",
                    "command": self.launch_experiment_registry,
                },
            ],
            "Experiment Management": [
                {
                    "name": "Experiment Runner",
                    "file": "apps/experiment_runner_gui.py",
                    "description": "Run and manage experiments with comprehensive controls and monitoring",
                    "icon": "[Play]",
                    "command": self.launch_experiment_runner,
                },
                {
                    "name": "Simple Experiment Runner",
                    "file": "utils/gui-simple-experiment-runner.py",
                    "description": "Simplified GUI for running experiments",
                    "icon": "[Simple]",
                    "command": self.launch_simple_experiment_runner,
                },
            ],
            "Analysis & Visualization": [
                {
                    "name": "Parameter Estimation GUI",
                    "file": "apgi_framework/gui/parameter_estimation_gui.py",
                    "description": "Parameter estimation and analysis tools",
                    "icon": "[Data]",
                    "command": self.launch_parameter_estimation,
                },
                {
                    "name": "Interactive Dashboard",
                    "file": "apgi_framework/gui/interactive_dashboard.py",
                    "description": "Web-based interactive dashboard (requires Flask)",
                    "icon": "[Web]",
                    "command": self.launch_interactive_dashboard,
                },
                {
                    "name": "Monitoring Dashboard",
                    "file": "apgi_framework/gui/monitoring_dashboard.py",
                    "description": "Real-time monitoring dashboard",
                    "icon": "[Chart]",
                    "command": self.launch_monitoring_dashboard,
                },
                {
                    "name": "Web Monitoring Dashboard",
                    "file": "apgi_framework/gui/web_monitoring_dashboard.py",
                    "description": "Web-based real-time monitoring",
                    "icon": "[Browser]",
                    "command": self.launch_web_monitoring_dashboard,
                },
                {
                    "name": "Reporting & Visualization",
                    "file": "apgi_framework/gui/reporting_visualization.py",
                    "description": "Generate reports and visualizations",
                    "icon": "[Report]",
                    "command": self.launch_reporting_visualization,
                },
            ],
            "Configuration & Tools": [
                {
                    "name": "Utils GUI",
                    "file": "Utils-GUI.py",
                    "description": "Utility script runner with GUI interface",
                    "icon": "[Tools]",
                    "command": self.launch_utils_gui,
                },
                {
                    "name": "Task Configuration",
                    "file": "apgi_framework/gui/task_configuration.py",
                    "description": "Configure experimental tasks",
                    "icon": "[Config]",
                    "command": self.launch_task_configuration,
                },
                {
                    "name": "Session Management",
                    "file": "apgi_framework/gui/session_management.py",
                    "description": "Manage experimental sessions",
                    "icon": "[Session]",
                    "command": self.launch_session_management,
                },
                {
                    "name": "Progress Monitoring",
                    "file": "apgi_framework/gui/progress_monitoring.py",
                    "description": "Monitor experiment progress",
                    "icon": "[Data]",
                    "command": self.launch_progress_monitoring,
                },
                {
                    "name": "Coverage Visualization",
                    "file": "apgi_framework/gui/coverage_visualization.py",
                    "description": "Test coverage visualization tool",
                    "icon": "[Coverage]",
                    "command": self.launch_coverage_visualization,
                },
                {
                    "name": "Enhanced Monitoring Dashboard",
                    "file": "apgi_framework/gui/enhanced_monitoring_dashboard.py",
                    "description": "Enhanced monitoring with advanced features",
                    "icon": "[Monitor]",
                    "command": self.launch_enhanced_monitoring_dashboard,
                },
                {
                    "name": "Results Viewer",
                    "file": "apgi_framework/gui/results_viewer.py",
                    "description": "View and analyze experiment results",
                    "icon": "[Results]",
                    "command": self.launch_results_viewer,
                },
            ],
            "Development & Testing": [
                {
                    "name": "Tests GUI",
                    "file": "Tests-GUI.py",
                    "description": "Comprehensive test runner with GUI interface",
                    "icon": "[Tests]",
                    "command": self.launch_tests_gui,
                },
                {
                    "name": "GUI Template",
                    "file": "apps/gui_template_background.py",
                    "description": "Template for GUI development",
                    "icon": "[Tools]",
                    "command": self.launch_gui_template,
                },
                {
                    "name": "GUI Template (Main)",
                    "file": "apps/gui_template.py",
                    "description": "Main GUI template for development",
                    "icon": "[Template]",
                    "command": self.launch_gui_template_main,
                },
                {
                    "name": "Error Handling Demo",
                    "file": "apgi_framework/gui/error_handling.py",
                    "description": "Error handling demonstration",
                    "icon": "[Warning]",
                    "command": self.launch_error_handling,
                },
            ],
            "CLI Tools & Utilities": [
                {
                    "name": "Comprehensive Test Runner",
                    "file": "run_tests.py",
                    "description": "Run comprehensive test suite with GUI integration",
                    "icon": "[Test]",
                    "command": self.launch_test_runner,
                },
                {
                    "name": "Experiment Runner (CLI)",
                    "file": "run_experiments.py",
                    "description": "Command-line experiment runner with all experiments",
                    "icon": "[CLI]",
                    "command": self.launch_experiment_runner_cli,
                },
                {
                    "name": "Framework CLI",
                    "file": "apgi_framework/cli.py",
                    "description": "Main command-line interface for APGI Framework",
                    "icon": "[Terminal]",
                    "command": self.launch_framework_cli,
                },
                {
                    "name": "Diagnostics CLI",
                    "file": "apgi_framework/validation/diagnostics_cli.py",
                    "description": "System diagnostics and validation tools",
                    "icon": "[Diag]",
                    "command": self.launch_diagnostics_cli,
                },
                {
                    "name": "Deployment CLI",
                    "file": "apgi_framework/deployment/cli.py",
                    "description": "Deployment automation and management",
                    "icon": "[Deploy]",
                    "command": self.launch_deployment_cli,
                },
            ],
            "Setup & Deployment": [
                {
                    "name": "Installer Utility",
                    "file": "utils/install_dependencies.py",
                    "description": "Installation and dependency setup utility",
                    "icon": "[Setup]",
                    "command": self.launch_setup_script,
                },
                {
                    "name": "Deployment Validator",
                    "file": "apgi_framework/deployment/deployment_validator.py",
                    "description": "System deployment and validation tool",
                    "icon": "[Check]",
                    "command": self.launch_quick_deploy,
                },
                {
                    "name": "Delete Cache",
                    "file": "delete_pycache.py",
                    "description": "Clean Python cache files",
                    "icon": "[Clean]",
                    "command": self.launch_delete_cache,
                },
            ],
            "Examples & Demos": [
                {
                    "name": "Data Loader Example",
                    "file": "examples/data_loader.py",
                    "description": "Data loading utility example",
                    "icon": "[Data]",
                    "command": self.launch_data_loader_example,
                },
                {
                    "name": "Coverage Collector Demo",
                    "file": "examples/coverage_collector_demo.py",
                    "description": "Coverage collection demonstration",
                    "icon": "[Coverage]",
                    "command": self.launch_coverage_collector_demo,
                },
                {
                    "name": "Primary Falsification Test",
                    "file": "examples/01_run_primary_falsification_test.py",
                    "description": "Run primary falsification test example",
                    "icon": "[Primary]",
                    "command": self.launch_primary_falsification_test,
                },
                {
                    "name": "Batch Processing Config",
                    "file": "examples/02_batch_processing_configurations.py",
                    "description": "Batch processing configuration example",
                    "icon": "[Batch]",
                    "command": self.launch_batch_processing_config,
                },
                {
                    "name": "Custom Analysis Results",
                    "file": "examples/03_custom_analysis_saved_results.py",
                    "description": "Custom analysis of saved results",
                    "icon": "[Analysis]",
                    "command": self.launch_custom_analysis_results,
                },
                {
                    "name": "Extending Falsification Criteria",
                    "file": "examples/04_extending_falsification_criteria.py",
                    "description": "Extend falsification criteria example",
                    "icon": "[Extend]",
                    "command": self.launch_extending_falsification_criteria,
                },
            ],
        }

    def create_widgets(self):
        """Create launcher widgets with organized layout."""
        # Main container
        main_container = tk.Frame(self.root, bg="#ecf0f1")
        main_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=UIConfig.MAIN_CONTAINER_PADDING,
            pady=UIConfig.MAIN_CONTAINER_PADDING,
        )

        # Header section
        header_frame = tk.Frame(main_container, bg="#ecf0f1")
        header_frame.pack(fill=tk.X, pady=(0, UIConfig.HEADER_SPACING))

        # Title and subtitle
        title_label = tk.Label(
            header_frame,
            text="APGI Framework Launcher",
            font=("Helvetica", UIConfig.FONT_TITLE_SIZE, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
        )
        title_label.pack()

        # Scrollable area for applications
        canvas = tk.Canvas(main_container, bg="#ecf0f1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            main_container, orient="vertical", command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas, bg="#ecf0f1")

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width()
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind canvas resize to update window width
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas.find_all()[0], width=event.width)

        canvas.bind("<Configure>", _on_canvas_configure)

        # Create application sections
        self.create_application_sections(scrollable_frame)

        # Pack scrollable area
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Bottom buttons
        self.create_bottom_buttons(main_container)

    def create_bottom_buttons(self, parent):
        """Create bottom action buttons."""
        bottom_frame = tk.Frame(parent, bg="#ecf0f1")
        bottom_frame.pack(
            fill=tk.BOTH, expand=True, pady=(UIConfig.BOTTOM_BUTTON_SPACING, 0)
        )

        # Left side buttons (now occupies full width)
        left_frame = tk.Frame(bottom_frame, bg="#ecf0f1")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Exit button (moved to left_frame)
        exit_button = ttk.Button(
            left_frame,
            text="Exit",
            command=self.root.quit,
            style="Danger.TButton",
        )
        exit_button.pack()

    def create_application_sections(self, parent):
        """Create application sections for each category."""
        for category, apps in self.gui_apps.items():
            # Category section
            category_frame = tk.Frame(parent, bg="#ecf0f1")
            category_frame.pack(
                fill=tk.BOTH, expand=True, pady=UIConfig.CATEGORY_SPACING
            )

            # Category header with count
            available_count = sum(
                1 for app in apps if self.app_status.get(app["file"], False)
            )
            total_count = len(apps)

            category_label = tk.Label(
                category_frame,
                text=f"{category} ({available_count}/{total_count})",
                font=("Helvetica", 18, "bold"),
                bg="#ecf0f1",
                fg="#2c3e50",
                anchor="w",
            )
            category_label.pack(fill=tk.X, pady=(0, 12))

            # Applications grid
            apps_frame = tk.Frame(category_frame, bg="#ecf0f1")
            apps_frame.pack(fill=tk.BOTH, expand=True)

            # Create application cards
            for i, app in enumerate(apps):
                self.create_application_card(apps_frame, app, i)

    def create_application_card(self, parent, app, index):
        """Create an individual application card with enhanced styling."""
        # Card frame
        card_frame = tk.Frame(
            parent,
            bg="#ffffff",
            relief=tk.RIDGE,
            bd=2,
            highlightthickness=1,
            highlightbackground="#d0d3d4",
        )
        card_frame.pack(fill=tk.X, pady=8, padx=0)

        # Check availability
        is_available = self.app_status.get(app["file"], False)

        # Card content
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=UIConfig.CARD_CONTENT_PADDING[0],
            pady=UIConfig.CARD_CONTENT_PADDING[1],
        )

        # Left side - Icon and info
        info_frame = tk.Frame(content_frame, bg="#ffffff")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Icon and name
        title_frame = tk.Frame(info_frame, bg="#ffffff")
        title_frame.pack(fill=tk.X, pady=(0, 8))

        # Status indicator
        status_color = "#27ae60" if is_available else "#e74c3c"
        status_text = "✓" if is_available else "✗"
        status_label = tk.Label(
            title_frame,
            text=status_text,
            font=("Helvetica", 16, "bold"),
            bg="#ffffff",
            fg=status_color,
        )
        status_label.pack(side=tk.LEFT, padx=(0, 12))

        # Icon
        icon_label = tk.Label(
            title_frame,
            text=app["icon"],
            font=("Helvetica", UIConfig.FONT_ICON_SIZE),
            bg="#ffffff",
            fg="#2c3e50",
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 12))

        # Name
        name_label = tk.Label(
            title_frame,
            text=app["name"],
            font=("Helvetica", 14, "bold"),
            bg="#ffffff",
            fg="#2c3e50" if is_available else "#95a5a6",
            anchor="w",
        )
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Description
        desc_label = tk.Label(
            info_frame,
            text=app["description"],
            font=("Helvetica", 10),
            bg="#ffffff",
            fg="#7f8c8d" if is_available else "#bdc3c7",
            anchor="w",
            justify=tk.LEFT,
            wraplength=1000,  # Increased for better width utilization
        )
        desc_label.pack(fill=tk.X)

        # File path
        file_label = tk.Label(
            info_frame,
            text=f"File: {app['file']}",
            font=("Courier", 9, "italic"),
            bg="#ffffff",
            fg="#95a5a6" if is_available else "#bdc3c7",
            anchor="w",
        )
        file_label.pack(fill=tk.X, pady=(8, 0))

        # Right side - Launch button
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(side=tk.RIGHT, padx=UIConfig.CARD_BUTTON_PADDING)

        if is_available:
            launch_button = ttk.Button(
                button_frame,
                text="Launch",
                command=app["command"],
                style="Primary.TButton",
            )
            launch_button.pack()
        else:
            disabled_button = ttk.Button(
                button_frame,
                text="Unavailable",
                state=tk.DISABLED,
                style="Secondary.TButton",
            )
            disabled_button.pack()

    # Launch methods for each application
    def launch_full_gui(self):
        """Launch the full-featured GUI."""
        self.launch_python_script("GUI.py", "Full-Featured GUI")

    def launch_apgi_gui_app(self):
        """Launch APGI Framework App."""
        self.launch_python_script("apgi_gui/app.py", "APGI Framework App")

    def launch_experiment_registry(self):
        """Launch Experiment Registry GUI."""
        self.launch_python_script(
            "GUI-Experiment-Registry.py", "Experiment Registry GUI"
        )

    def launch_experiment_runner(self):
        """Launch Experiment Runner."""
        self.launch_python_script("apps/experiment_runner_gui.py", "Experiment Runner")

    def launch_simple_experiment_runner(self):
        """Launch Simple Experiment Runner."""
        self.launch_python_script(
            "utils/gui-simple-experiment-runner.py", "Simple Experiment Runner"
        )

    def launch_parameter_estimation(self):
        """Launch Parameter Estimation GUI."""
        self.launch_python_script(
            "apgi_framework/gui/parameter_estimation_gui.py", "Parameter Estimation GUI"
        )

    def launch_interactive_dashboard(self):
        """Launch Interactive Dashboard."""
        self.launch_python_script(
            "apgi_framework/gui/interactive_dashboard.py", "Interactive Dashboard"
        )

    def launch_monitoring_dashboard(self):
        """Launch Monitoring Dashboard."""
        self.launch_python_script(
            "apgi_framework/gui/monitoring_dashboard.py", "Monitoring Dashboard"
        )

    def launch_web_monitoring_dashboard(self):
        """Launch Web Monitoring Dashboard."""
        self.launch_python_script(
            "apgi_framework/gui/web_monitoring_dashboard.py", "Web Monitoring Dashboard"
        )

    def launch_reporting_visualization(self):
        """Launch Reporting & Visualization."""
        self.launch_python_script(
            "apgi_framework/gui/reporting_visualization.py", "Reporting & Visualization"
        )

    def launch_task_configuration(self):
        """Launch Task Configuration."""
        self.launch_python_script(
            "apgi_framework/gui/task_configuration.py", "Task Configuration"
        )

    def launch_session_management(self):
        """Launch Session Management."""
        self.launch_python_script(
            "apgi_framework/gui/session_management.py", "Session Management"
        )

    def launch_progress_monitoring(self):
        """Launch Progress Monitoring."""
        self.launch_python_script(
            "apgi_framework/gui/progress_monitoring.py", "Progress Monitoring"
        )

    def launch_utils_gui(self):
        """Launch Utils GUI."""
        self.launch_python_script("Utils-GUI.py", "Utils GUI")

    def launch_gui_template(self):
        """Launch GUI Template."""
        self.launch_python_script("apps/gui_template_background.py", "GUI Template")

    def launch_error_handling(self):
        """Launch Error Handling Demo."""
        self.launch_python_script(
            "apgi_framework/gui/error_handling.py", "Error Handling Demo"
        )

    def launch_tests_gui(self):
        """Launch Tests GUI."""
        self.launch_python_script("Tests-GUI.py", "Tests GUI")

    # Additional GUI launch methods
    def launch_coverage_visualization(self):
        """Launch Coverage Visualization."""
        self.launch_python_script(
            "apgi_framework/gui/coverage_visualization.py", "Coverage Visualization"
        )

    def launch_enhanced_monitoring_dashboard(self):
        """Launch Enhanced Monitoring Dashboard."""
        self.launch_python_script(
            "apgi_framework/gui/enhanced_monitoring_dashboard.py",
            "Enhanced Monitoring Dashboard",
        )

    def launch_results_viewer(self):
        """Launch Results Viewer."""
        self.launch_python_script(
            "apgi_framework/gui/results_viewer.py", "Results Viewer"
        )

    def launch_gui_template_main(self):
        """Launch GUI Template (Main)."""
        self.launch_python_script("apps/gui_template.py", "GUI Template (Main)")

    # CLI Tools launch methods
    def launch_test_runner(self):
        """Launch Comprehensive Test Runner."""
        self.launch_python_script("run_tests.py", "Comprehensive Test Runner")

    def launch_experiment_runner_cli(self):
        """Launch Experiment Runner (CLI)."""
        self.launch_python_script("run_experiments.py", "Experiment Runner (CLI)")

    def launch_framework_cli(self):
        """Launch Framework CLI."""
        self.launch_python_script("apgi_framework/cli.py", "Framework CLI")

    def launch_diagnostics_cli(self):
        """Launch Diagnostics CLI."""
        self.launch_python_script(
            "apgi_framework/validation/diagnostics_cli.py", "Diagnostics CLI"
        )

    def launch_deployment_cli(self):
        """Launch Deployment CLI."""
        self.launch_python_script("apgi_framework/deployment/cli.py", "Deployment CLI")

    # Setup & Deployment launch methods
    def launch_setup_script(self):
        """Launch Setup Script."""
        self.launch_python_script("utils/install_dependencies.py", "Setup Script")

    def launch_quick_deploy(self):
        """Launch Quick Deploy."""
        self.launch_python_script(
            "apgi_framework/deployment/deployment_validator.py", "Quick Deploy"
        )

    def launch_delete_cache(self):
        """Launch Delete Cache."""
        self.launch_python_script("delete_pycache.py", "Delete Cache")

    # Examples & Demos launch methods
    def launch_data_loader_example(self):
        """Launch Data Loader Example."""
        self.launch_python_script("examples/data_loader.py", "Data Loader Example")

    def launch_coverage_collector_demo(self):
        """Launch Coverage Collector Demo."""
        self.launch_python_script(
            "examples/coverage_collector_demo.py", "Coverage Collector Demo"
        )

    def launch_primary_falsification_test(self):
        """Launch Primary Falsification Test."""
        self.launch_python_script(
            "examples/01_run_primary_falsification_test.py",
            "Primary Falsification Test",
        )

    def launch_batch_processing_config(self):
        """Launch Batch Processing Config."""
        self.launch_python_script(
            "examples/02_batch_processing_configurations.py", "Batch Processing Config"
        )

    def launch_custom_analysis_results(self):
        """Launch Custom Analysis Results."""
        self.launch_python_script(
            "examples/03_custom_analysis_saved_results.py", "Custom Analysis Results"
        )

    def launch_extending_falsification_criteria(self):
        """Launch Extending Falsification Criteria."""
        self.launch_python_script(
            "examples/04_extending_falsification_criteria.py",
            "Extending Falsification Criteria",
        )

    def launch_python_script(self, script_path, app_name):
        """Launch a Python script in a separate process."""
        try:
            print(f"Launching {app_name} ({script_path})...")

            # Get the absolute path to the script
            current_dir = Path(__file__).parent.absolute()
            script_full_path = current_dir / script_path

            if not script_full_path.exists():
                messagebox.showerror(
                    "File Not Found",
                    f"The script {script_path} was not found.\n"
                    f"Expected path: {script_full_path}",
                )
                return

            # Launch in a separate thread to avoid blocking the GUI
            def run_script():
                try:
                    process = subprocess.Popen(
                        [sys.executable, str(script_full_path)],
                        cwd=current_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    # Verify process actually started before showing success message
                    # Give it a brief moment to start and check if it's still running
                    import time

                    time.sleep(0.1)
                    if process.poll() is None:
                        print(f"Successfully launched {app_name}")
                    else:
                        stdout, stderr = process.communicate()
                        error_msg = stderr if stderr else stdout
                        print(f"Failed to launch {app_name}: {error_msg}")
                except Exception as e:
                    messagebox.showerror(
                        "Launch Error", f"Failed to launch {app_name}: {str(e)}"
                    )

            thread = threading.Thread(target=run_script, daemon=True)
            thread.start()

        except Exception as e:
            messagebox.showerror(
                "System Error", f"System error while launching {app_name}: {str(e)}"
            )

    def show_system_info(self):
        """Show system information dialog."""
        # Check which applications actually exist
        existing_apps = 0
        missing_apps = []

        for category, apps in self.gui_apps.items():
            for app in apps:
                script_path = Path(__file__).parent / app["file"]
                if script_path.exists():
                    existing_apps += 1
                else:
                    missing_apps.append(f"{app['name']} ({app['file']})")

        info_text = f"""
APGI Framework Information
================================

Python Version: {sys.version.split()[0]}
Platform: {sys.platform}
Current Directory: {Path.cwd()}
APGI Root: {Path(__file__).parent}

GUI Applications Status:
• Total Applications: {sum(len(apps) for apps in self.gui_apps.values())}
• Available: {existing_apps}
• Missing: {len(missing_apps)}

Categories:
{chr(10).join(f"• {category}: {len(apps)} apps" for category, apps in self.gui_apps.items())}

System Requirements:
• Python 3.7+ ✓
• tkinter (included with Python) ✓
• CustomTkinter (for some GUIs) - optional
• Flask/Flask-SocketIO (for web dashboard) - optional

Missing Applications:
{chr(10).join(f'• {app}' for app in missing_apps) if missing_apps else 'None - All applications available!'}
        """

        # Create a scrollable text widget for better display
        info_window = tk.Toplevel(self.root)
        info_window.title("System Information")
        info_window.geometry(
            f"{UIConfig.INFO_WINDOW_WIDTH}x{UIConfig.INFO_WINDOW_HEIGHT}"
        )
        info_window.resizable(True, True)

        # Center the info window
        info_window.update_idletasks()
        width = info_window.winfo_width()
        height = info_window.winfo_height()
        x = (info_window.winfo_screenwidth() // 2) - (width // 2)
        y = (info_window.winfo_screenheight() // 2) - (height // 2)
        info_window.geometry(f"{width}x{height}+{x}+{y}")

        # Create text widget with scrollbar
        text_frame = tk.Frame(info_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar_info = ttk.Scrollbar(
            text_frame, orient="vertical", command=text_widget.yview
        )
        text_widget.configure(yscrollcommand=scrollbar_info.set)

        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar_info.pack(side="right", fill="y")

        text_widget.insert("1.0", info_text)
        text_widget.config(state=tk.DISABLED)

        # Close button
        close_button = tk.Button(
            info_window,
            text="Close",
            command=info_window.destroy,
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=UIConfig.BUTTON_PADDING_CLOSE[0],
            pady=UIConfig.BUTTON_PADDING_CLOSE[1],
        )
        close_button.pack(pady=10)

    def run(self):
        """Run the launcher."""
        self.root.mainloop()


def main():
    """Main entry point."""
    launcher = ComprehensiveGUILauncher()
    launcher.run()


if __name__ == "__main__":
    main()
