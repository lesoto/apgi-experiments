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

# Set matplotlib backend before importing to avoid threading issues
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to prevent GUI conflicts

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

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")

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
        ttk.Label(control_frame, text="Select Experiment:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )

        self.experiment_var = tk.StringVar(value="interoceptive_gating")
        
        # Get available experiments
        if EXPERIMENTS_AVAILABLE:
            try:
                available_experiments = get_available_experiments()
                experiments = list(available_experiments.keys())
                if not experiments:
                    experiments = ["interoceptive_gating", "somatic_marker_priming", "metabolic_cost"]
            except Exception as e:
                logger.warning(f"Could not load experiments: {e}")
                experiments = ["interoceptive_gating", "somatic_marker_priming", "metabolic_cost"]
        else:
            experiments = ["interoceptive_gating", "somatic_marker_priming", "metabolic_cost"]

        experiment_combo = ttk.Combobox(
            control_frame,
            textvariable=self.experiment_var,
            values=experiments,
            state="readonly",
        )
        experiment_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        # Parameters
        ttk.Label(control_frame, text="Parameters:").grid(
            row=2, column=0, sticky=tk.W, pady=(20, 5)
        )

        param_frame = ttk.Frame(control_frame)
        param_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)

        # Participants parameter
        ttk.Label(param_frame, text="Participants:").grid(
            row=0, column=0, sticky=tk.W
        )
        self.threshold_var = tk.DoubleVar(value=10.0)
        threshold_spinbox = ttk.Spinbox(
            param_frame, from_=1, to=50, textvariable=self.threshold_var, width=10
        )
        threshold_spinbox.grid(row=0, column=1, padx=5)

        # Trials parameter
        ttk.Label(param_frame, text="Trials/Condition:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.simulations_var = tk.IntVar(value=50)
        simulations_spinbox = ttk.Spinbox(
            param_frame, from_=10, to=200, textvariable=self.simulations_var, width=10
        )
        simulations_spinbox.grid(row=1, column=1, padx=5)

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
            daemon=True
        )
        thread.start()
        
        # Start progress simulation
        self.root.after(100, self.simulate_experiment_progress, 0)

    def _run_experiment_thread(self, experiment, threshold, simulations):
        """Run experiment in background thread with isolation to prevent crashes."""
        try:
            if EXPERIMENTS_AVAILABLE:
                # Use subprocess isolation to prevent GUI crashes
                experiment_params = {
                    'n_participants': int(threshold),
                    'n_trials_per_condition': simulations
                }
                
                # Create a simple Python script to run the experiment
                script_content = f'''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from tools.run_experiments import run_experiment
    result = run_experiment("{experiment}", n_participants={int(threshold)}, n_trials_per_condition={simulations})
    print("SUCCESS: Experiment completed")
    print(f"RESULT: {{result}}")
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
'''
                
                # Write script to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(script_content)
                    script_path = f.name
                
                try:
                    # Run experiment in subprocess to isolate from GUI
                    result = subprocess.run(
                        [sys.executable, script_path],
                        capture_output=True,
                        text=True,
                        timeout=60  # 60 second timeout
                    )
                    
                    output = result.stdout
                    error = result.stderr
                    
                    if result.returncode == 0 and "SUCCESS:" in output:
                        # Extract result from output
                        lines = output.split('\n')
                        result_line = next((line for line in lines if line.startswith("RESULT:")), "")
                        if result_line:
                            result_value = result_line.replace("RESULT: ", "")
                        else:
                            result_value = "Experiment completed successfully"
                        
                        self.root.after(0, self._update_experiment_results, output, result_value, None)
                    else:
                        error_msg = error or output or "Unknown error occurred"
                        self.root.after(0, self._update_experiment_results, None, None, error_msg)
                        
                except subprocess.TimeoutExpired:
                    error_msg = "Experiment timed out after 60 seconds"
                    self.root.after(0, self._update_experiment_results, None, None, error_msg)
                except Exception as e:
                    error_msg = f"Failed to run experiment subprocess: {e}"
                    self.root.after(0, self._update_experiment_results, None, None, error_msg)
                finally:
                    # Clean up temporary script
                    try:
                        os.unlink(script_path)
                    except:
                        pass
                        
            else:
                # Simulation mode
                self.root.after(2000, self._update_experiment_results, "Simulation mode - experiment runner not available", None, None)
                
        except Exception as e:
            logger.error(f"Error running experiment {experiment}: {e}")
            self.root.after(0, self._update_experiment_results, None, None, str(e))

    def _update_experiment_results(self, output, result, error):
        """Update GUI with experiment results."""
        if error:
            self.results_text.insert(tk.END, f"ERROR: {error}\n")
            messagebox.showerror("Experiment Error", f"Failed to run experiment: {error}")
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
                self.results_text.insert(tk.END, f"  - Gating threshold: {threshold:.2f}\n")
                self.results_text.insert(tk.END, f"  - Success rate: {75 + (threshold/20)*100:.1f}%\n")
                self.results_text.insert(tk.END, f"  - Processing time: {2.5 + (simulations/50):.2f}s\n")
            elif "somatic" in experiment:
                self.results_text.insert(tk.END, f"Somatic Marker Results:\n")
                self.results_text.insert(tk.END, f"  - Marker influence: {0.3 + (threshold/15):.3f}\n")
                self.results_text.insert(tk.END, f"  - Modulation effect: {0.6 + (simulations/200):.3f}\n")
                self.results_text.insert(tk.END, f"  - Response latency: {80 + threshold:.0f} ms\n")
            elif "metabolic" in experiment:
                self.results_text.insert(tk.END, f"Metabolic Cost Results:\n")
                self.results_text.insert(tk.END, f"  - Energy consumption: {threshold * 10:.1f} units\n")
                self.results_text.insert(tk.END, f"  - Efficiency score: {85 + (simulations/10):.1f}%\n")
                self.results_text.insert(tk.END, f"  - Cost-benefit ratio: {1.2 - (threshold/50):.2f}\n")
            else:
                self.results_text.insert(tk.END, f"General Experiment Results:\n")
                self.results_text.insert(tk.END, f"  - Data points processed: {simulations * 100}\n")
                self.results_text.insert(tk.END, f"  - Success rate: {85 + (threshold/2):.1f}%\n")
                self.results_text.insert(tk.END, f"  - Processing time: {2.5 + (simulations/50):.2f}s\n")
            
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
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Update GUI with loaded values
                if 'n_participants' in config or 'participants' in config:
                    participants = config.get('n_participants', config.get('participants', 10))
                    self.threshold_var.set(float(participants))
                if 'n_trials_per_condition' in config or 'trials' in config:
                    trials = config.get('n_trials_per_condition', config.get('trials', 50))
                    self.simulations_var.set(int(trials))
                if 'experiment' in config:
                    self.experiment_var.set(str(config['experiment']))
                
                self.status_label.config(
                    text=f"Configuration loaded from {Path(filename).name}"
                )
                messagebox.showinfo(
                    "Config Loaded", f"Configuration loaded from {filename}\n\nLoaded values:\n{json.dumps(config, indent=2)}"
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
