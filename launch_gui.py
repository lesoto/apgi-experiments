#!/usr/bin/env python3
"""
Comprehensive GUI Launcher for APGI Framework

This script provides a centralized launcher to access all GUI applications and tools
in the APGI Framework, organized by category for easy navigation.
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, font
import importlib.util
import subprocess
import threading
import webbrowser


class ComprehensiveGUILauncher:
    """Comprehensive launcher for all APGI Framework GUI applications."""

    def __init__(self):
        """Initialize the comprehensive launcher."""
        self.root = tk.Tk()
        self.root.title("APGI Framework - Comprehensive GUI Launcher")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)

        # Set window icon and styling
        self.root.configure(bg="#ecf0f1")

        # Center window
        self.center_window()

        # Configure styles
        self.setup_styles()

        # Define GUI applications
        self.gui_apps = self.define_gui_applications()

        # Check application availability
        self.check_app_availability()

        # Create widgets
        self.create_widgets()

    def center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_styles(self):
        """Setup custom styles for better appearance."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure custom styles
        self.style.configure(
            "Title.TLabel",
            font=("Helvetica", 32, "bold"),
            background="#ecf0f1",
            foreground="#2c3e50",
        )

        self.style.configure(
            "Subtitle.TLabel",
            font=("Helvetica", 12),
            background="#ecf0f1",
            foreground="#7f8c8d",
        )

        self.style.configure(
            "Category.TLabel",
            font=("Helvetica", 18, "bold"),
            background="#ecf0f1",
            foreground="#34495e",
        )

        self.style.configure(
            "App.TLabel",
            font=("Helvetica", 13, "bold"),
            background="#ffffff",
            foreground="#2c3e50",
        )

        self.style.configure(
            "Desc.TLabel",
            font=("Helvetica", 10),
            background="#ffffff",
            foreground="#7f8c8d",
        )

        self.style.configure(
            "Path.TLabel",
            font=("Courier", 9, "italic"),
            background="#ffffff",
            foreground="#95a5a6",
        )

        self.style.configure(
            "Launch.TButton", font=("Helvetica", 11, "bold"), padding=(20, 10)
        )

        self.style.configure(
            "Status.TLabel", font=("Helvetica", 9, "bold"), background="#ffffff"
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
                    "icon": "🎯",
                    "command": self.launch_full_gui,
                },
                {
                    "name": "Simple GUI",
                    "file": "GUI-Simple.py",
                    "description": "Streamlined interface for essential functions",
                    "icon": "⚡",
                    "command": self.launch_simple_gui,
                },
                {
                    "name": "APGI Framework App",
                    "file": "apgi_gui/app.py",
                    "description": "Modern CustomTkinter-based framework application",
                    "icon": "🚀",
                    "command": self.launch_apgi_gui_app,
                },
            ],
            "Experiment Management": [
                {
                    "name": "Experiment Runner",
                    "file": "apps/experiment_runner_gui.py",
                    "description": "Run and manage experiments with comprehensive controls and monitoring",
                    "icon": "▶️",
                    "command": self.launch_experiment_runner,
                },
                {
                    "name": "Falsification GUI",
                    "file": "apps/apgi_falsification_gui.py",
                    "description": "Falsification testing interface for consciousness evaluation experiments",
                    "icon": "🔬",
                    "command": self.launch_falsification_gui,
                },
                {
                    "name": "Falsification GUI (Refactored)",
                    "file": "apps/apgi_falsification_gui_refactored.py",
                    "description": "Refactored falsification testing interface with improved architecture",
                    "icon": "🧪",
                    "command": self.launch_falsification_gui_refactored,
                },
            ],
            "Analysis & Visualization": [
                {
                    "name": "Parameter Estimation GUI",
                    "file": "apgi_framework/gui/parameter_estimation_gui.py",
                    "description": "Parameter estimation and analysis tools",
                    "icon": "📊",
                    "command": self.launch_parameter_estimation,
                },
                {
                    "name": "Interactive Dashboard",
                    "file": "apgi_framework/gui/interactive_dashboard.py",
                    "description": "Web-based interactive dashboard (requires Flask)",
                    "icon": "🌐",
                    "command": self.launch_interactive_dashboard,
                },
                {
                    "name": "Monitoring Dashboard",
                    "file": "apgi_framework/gui/monitoring_dashboard.py",
                    "description": "Real-time monitoring dashboard",
                    "icon": "📈",
                    "command": self.launch_monitoring_dashboard,
                },
                {
                    "name": "Reporting & Visualization",
                    "file": "apgi_framework/gui/reporting_visualization.py",
                    "description": "Generate reports and visualizations",
                    "icon": "📑",
                    "command": self.launch_reporting_visualization,
                },
            ],
            "Configuration & Tools": [
                {
                    "name": "Task Configuration",
                    "file": "apgi_framework/gui/task_configuration.py",
                    "description": "Configure experimental tasks",
                    "icon": "⚙️",
                    "command": self.launch_task_configuration,
                },
                {
                    "name": "Session Management",
                    "file": "apgi_framework/gui/session_management.py",
                    "description": "Manage experimental sessions",
                    "icon": "🗂️",
                    "command": self.launch_session_management,
                },
                {
                    "name": "Progress Monitoring",
                    "file": "apgi_framework/gui/progress_monitoring.py",
                    "description": "Monitor experiment progress",
                    "icon": "📊",
                    "command": self.launch_progress_monitoring,
                },
            ],
            "Development & Testing": [
                {
                    "name": "GUI Template",
                    "file": "apps/gui_template.py",
                    "description": "Template for GUI development",
                    "icon": "🛠️",
                    "command": self.launch_gui_template,
                },
                {
                    "name": "Error Handling Demo",
                    "file": "apgi_framework/gui/error_handling.py",
                    "description": "Error handling demonstration",
                    "icon": "⚠️",
                    "command": self.launch_error_handling,
                },
            ],
        }

    def create_widgets(self):
        """Create launcher widgets with organized layout."""
        # Main container
        main_container = tk.Frame(self.root, bg="#ecf0f1")
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Header section
        header_frame = tk.Frame(main_container, bg="#ecf0f1")
        header_frame.pack(fill=tk.X, pady=(0, 25))

        # Title and subtitle
        title_label = tk.Label(
            header_frame,
            text="🧠 APGI Framework Launcher",
            font=("Helvetica", 36, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame,
            text="Comprehensive GUI Application Launcher • v1.0",
            font=("Helvetica", 13),
            bg="#ecf0f1",
            fg="#7f8c8d",
        )
        subtitle_label.pack(pady=(8, 0))

        # Status bar
        self.create_status_bar(header_frame)

        # Scrollable area for applications
        canvas = tk.Canvas(main_container, bg="#ecf0f1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            main_container, orient="vertical", command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas, bg="#ecf0f1")

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

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

    def create_status_bar(self, parent):
        """Create status bar showing application availability."""
        status_frame = tk.Frame(parent, bg="#ecf0f1")
        status_frame.pack(fill=tk.X, pady=(15, 0))

        total_apps = sum(len(apps) for apps in self.gui_apps.values())
        available_apps = sum(1 for status in self.app_status.values() if status)
        missing_apps = total_apps - available_apps

        status_text = f"📦 Applications: {available_apps}/{total_apps} available"
        if missing_apps > 0:
            status_text += f" • ⚠️ {missing_apps} missing"

        status_label = tk.Label(
            status_frame,
            text=status_text,
            font=("Helvetica", 11, "bold"),
            bg="#ecf0f1",
            fg="#27ae60" if missing_apps == 0 else "#e67e22",
        )
        status_label.pack()

    def create_bottom_buttons(self, parent):
        """Create bottom action buttons."""
        bottom_frame = tk.Frame(parent, bg="#ecf0f1")
        bottom_frame.pack(fill=tk.X, pady=(25, 0))

        # Left side buttons
        left_frame = tk.Frame(bottom_frame, bg="#ecf0f1")
        left_frame.pack(side=tk.LEFT)

        # System Info button
        info_button = tk.Button(
            left_frame,
            text="ℹ️ System Info",
            command=self.show_system_info,
            font=("Helvetica", 11, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground="#2980b9",
        )
        info_button.pack(side=tk.LEFT, padx=(0, 10))

        # Refresh button
        refresh_button = tk.Button(
            left_frame,
            text="🔄 Refresh",
            command=self.refresh_status,
            font=("Helvetica", 11, "bold"),
            bg="#95a5a6",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground="#7f8c8d",
        )
        refresh_button.pack(side=tk.LEFT)

        # Right side buttons
        right_frame = tk.Frame(bottom_frame, bg="#ecf0f1")
        right_frame.pack(side=tk.RIGHT)

        # Exit button
        exit_button = tk.Button(
            right_frame,
            text="❌ Exit",
            command=self.root.quit,
            font=("Helvetica", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground="#c0392b",
        )
        exit_button.pack()

    def create_application_sections(self, parent):
        """Create application sections for each category."""
        for category, apps in self.gui_apps.items():
            # Category section
            category_frame = tk.Frame(parent, bg="#ecf0f1")
            category_frame.pack(fill=tk.X, pady=(20, 15))

            # Category header with count
            available_count = sum(
                1 for app in apps if self.app_status.get(app["file"], False)
            )
            total_count = len(apps)

            category_label = tk.Label(
                category_frame,
                text=f"📁 {category} ({available_count}/{total_count})",
                font=("Helvetica", 18, "bold"),
                bg="#ecf0f1",
                fg="#2c3e50",
                anchor="w",
            )
            category_label.pack(fill=tk.X, pady=(0, 12))

            # Applications grid
            apps_frame = tk.Frame(category_frame, bg="#ecf0f1")
            apps_frame.pack(fill=tk.X)

            # Create application cards
            for i, app in enumerate(apps):
                self.create_application_card(apps_frame, app, i)

    def create_application_card(self, parent, app, index):
        """Create an individual application card with enhanced styling."""
        # Card frame
        card_frame = tk.Frame(parent, bg="#ffffff", relief=tk.RAISED, bd=2)
        card_frame.pack(fill=tk.X, pady=8, padx=15)

        # Check availability
        is_available = self.app_status.get(app["file"], False)

        # Card content
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill=tk.X, padx=20, pady=15)

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
            font=("Helvetica", 20),
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
            wraplength=800,
        )
        desc_label.pack(fill=tk.X)

        # File path
        file_label = tk.Label(
            info_frame,
            text=f"📄 {app['file']}",
            font=("Courier", 9, "italic"),
            bg="#ffffff",
            fg="#95a5a6" if is_available else "#bdc3c7",
            anchor="w",
        )
        file_label.pack(fill=tk.X, pady=(8, 0))

        # Right side - Launch button
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(side=tk.RIGHT, padx=(20, 0))

        if is_available:
            launch_button = tk.Button(
                button_frame,
                text="🚀 Launch",
                command=app["command"],
                font=("Helvetica", 11, "bold"),
                bg="#27ae60",
                fg="white",
                relief=tk.FLAT,
                padx=25,
                pady=12,
                cursor="hand2",
                activebackground="#2ecc71",
                activeforeground="white",
            )
            launch_button.pack()

            # Add hover effects
            def on_enter(e):
                launch_button.config(bg="#2ecc71")

            def on_leave(e):
                launch_button.config(bg="#27ae60")

            launch_button.bind("<Enter>", on_enter)
            launch_button.bind("<Leave>", on_leave)
        else:
            disabled_button = tk.Button(
                button_frame,
                text="❌ Unavailable",
                state=tk.DISABLED,
                font=("Helvetica", 11, "bold"),
                bg="#bdc3c7",
                fg="white",
                relief=tk.FLAT,
                padx=25,
                pady=12,
            )
            disabled_button.pack()

    # Launch methods for each application
    def launch_full_gui(self):
        """Launch the full-featured GUI."""
        self.launch_python_script("GUI.py", "Full-Featured GUI")

    def launch_simple_gui(self):
        """Launch simple GUI."""
        self.launch_python_script("GUI-Simple.py", "Simple GUI")

    def launch_apgi_gui_app(self):
        """Launch APGI Framework App."""
        self.launch_python_script("apgi_gui/app.py", "APGI Framework App")

    def launch_experiment_runner(self):
        """Launch Experiment Runner."""
        self.launch_python_script("apps/experiment_runner_gui.py", "Experiment Runner")

    def launch_falsification_gui(self):
        """Launch Falsification GUI."""
        self.launch_python_script("apps/apgi_falsification_gui.py", "Falsification GUI")

    def launch_falsification_gui_refactored(self):
        """Launch Falsification GUI (Refactored)."""
        self.launch_python_script(
            "apps/apgi_falsification_gui_refactored.py",
            "Falsification GUI (Refactored)",
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

    def launch_gui_template(self):
        """Launch GUI Template."""
        self.launch_python_script("apps/gui_template.py", "GUI Template")

    def launch_error_handling(self):
        """Launch Error Handling Demo."""
        self.launch_python_script(
            "apgi_framework/gui/error_handling.py", "Error Handling Demo"
        )

    def launch_python_script(self, script_path, app_name):
        """Launch a Python script in a separate process."""
        try:
            print(f"Launching {app_name} ({script_path})...")

            # Get the absolute path to the script
            current_dir = Path(__file__).parent.absolute()
            script_full_path = current_dir / script_path

            if not script_full_path.exists():
                messagebox.showwarning(
                    "File Not Found",
                    f"Script not found:\n{script_full_path}\n\n"
                    f"This application may not be implemented yet.",
                )
                return

            # Launch in a separate thread to avoid blocking the GUI
            def run_script():
                try:
                    subprocess.run(
                        [sys.executable, str(script_full_path)],
                        cwd=current_dir,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                except subprocess.CalledProcessError as e:
                    # Show error in main thread - capture error message for lambda
                    error_msg = f"Failed to launch {app_name}:\n{e.stderr or str(e)}"
                    self.root.after(
                        0,
                        lambda msg=error_msg: messagebox.showerror("Launch Error", msg),
                    )
                except Exception as e:
                    # Show error in main thread - capture error message for lambda
                    error_msg = f"Unexpected error launching {app_name}: {str(e)}"
                    self.root.after(
                        0,
                        lambda msg=error_msg: messagebox.showerror(
                            "Unexpected Error", msg
                        ),
                    )

            thread = threading.Thread(target=run_script, daemon=True)
            thread.start()

            # Show success message briefly
            self.root.after(
                100,
                lambda: messagebox.showinfo(
                    "Launch Started",
                    f"{app_name} is starting...\n"
                    f"If the application doesn't appear, check for any error messages.",
                ),
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {app_name}: {e}")

    def refresh_status(self):
        """Refresh application availability status."""
        self.check_app_availability()
        messagebox.showinfo(
            "Refreshed",
            "Application status has been refreshed.",
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
APGI Framework System Information
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
        info_window.geometry("600x500")
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
            padx=20,
            pady=8,
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
