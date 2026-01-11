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

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.run_experiments import EXPERIMENTS, run_experiment


class ExperimentRegistryGUI:
    """GUI for the APGI Experiment Registry."""

    def __init__(self, root):
        self.root = root
        self.root.title("APGI Experiment Registry")
        self.root.geometry("1200x800")

        # Variables
        self.current_experiment = tk.StringVar()
        self.n_participants = tk.IntVar(value=5)
        self.n_trials = tk.IntVar(value=20)
        self.output_file = tk.StringVar(value="")
        self.running = False

        # Experiment status tracking
        self.experiment_status = {}
        self.initialize_experiment_status()

        # Create GUI
        self.create_widgets()
        self.populate_experiment_list()

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
        ttk.Label(params_frame, text="Number of Participants:").grid(
            row=0, column=0, sticky=tk.W
        )
        participants_spinbox = ttk.Spinbox(
            params_frame, from_=1, to=100, width=10, textvariable=self.n_participants
        )
        participants_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Number of trials
        ttk.Label(params_frame, text="Number of Trials:").grid(
            row=1, column=0, sticky=tk.W, pady=(5, 0)
        )
        trials_spinbox = ttk.Spinbox(
            params_frame, from_=1, to=1000, width=10, textvariable=self.n_trials
        )
        trials_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))

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
            # Extract file path from module path
            file_path = module_path.replace(".", "/") + ".py"
            full_path = project_root / file_path

            if full_path.exists():
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract docstring
                lines = content.split("\n")
                docstring_lines = []
                in_docstring = False

                for line in lines:
                    if '"""' in line:
                        if not in_docstring:
                            in_docstring = True
                            docstring_lines.append(line.strip('"""'))
                        else:
                            break
                    elif in_docstring:
                        docstring_lines.append(line)

                docstring = "\n".join(docstring_lines[:20])  # Limit to first 20 lines

                # Display details
                details = f"Experiment: {exp_name}\n"
                details += f"Module: {module_path}\n"
                details += f"Status: {self.experiment_status[exp_name]}\n"
                details += f"\n{'='*50}\n\n"
                details += docstring

                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(1.0, details)
            else:
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(
                    1.0,
                    f"Experiment: {exp_name}\nModule: {module_path}\n\nFile not found.",
                )
        except Exception as e:
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(
                1.0,
                f"Experiment: {exp_name}\nModule: {module_path}\n\nError loading details: {e}",
            )

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
        thread.daemon = True
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
        thread.daemon = True
        thread.start()

    def _run_experiment(self, exp_name):
        """Run a single experiment (called from thread)."""
        try:
            self.running = True
            self.log_output(f"Starting experiment: {exp_name}")
            self.update_status(f"Running: {exp_name}")

            # Prepare parameters
            params = {
                "n_participants": self.n_participants.get(),
                "n_trials": self.n_trials.get(),
            }

            if self.output_file.get():
                params["output_file"] = self.output_file.get()

            # Run experiment
            start_time = time.time()
            result = run_experiment(exp_name, **params)
            end_time = time.time()

            # Update status
            self.experiment_status[exp_name] = "Success"
            self.log_output(
                f"✓ {exp_name} completed successfully in {end_time - start_time:.2f} seconds"
            )

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
        """Run all experiments (called from thread)."""
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

                # Prepare parameters
                params = {
                    "n_participants": self.n_participants.get(),
                    "n_trials": self.n_trials.get(),
                }

                try:
                    start_time = time.time()
                    result = run_experiment(exp_name, **params)
                    end_time = time.time()

                    self.experiment_status[exp_name] = "Success"
                    self.log_output(
                        f"✓ {exp_name} - Success ({end_time - start_time:.2f}s)"
                    )

                except Exception as e:
                    self.experiment_status[exp_name] = "Failed"
                    self.log_output(f"✗ {exp_name} - Failed: {str(e)}")

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
            messagebox.showerror("Error", f"Error running all experiments: {e}")

        finally:
            self.running = False
            self.update_status("Ready")

    def clear_output(self):
        """Clear the output console."""
        self.output_text.delete(1.0, tk.END)


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
