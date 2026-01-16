#!/usr/bin/env python3
"""
TEMPLATE.py - Simplified APGI Framework GUI Template

This is a streamlined version of the GUI.py that provides
a basic interface for the APGI Framework experiments.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from pathlib import Path
import logging
import json
import subprocess
import threading
import importlib

# Add project root to path for tooltip import
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import customtkinter for theme support (optional)
ctk = None
CUSTOMTKINTER_AVAILABLE = False
try:
    import customtkinter as ctk

    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None

# Import tooltip manager
try:
    from apgi_gui.utils.tooltip_manager import add_tooltip, add_parameter_tooltips

    TOOLTIPS_AVAILABLE = True
except ImportError:
    # Fallback tooltip implementation
    TOOLTIPS_AVAILABLE = False

    def add_tooltip(widget, param_name):
        pass

    def add_parameter_tooltips(widgets):
        pass


# Import keyboard manager
try:
    from apgi_gui.utils.keyboard_manager import (
        KeyboardManager,
        setup_standard_shortcuts,
    )

    KEYBOARD_SHORTCUTS_AVAILABLE = True
except ImportError:
    # Fallback keyboard implementation
    KEYBOARD_SHORTCUTS_AVAILABLE = False

    class KeyboardManager:
        def __init__(self, root):
            pass

        def bind_shortcut(self, *args, **kwargs):
            pass

    def setup_standard_shortcuts(*args, **kwargs):
        pass


# Import undo/redo manager
try:
    from apgi_gui.utils.undo_redo_manager import (
        UndoRedoManager,
        WidgetTracker,
        create_undo_redo_menu,
    )

    UNDO_REDO_AVAILABLE = True
except ImportError:
    # Fallback undo/redo implementation
    UNDO_REDO_AVAILABLE = False

    class UndoRedoManager:
        def __init__(self, *args, **kwargs):
            pass

        def undo(self):
            pass

        def redo(self):
            pass

        def can_undo(self):
            return False

        def can_redo(self):
            return False

    class WidgetTracker:
        def __init__(self, *args, **kwargs):
            pass

        def track_widget(self, *args, **kwargs):
            pass

    def create_undo_redo_menu(*args, **kwargs):
        pass


# Import theme manager
try:
    from apgi_gui.utils.theme_manager import ThemeManager, get_system_theme_preference

    THEME_AVAILABLE = True
except ImportError:
    # Fallback theme implementation
    THEME_AVAILABLE = False

    class ThemeManager:
        def __init__(self, *args, **kwargs):
            pass

        def set_theme(self, *args, **kwargs):
            pass

        def toggle_dark_mode(self):
            pass

    def get_system_theme_preference():
        return "light"


# Import Excel export manager
try:
    from apgi_gui.utils.excel_export_manager import (
        get_excel_export_manager,
        create_excel_export_dialog,
    )

    EXCEL_EXPORT_AVAILABLE = True
except ImportError:
    # Fallback Excel export implementation
    EXCEL_EXPORT_AVAILABLE = False

    def get_excel_export_manager():
        return None

    def create_excel_export_dialog(*args, **kwargs):
        pass


# Set matplotlib backend before importing to avoid threading issues
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend to prevent GUI conflicts

# Set up logging with standardized system
try:
    from apgi_framework.logging.standardized_logging import get_logger

    logger = get_logger("gui_simple")
except ImportError:
    # Fallback to basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("gui_simple")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import experiment runner
try:
    from tools.run_experiments import get_available_experiments, run_experiment

    EXPERIMENTS_AVAILABLE = True
except ImportError:
    EXPERIMENTS_AVAILABLE = False
    logger.warning("Experiment runner not available, using simulation mode")


class TemplateGUI:
    """Simplified APGI Framework GUI Template."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("APGI Framework - Template GUI")
        self.root.geometry("800x600")

        # Thread management
        self.experiment_threads = []
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Initialize keyboard shortcuts
        if KEYBOARD_SHORTCUTS_AVAILABLE:
            self.keyboard_manager = KeyboardManager(self.root)
            setup_standard_shortcuts(self, self.keyboard_manager)
        else:
            self.keyboard_manager = None

        # Initialize undo/redo functionality
        if UNDO_REDO_AVAILABLE:
            self.undo_manager = UndoRedoManager(max_history=50)
            self.widget_tracker = WidgetTracker(self.undo_manager)
        else:
            self.undo_manager = None
            self.widget_tracker = None

        # Initialize theme manager
        if THEME_AVAILABLE and CUSTOMTKINTER_AVAILABLE:
            self.theme_manager = ThemeManager(self.root)
            # Try to load system preference
            system_theme = get_system_theme_preference()
            self.theme_manager.set_theme(system_theme)
        else:
            self.theme_manager = None

        # Initialize Excel export manager
        if EXCEL_EXPORT_AVAILABLE:
            self.excel_export_manager = get_excel_export_manager()
        else:
            self.excel_export_manager = None

        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

        self.create_widgets()

    def create_widgets(self):
        """Create the main GUI widgets."""
        # Title
        title_label = ttk.Label(
            self.main_frame,
            text="APGI Framework Template Interface",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Left panel - Controls
        self.create_control_panel()

        # Right panel - Display
        self.create_display_panel()

        # Bottom panel - Status
        self.create_status_panel()

    def create_control_panel(self):
        """Create the left control panel."""
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="10")
        control_frame.grid(
            row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10)
        )

        # Experiment selection
        experiment_label = ttk.Label(control_frame, text="Select Experiment:")
        experiment_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        add_tooltip(experiment_label, "interoceptive_gating")

        self.experiment_var = tk.StringVar(value="interoceptive_gating")

        # Get available experiments
        if EXPERIMENTS_AVAILABLE:
            try:
                available_experiments = get_available_experiments()
                experiments = list(available_experiments.keys())
                if not experiments:
                    experiments = [
                        "interoceptive_gating",
                        "somatic_marker_priming",
                        "metabolic_cost",
                    ]
            except Exception as e:
                logger.warning(f"Could not load experiments: {e}")
                experiments = [
                    "interoceptive_gating",
                    "somatic_marker_priming",
                    "metabolic_cost",
                ]
        else:
            experiments = [
                "interoceptive_gating",
                "somatic_marker_priming",
                "metabolic_cost",
            ]

        experiment_combo = ttk.Combobox(
            control_frame,
            textvariable=self.experiment_var,
            values=experiments,
            state="readonly",
        )
        experiment_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        add_tooltip(experiment_combo, "interoceptive_gating")

        # Parameters
        ttk.Label(control_frame, text="Parameters:").grid(
            row=2, column=0, sticky=tk.W, pady=(20, 5)
        )

        param_frame = ttk.Frame(control_frame)
        param_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)

        # Participants parameter
        participants_label = ttk.Label(param_frame, text="Participants:")
        participants_label.grid(row=0, column=0, sticky=tk.W)
        add_tooltip(participants_label, "n_participants")

        self.threshold_var = tk.DoubleVar(value=10.0)
        participants_spinbox = ttk.Spinbox(
            param_frame, from_=1, to=50, textvariable=self.threshold_var, width=10
        )
        participants_spinbox.grid(row=0, column=1, padx=5)
        add_tooltip(participants_spinbox, "n_participants")

        # Track for undo/redo
        if self.widget_tracker:
            self.widget_tracker.track_widget(participants_spinbox, "parameter")
            self.widget_tracker.tracked_widgets[str(id(participants_spinbox))][
                "param_name"
            ] = "n_participants"

        # Trials parameter
        trials_label = ttk.Label(param_frame, text="Trials/Condition:")
        trials_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        add_tooltip(trials_label, "n_trials_per_condition")

        self.simulations_var = tk.IntVar(value=50)
        simulations_spinbox = ttk.Spinbox(
            param_frame, from_=10, to=200, textvariable=self.simulations_var, width=10
        )
        simulations_spinbox.grid(row=1, column=1, padx=5)
        add_tooltip(simulations_spinbox, "n_trials_per_condition")

        # Track for undo/redo
        if self.widget_tracker:
            self.widget_tracker.track_widget(simulations_spinbox, "parameter")
            self.widget_tracker.tracked_widgets[str(id(simulations_spinbox))][
                "param_name"
            ] = "n_trials_per_condition"

        # Action buttons
        ttk.Label(control_frame, text="Actions:").grid(
            row=4, column=0, sticky=tk.W, pady=(20, 5)
        )

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)

        self.run_button = ttk.Button(
            button_frame, text="Run Experiment", command=self.run_experiment
        )
        self.run_button.grid(row=0, column=0, padx=2, pady=2)

        self.clear_button = ttk.Button(
            button_frame, text="Clear Results", command=self.clear_results
        )
        self.clear_button.grid(row=0, column=1, padx=2, pady=2)

        self.export_button = ttk.Button(
            button_frame, text="Export Data", command=self.export_data
        )
        self.export_button.grid(row=1, column=0, padx=2, pady=2)

        self.load_button = ttk.Button(
            button_frame, text="Load Config", command=self.load_config
        )
        self.load_button.grid(row=1, column=1, padx=2, pady=2)

        # Excel export button
        if self.excel_export_manager:
            self.excel_export_button = ttk.Button(
                button_frame, text="Export to Excel", command=self.export_to_excel
            )
            self.excel_export_button.grid(row=2, column=0, columnspan=2, padx=2, pady=2)

        # Theme selection
        if self.theme_manager and CUSTOMTKINTER_AVAILABLE:
            theme_label = ttk.Label(control_frame, text="Theme:")
            theme_label.grid(row=6, column=0, sticky=tk.W, pady=(20, 5))

            theme_selector = self.theme_manager.create_theme_selector(control_frame)
            theme_selector.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=5)

    def create_display_panel(self):
        """Create the right display panel."""
        display_frame = ttk.LabelFrame(
            self.main_frame, text="Results Display", padding="10"
        )
        display_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create text widget for results
        self.results_text = tk.Text(display_frame, wrap=tk.WORD, width=50, height=20)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            display_frame, orient=tk.VERTICAL, command=self.results_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)

        # Configure grid weights
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)

        # Initial message
        self.results_text.insert(tk.END, "Welcome to APGI Framework Template GUI\n\n")
        self.results_text.insert(
            tk.END, "Select an experiment and click 'Run Experiment' to begin.\n"
        )
        self.results_text.insert(tk.END, "Results will appear here.\n")

    def create_status_panel(self):
        """Create the bottom status panel."""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        # Status label
        self.status_label = ttk.Label(
            status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))

        # Configure grid weights
        status_frame.columnconfigure(0, weight=3)
        status_frame.columnconfigure(1, weight=1)

    def run_experiment(self):
        """Run the selected experiment."""
        experiment = self.experiment_var.get()
        threshold = self.threshold_var.get()
        simulations = self.simulations_var.get()

        self.status_label.config(text=f"Running {experiment}...")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Running Experiment: {experiment}\n")
        self.results_text.insert(tk.END, f"Parameters:\n")
        self.results_text.insert(tk.END, f"  - Participants: {int(threshold)}\n")
        self.results_text.insert(tk.END, f"  - Trials per condition: {simulations}\n\n")

        # Run experiment in separate thread to avoid GUI freezing
        thread = threading.Thread(
            target=self._run_experiment_thread,
            args=(experiment, threshold, simulations),
        )
        self.experiment_threads.append(thread)
        thread.start()

        # Start progress simulation
        self.root.after(100, self.simulate_experiment_progress, 0)

    def _run_experiment_thread(self, experiment, threshold, simulations):
        """Run experiment in background thread with isolation to prevent crashes."""
        try:
            if EXPERIMENTS_AVAILABLE:
                # Use subprocess isolation to prevent GUI crashes
                experiment_params = {
                    "n_participants": int(threshold),
                    "n_trials_per_condition": simulations,
                }

                # Create a simple Python script to run the experiment
                script_content = f"""
import sys
from pathlib import Path

# Add the actual project root to Python path
project_root = Path("{project_root}")
sys.path.insert(0, str(project_root))

try:
    from tools.run_experiments import run_experiment
    result = run_experiment("{experiment}", n_participants={int(threshold)}, n_trials_per_condition={simulations})
    print("SUCCESS: Experiment completed")
    print(f"RESULT: {{result}}")
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
"""

                # Write script to temporary file
                import tempfile

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as f:
                    f.write(script_content)
                    script_path = f.name

                try:
                    # Run experiment in subprocess to isolate from GUI
                    result = subprocess.run(
                        [sys.executable, script_path],
                        capture_output=True,
                        text=True,
                        timeout=60,  # 60 second timeout
                    )

                    output = result.stdout
                    error = result.stderr

                    if result.returncode == 0 and "SUCCESS:" in output:
                        # Extract result from output
                        lines = output.split("\n")
                        result_line = next(
                            (line for line in lines if line.startswith("RESULT:")), ""
                        )
                        if result_line:
                            result_value = result_line.replace("RESULT: ", "")
                        else:
                            result_value = "Experiment completed successfully"

                        # Check if window still exists before updating GUI
                        if self.root.winfo_exists():
                            self.root.after(
                                0,
                                self._update_experiment_results,
                                output,
                                result_value,
                                None,
                            )
                    else:
                        error_msg = error or output or "Unknown error occurred"
                        # Check if window still exists before updating GUI
                        if self.root.winfo_exists():
                            self.root.after(
                                0,
                                self._update_experiment_results,
                                None,
                                None,
                                error_msg,
                            )

                except subprocess.TimeoutExpired:
                    error_msg = "Experiment timed out after 60 seconds"
                    # Check if window still exists before updating GUI
                    if self.root.winfo_exists():
                        self.root.after(
                            0, self._update_experiment_results, None, None, error_msg
                        )
                except Exception as e:
                    error_msg = f"Failed to run experiment subprocess: {e}"
                    # Check if window still exists before updating GUI
                    if self.root.winfo_exists():
                        self.root.after(
                            0, self._update_experiment_results, None, None, error_msg
                        )
                finally:
                    # Clean up temporary script
                    try:
                        os.unlink(script_path)
                    except Exception as e:
                        # Ignore cleanup errors - temp file will be cleaned by OS
                        pass

            else:
                # Simulation mode
                # Check if window still exists before updating GUI
                if self.root.winfo_exists():
                    self.root.after(
                        2000,
                        self._update_experiment_results,
                        "Simulation mode - experiment runner not available",
                        None,
                        None,
                    )

        except Exception as e:
            logger.error(f"Error running experiment {experiment}: {e}")
            # Check if window still exists before updating GUI
            if self.root.winfo_exists():
                self.root.after(0, self._update_experiment_results, None, None, str(e))

    def _update_experiment_results(self, output, result, error):
        """Update GUI with experiment results."""
        if error:
            self.results_text.insert(tk.END, f"ERROR: {error}\n")
            messagebox.showerror(
                "Experiment Error", f"Failed to run experiment: {error}"
            )
        else:
            if output:
                self.results_text.insert(tk.END, f"Output:\n{output}\n")
            if result:
                self.results_text.insert(tk.END, f"Result: {result}\n")

            # Add summary
            self.results_text.insert(tk.END, "\n" + "=" * 50 + "\n")
            self.results_text.insert(tk.END, "EXPERIMENT COMPLETED\n")
            self.results_text.insert(tk.END, "=" * 50 + "\n\n")

        self.results_text.see(tk.END)
        self.complete_experiment()

    def simulate_experiment_progress(self, progress):
        """Simulate experiment progress."""
        if progress <= 100:
            self.progress_var.set(progress)
            self.status_label.config(text=f"Running experiment... {progress}%")

            if progress % 20 == 0:
                self.results_text.insert(
                    tk.END, f"Progress: {progress}% - Processing data...\n"
                )
                self.results_text.see(tk.END)
                self.root.update_idletasks()

            # Continue progress
            self.root.after(
                200, lambda: self.simulate_experiment_progress(progress + 10)
            )
        else:
            self.complete_experiment()

    def complete_experiment(self):
        """Complete the experiment simulation."""
        self.progress_var.set(0)
        self.status_label.config(text="Experiment completed")

        # Show completion message if not already shown by _update_experiment_results
        if "EXPERIMENT COMPLETED" not in self.results_text.get(1.0, tk.END):
            experiment = self.experiment_var.get()
            threshold = self.threshold_var.get()
            simulations = self.simulations_var.get()

            # Show results
            self.results_text.insert(tk.END, "\n" + "=" * 50 + "\n")
            self.results_text.insert(tk.END, "EXPERIMENT RESULTS\n")
            self.results_text.insert(tk.END, "=" * 50 + "\n\n")

            # Simulate some results based on experiment type
            if "interoceptive" in experiment:
                self.results_text.insert(tk.END, f"Interoceptive Gating Results:\n")
                self.results_text.insert(
                    tk.END, f"  - Gating threshold: {threshold:.2f}\n"
                )
                self.results_text.insert(
                    tk.END, f"  - Success rate: {75 + (threshold/20)*100:.1f}%\n"
                )
                self.results_text.insert(
                    tk.END, f"  - Processing time: {2.5 + (simulations/50):.2f}s\n"
                )
            elif "somatic" in experiment:
                self.results_text.insert(tk.END, f"Somatic Marker Results:\n")
                self.results_text.insert(
                    tk.END, f"  - Marker influence: {0.3 + (threshold/15):.3f}\n"
                )
                self.results_text.insert(
                    tk.END, f"  - Modulation effect: {0.6 + (simulations/200):.3f}\n"
                )
                self.results_text.insert(
                    tk.END, f"  - Response latency: {80 + threshold:.0f} ms\n"
                )
            elif "metabolic" in experiment:
                self.results_text.insert(tk.END, f"Metabolic Cost Results:\n")
                self.results_text.insert(
                    tk.END, f"  - Energy consumption: {threshold * 10:.1f} units\n"
                )
                self.results_text.insert(
                    tk.END, f"  - Efficiency score: {85 + (simulations/10):.1f}%\n"
                )
                self.results_text.insert(
                    tk.END, f"  - Cost-benefit ratio: {1.2 - (threshold/50):.2f}\n"
                )
            else:
                self.results_text.insert(tk.END, f"General Experiment Results:\n")
                self.results_text.insert(
                    tk.END, f"  - Data points processed: {simulations * 100}\n"
                )
                self.results_text.insert(
                    tk.END, f"  - Success rate: {85 + (threshold/2):.1f}%\n"
                )
                self.results_text.insert(
                    tk.END, f"  - Processing time: {2.5 + (simulations/50):.2f}s\n"
                )

            self.results_text.insert(tk.END, f"\nExperiment completed successfully!\n")
            self.results_text.see(tk.END)

            messagebox.showinfo(
                "Experiment Complete", f"{experiment} completed successfully!"
            )

    def clear_results(self):
        """Clear the results display."""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Results cleared.\n")
        self.status_label.config(text="Results cleared")
        self.progress_var.set(0)

    def export_data(self):
        """Export experiment data."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if filename:
            try:
                with open(filename, "w") as f:
                    f.write(self.results_text.get(1.0, tk.END))
                self.status_label.config(text=f"Data exported to {Path(filename).name}")
                messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def load_config(self):
        """Load configuration from file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                # Load actual JSON configuration
                with open(filename, "r") as f:
                    config = json.load(f)

                # Update GUI with loaded values
                if "n_participants" in config or "participants" in config:
                    participants = config.get(
                        "n_participants", config.get("participants", 10)
                    )
                    self.threshold_var.set(float(participants))
                if "n_trials_per_condition" in config or "trials" in config:
                    trials = config.get(
                        "n_trials_per_condition", config.get("trials", 50)
                    )
                    self.simulations_var.set(int(trials))
                if "experiment" in config:
                    self.experiment_var.set(str(config["experiment"]))

                self.status_label.config(
                    text=f"Configuration loaded from {Path(filename).name}"
                )
                messagebox.showinfo(
                    "Config Loaded",
                    f"Configuration loaded from {filename}\n\nLoaded values:\n{json.dumps(config, indent=2)}",
                )

                logger.info(f"Configuration loaded from {filename}: {config}")

            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON format: {e}"
                logger.error(error_msg)
                messagebox.showerror("Load Error", error_msg)
            except Exception as e:
                error_msg = f"Failed to load configuration: {e}"
                logger.error(error_msg)
                messagebox.showerror("Load Error", error_msg)

    def on_closing(self):
        """Handle window closing with proper thread cleanup."""
        # Wait for all experiment threads to complete
        for thread in self.experiment_threads:
            if thread.is_alive():
                thread.join(timeout=5.0)
        self.root.destroy()

    def undo(self):
        """Perform undo operation."""
        if self.undo_manager and self.undo_manager.can_undo():
            description = self.undo_manager.undo()
            if description:
                self.status_label.config(text=f"Undone: {description}")

    def redo(self):
        """Perform redo operation."""
        if self.undo_manager and self.undo_manager.can_redo():
            description = self.undo_manager.redo()
            if description:
                self.status_label.config(text=f"Redone: {description}")

    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        if self.theme_manager and CUSTOMTKINTER_AVAILABLE:
            new_theme = self.theme_manager.toggle_dark_mode()
            self.status_label.config(text=f"Theme changed to: {new_theme.title()}")

    def export_to_excel(self):
        """Export results to Excel format."""
        if not self.excel_export_manager:
            messagebox.showerror(
                "Error", "Excel export not available. Please install openpyxl."
            )
            return

        # Get current results text
        results_text = self.results_text.get(1.0, tk.END)

        if not results_text.strip() or results_text.strip() == "Results cleared.\n":
            messagebox.showwarning("Warning", "No results to export.")
            return

        # Parse results into structured data
        data = self._parse_results_for_excel(results_text)

        # Create export dialog
        def perform_export(filepath, options):
            try:
                success = self.excel_export_manager.export_to_excel(
                    data,
                    filepath,
                    sheet_name="Experiment Results",
                    include_charts=options.get("include_charts", False),
                    styling=options.get("styling", True),
                )
                return success
            except Exception as e:
                print(f"Export error: {e}")
                return False

        create_excel_export_dialog(self.root, perform_export)

    def _parse_results_for_excel(self, results_text: str) -> List[Dict[str, Any]]:
        """Parse results text into structured data for Excel export."""
        data = []
        lines = results_text.split("\n")

        # Extract experiment info
        experiment_info = {}
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for key-value pairs
            if ":" in line and not line.startswith(" "):
                if "Experiment:" in line:
                    experiment_info["Experiment"] = line.split(":", 1)[1].strip()
                elif "Participants:" in line:
                    experiment_info["Participants"] = int(line.split(":", 1)[1].strip())
                elif "Trials/Condition:" in line:
                    experiment_info["Trials per Condition"] = int(
                        line.split(":", 1)[1].strip()
                    )
                elif "Success rate:" in line:
                    experiment_info["Success Rate"] = line.split(":", 1)[1].strip()
                elif "Processing time:" in line:
                    experiment_info["Processing Time"] = line.split(":", 1)[1].strip()

        if experiment_info:
            data.append(experiment_info)

        return data

    def run(self):
        """Start the GUI application."""
        logger.info("Starting Template GUI application...")
        self.root.mainloop()


def main():
    """Main entry point."""
    try:
        app = TemplateGUI()
        app.run()
    except Exception as e:
        logger.error(f"Error starting Template GUI: {e}")
        messagebox.showerror("Error", f"Failed to start GUI: {e}")


if __name__ == "__main__":
    main()
