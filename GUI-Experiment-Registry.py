#!/usr/bin/env python3
"""
APGI Experiment Registry GUI

A simple GUI to display and run all 24 experiments from the experiment registry.
Provides an easy interface to view experiment details and execute experiments.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import sys
import os
from pathlib import Path
import time
from typing import Dict, Any
import logging
import subprocess
import tempfile

# Set matplotlib backend before importing to avoid threading issues
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend to prevent GUI conflicts

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import experiment runner
from tools.run_experiments import EXPERIMENTS, run_experiment

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


# Set up logging with standardized system
try:
    from apgi_framework.logging.standardized_logging import get_logger

    logger = get_logger("gui_experiment_registry")
except ImportError:
    # Fallback to basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("gui_experiment_registry")


class ExperimentRegistryGUI:
    """GUI for the APGI Experiment Registry."""

    def __init__(self, root):
        self.root = root
        self.root.title("APGI Experiment Registry")
        self.root.geometry("1200x800")

        # Variables
        self.current_experiment = tk.StringVar()
        self.n_participants = tk.IntVar(value=2)
        self.n_trials = tk.IntVar(value=50)
        self.output_file = tk.StringVar(value="")
        self.running = False

        # Thread management
        self.experiment_threads = []
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Experiment status tracking
        self.experiment_status = {}
        self.initialize_experiment_status()

        # Initialize keyboard shortcuts
        if KEYBOARD_SHORTCUTS_AVAILABLE:
            self.keyboard_manager = KeyboardManager(self.root)
            setup_standard_shortcuts(self, self.keyboard_manager)
            # Add custom shortcuts for this GUI
            self._setup_custom_shortcuts()
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
        if THEME_AVAILABLE:
            self.theme_manager = ThemeManager(self.root)
            # Try to load system preference
            system_theme = get_system_theme_preference()
            self.theme_manager.set_theme(system_theme)
        else:
            self.theme_manager = None

        # Create GUI
        self.create_widgets()
        self.populate_experiment_list()

    def _setup_custom_shortcuts(self):
        """Setup custom shortcuts specific to this GUI."""
        if self.keyboard_manager:
            # Run selected experiment
            self.keyboard_manager.bind_shortcut(
                "Return", self.run_selected_experiment, "Run selected experiment"
            )
            # Run all experiments
            self.keyboard_manager.bind_shortcut(
                "Ctrl+Shift+R", self.run_all_experiments, "Run all experiments"
            )

    def initialize_experiment_status(self):
        """Initialize status tracking for all experiments."""
        for exp_name in EXPERIMENTS.keys():
            self.experiment_status[exp_name] = "Not Run"

    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="APGI Experiment Registry", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Left panel - Experiment list and controls
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Experiment list
        ttk.Label(left_frame, text="Experiments:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        # Listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.experiment_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, height=15
        )
        self.experiment_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.experiment_listbox.yview)

        self.experiment_listbox.bind("<<ListboxSelect>>", self.on_experiment_select)

        # Status label
        self.status_label = ttk.Label(
            left_frame, text="Select an experiment to view details", foreground="gray"
        )
        self.status_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))

        # Right panel - Details and controls
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        # Experiment details
        details_frame = ttk.LabelFrame(
            right_frame, text="Experiment Details", padding="10"
        )
        details_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)

        self.details_text = scrolledtext.ScrolledText(
            details_frame, height=10, width=50, wrap=tk.WORD
        )
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Parameters frame
        params_frame = ttk.LabelFrame(right_frame, text="Parameters", padding="10")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Number of participants
        participants_label = ttk.Label(params_frame, text="Number of Participants:")
        participants_label.grid(row=0, column=0, sticky=tk.W)
        add_tooltip(participants_label, "n_participants")

        participants_spinbox = ttk.Spinbox(
            params_frame, from_=1, to=100, width=10, textvariable=self.n_participants
        )
        participants_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        add_tooltip(participants_spinbox, "n_participants")

        # Track for undo/redo
        if self.widget_tracker:
            self.widget_tracker.track_widget(participants_spinbox, "parameter")
            self.widget_tracker.tracked_widgets[str(id(participants_spinbox))][
                "param_name"
            ] = "n_participants"

        # Number of trials
        trials_label = ttk.Label(params_frame, text="Number of Trials:")
        trials_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        add_tooltip(trials_label, "n_trials_per_condition")

        trials_spinbox = ttk.Spinbox(
            params_frame, from_=1, to=1000, width=10, textvariable=self.n_trials
        )
        trials_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        add_tooltip(trials_spinbox, "n_trials_per_condition")

        # Track for undo/redo
        if self.widget_tracker:
            self.widget_tracker.track_widget(trials_spinbox, "parameter")
            self.widget_tracker.tracked_widgets[str(id(trials_spinbox))][
                "param_name"
            ] = "n_trials_per_condition"

        # Output file
        ttk.Label(params_frame, text="Output File (optional):").grid(
            row=2, column=0, sticky=tk.W, pady=(5, 0)
        )
        file_frame = ttk.Frame(params_frame)
        file_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(5, 0))

        file_entry = ttk.Entry(file_frame, textvariable=self.output_file, width=30)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_button = ttk.Button(
            file_frame, text="Browse...", command=self.browse_output_file
        )
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Theme selection
        if self.theme_manager:
            theme_label = ttk.Label(params_frame, text="Theme:")
            theme_label.grid(row=3, column=0, sticky=tk.W, pady=(20, 5))

            theme_selector = self.theme_manager.create_theme_selector(params_frame)
            theme_selector.grid(
                row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5
            )

        # Control buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        self.run_button = ttk.Button(
            button_frame,
            text="Run Selected Experiment",
            command=self.run_selected_experiment,
        )
        self.run_button.pack(side=tk.LEFT, padx=(0, 5))

        self.run_all_button = ttk.Button(
            button_frame, text="Run All Experiments", command=self.run_all_experiments
        )
        self.run_all_button.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_button = ttk.Button(
            button_frame, text="Clear Output", command=self.clear_output
        )
        self.clear_button.pack(side=tk.LEFT)

        # Bottom panel - Output
        output_frame = ttk.LabelFrame(main_frame, text="Output Console", padding="10")
        output_frame.grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0)
        )
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(
            output_frame, height=15, width=100, wrap=tk.WORD
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, variable=self.progress_var, maximum=100, length=400
        )
        self.progress_bar.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0)
        )

    def populate_experiment_list(self):
        """Populate the experiment list with all available experiments."""
        for exp_name in sorted(EXPERIMENTS.keys()):
            self.experiment_listbox.insert(tk.END, exp_name)

    def on_experiment_select(self, event):
        """Handle experiment selection."""
        selection = self.experiment_listbox.curselection()
        if selection:
            index = selection[0]
            exp_name = self.experiment_listbox.get(index)
            self.current_experiment.set(exp_name)
            self.show_experiment_details(exp_name)
            self.update_status(f"Selected: {exp_name}")

    def show_experiment_details(self, exp_name):
        """Show details for the selected experiment."""
        module_path = EXPERIMENTS[exp_name]

        # Try to read the experiment file to get details
        try:
            # Extract file path from module path using cross-platform approach
            module_parts = module_path.split(".")
            script_path = Path(*module_parts).with_suffix(".py")
            full_path = project_root / script_path

            if full_path.exists():
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract docstring
                lines = content.split("\n")
                docstring_lines = []
                in_docstring = False
                docstring_start = False

                for line in lines:
                    if '"""' in line:
                        if not in_docstring:
                            in_docstring = True
                            docstring_start = True
                            # Extract content after the opening """
                            cleaned_line = line.replace('"""', "").strip()
                            if cleaned_line:
                                docstring_lines.append(cleaned_line)
                        else:
                            # End of docstring
                            break
                    elif in_docstring:
                        docstring_lines.append(line.rstrip())

                # If no docstring found, provide basic info
                if not docstring_lines:
                    docstring_lines = [
                        "No description available.",
                        f"This experiment implements the {exp_name} paradigm.",
                        "\nParameters:",
                        f"- n_participants: Number of participants (default: 5)",
                        f"- n_trials_per_condition: Number of trials per condition (default: 20)",
                    ]

                docstring = "\n".join(docstring_lines[:25])  # Limit to first 25 lines

                # Display details
                details = f"Experiment: {exp_name}\n"
                details += f"Module: {module_path}\n"
                details += (
                    f"Status: {self.experiment_status.get(exp_name, 'Not Run')}\n"
                )
                details += f"\n{'='*50}\n\n"
                details += docstring

                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(1.0, details)
            else:
                # File not found - provide basic info
                details = f"Experiment: {exp_name}\n"
                details += f"Module: {module_path}\n"
                details += (
                    f"Status: {self.experiment_status.get(exp_name, 'Not Run')}\n"
                )
                details += f"\n{'='*50}\n\n"
                details += "Source file not found.\n\n"
                details += "This experiment is registered but the source file may be missing.\n"
                details += f"Expected location: {full_path}\n\n"
                details += "Parameters:\n"
                details += "- n_participants: Number of participants\n"
                details += "- n_trials_per_condition: Number of trials per condition"

                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(1.0, details)

        except Exception as e:
            logger.error(f"Error loading experiment details for {exp_name}: {e}")
            # Provide fallback information
            details = f"Experiment: {exp_name}\n"
            details += f"Module: {module_path}\n"
            details += f"Status: {self.experiment_status.get(exp_name, 'Not Run')}\n"
            details += f"\n{'='*50}\n\n"
            details += f"Error loading details: {str(e)}\n\n"
            details += "This experiment is registered but could not be loaded.\n\n"
            details += "Parameters:\n"
            details += "- n_participants: Number of participants\n"
            details += "- n_trials_per_condition: Number of trials per condition"

            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, details)

    def browse_output_file(self):
        """Browse for output file location."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filename:
            self.output_file.set(filename)

    def log_output(self, message):
        """Log message to output console."""
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()

    def update_status(self, message):
        """Update status label."""
        self.status_label.config(text=message)

    def run_selected_experiment(self):
        """Run the selected experiment."""
        selection = self.experiment_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "No Selection", "Please select an experiment to run."
            )
            return

        exp_name = self.experiment_listbox.get(selection[0])

        # Run in separate thread to avoid GUI freezing
        thread = threading.Thread(target=self._run_experiment, args=(exp_name,))
        self.experiment_threads.append(thread)
        thread.start()

    def run_all_experiments(self):
        """Run all experiments."""
        if self.running:
            messagebox.showwarning(
                "Already Running", "Experiments are already running."
            )
            return

        # Confirm before running all
        result = messagebox.askyesno(
            "Run All Experiments",
            f"Run all {len(EXPERIMENTS)} experiments? This may take several minutes.",
        )
        if not result:
            return

        # Run in separate thread
        thread = threading.Thread(target=self._run_all_experiments)
        self.experiment_threads.append(thread)
        thread.start()

    def _run_experiment(self, exp_name):
        """Run a single experiment (called from thread) with subprocess isolation."""
        try:
            self.running = True
            self.log_output(f"Starting experiment: {exp_name}")
            self.update_status(f"Running: {exp_name}")

            # Prepare parameters with correct names
            params = {
                "n_participants": self.n_participants.get(),
                "n_trials_per_condition": self.n_trials.get(),
            }

            if self.output_file.get():
                params["output_file"] = self.output_file.get()

            # Create a simple Python script to run the experiment
            script_content = f"""
import sys
from pathlib import Path

# Add the actual project root to Python path
project_root = Path("{project_root}")
sys.path.insert(0, str(project_root))

try:
    from tools.run_experiments import run_experiment
    result = run_experiment("{exp_name}", n_participants={params["n_participants"]}, n_trials_per_condition={params["n_trials_per_condition"]})
    print("SUCCESS: Experiment completed")
    print(f"RESULT: {{result}}")
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
"""

            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(script_content)
                script_path = f.name

            try:
                # Run experiment in subprocess to isolate from GUI
                start_time = time.time()
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )
                end_time = time.time()

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

                    # Update status
                    self.experiment_status[exp_name] = "Success"
                    self.log_output(
                        f"✓ {exp_name} completed successfully in {end_time - start_time:.2f} seconds"
                    )
                    if result_value != "Experiment completed successfully":
                        self.log_output(f"Result: {result_value}")
                else:
                    self.experiment_status[exp_name] = "Failed"
                    error_msg = error or output or "Unknown error occurred"
                    self.log_output(f"✗ {exp_name} failed: {error_msg}")
                    messagebox.showerror(
                        "Experiment Failed",
                        f"Experiment {exp_name} failed: {error_msg}",
                    )

            except subprocess.TimeoutExpired:
                self.experiment_status[exp_name] = "Failed"
                error_msg = "Experiment timed out after 300 seconds"
                self.log_output(f"✗ {exp_name} failed: {error_msg}")
                messagebox.showerror(
                    "Experiment Failed", f"Experiment {exp_name} timed out"
                )
            except Exception as e:
                self.experiment_status[exp_name] = "Failed"
                error_msg = f"Failed to run experiment subprocess: {e}"
                self.log_output(f"✗ {exp_name} failed: {error_msg}")
                messagebox.showerror(
                    "Experiment Failed", f"Experiment {exp_name} failed: {error_msg}"
                )
            finally:
                # Clean up temporary script
                try:
                    os.unlink(script_path)
                except Exception as e:
                    # Ignore cleanup errors - temp file will be cleaned by OS
                    pass

            # Update GUI if this experiment is selected
            if self.current_experiment.get() == exp_name:
                self.show_experiment_details(exp_name)

        except Exception as e:
            self.experiment_status[exp_name] = "Failed"
            error_msg = f"✗ {exp_name} failed: {str(e)}"
            self.log_output(error_msg)
            messagebox.showerror("Experiment Failed", error_msg)

        finally:
            self.running = False
            self.update_status("Ready")

    def _run_all_experiments(self):
        """Run all experiments (called from thread) with subprocess isolation."""
        try:
            self.running = True
            total_experiments = len(EXPERIMENTS)
            completed = 0

            self.log_output(f"Starting to run all {total_experiments} experiments...")

            for exp_name in sorted(EXPERIMENTS.keys()):
                self.update_status(
                    f"Running: {exp_name} ({completed + 1}/{total_experiments})"
                )

                # Update progress bar
                progress = (completed / total_experiments) * 100
                self.progress_var.set(progress)

                # Prepare parameters with correct names
                params = {
                    "n_participants": self.n_participants.get(),
                    "n_trials_per_condition": self.n_trials.get(),
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
    result = run_experiment("{exp_name}", n_participants={params["n_participants"]}, n_trials_per_condition={params["n_trials_per_condition"]})
    print("SUCCESS: Experiment completed")
    print(f"RESULT: {{result}}")
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
"""

                # Write script to temporary file
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as f:
                    f.write(script_content)
                    script_path = f.name

                try:
                    # Run experiment in subprocess to isolate from GUI
                    start_time = time.time()
                    result = subprocess.run(
                        [sys.executable, script_path],
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5 minute timeout
                    )
                    end_time = time.time()

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

                        self.experiment_status[exp_name] = "Success"
                        self.log_output(
                            f"✓ {exp_name} - Success ({end_time - start_time:.2f}s)"
                        )
                        if result_value != "Experiment completed successfully":
                            self.log_output(f"  Result: {result_value}")
                        logger.info(f"Experiment {exp_name} completed in batch run")
                    else:
                        self.experiment_status[exp_name] = "Failed"
                        error_msg = error or output or "Unknown error occurred"
                        self.log_output(f"✗ {exp_name} - Failed: {error_msg}")
                        logger.error(
                            f"Experiment {exp_name} failed in batch run: {error_msg}"
                        )

                except subprocess.TimeoutExpired:
                    self.experiment_status[exp_name] = "Failed"
                    error_msg = "Experiment timed out after 300 seconds"
                    self.log_output(f"✗ {exp_name} - Failed: {error_msg}")
                    logger.error(f"Experiment {exp_name} timed out in batch run")
                except Exception as e:
                    self.experiment_status[exp_name] = "Failed"
                    error_msg = f"Failed to run experiment subprocess: {e}"
                    self.log_output(f"✗ {exp_name} - Failed: {error_msg}")
                    logger.error(
                        f"Experiment {exp_name} subprocess failed in batch run: {e}"
                    )
                finally:
                    # Clean up temporary script
                    try:
                        os.unlink(script_path)
                    except Exception as e:
                        # Ignore cleanup errors - temp file will be cleaned by OS
                        pass

                completed += 1

                # Small delay to prevent overwhelming
                time.sleep(0.5)

            # Final update
            self.progress_var.set(100)
            self.log_output(f"\nAll experiments completed!")

            # Summary
            successful = sum(
                1 for status in self.experiment_status.values() if status == "Success"
            )
            failed = total_experiments - successful
            self.log_output(f"Summary: {successful} successful, {failed} failed")

        except Exception as e:
            self.log_output(f"Error running all experiments: {e}")
            logger.error(f"Error in batch experiment run: {e}")
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error", f"Error running all experiments: {e}"
                ),
            )

        finally:
            self.running = False
            self.update_status("Ready")

    def clear_output(self):
        """Clear the output console."""
        self.output_text.delete(1.0, tk.END)

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
                self.update_status(f"Undone: {description}")

    def redo(self):
        """Perform redo operation."""
        if self.undo_manager and self.undo_manager.can_redo():
            description = self.undo_manager.redo()
            if description:
                self.update_status(f"Redone: {description}")


def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = ExperimentRegistryGUI(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
