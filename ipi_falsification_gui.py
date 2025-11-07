"""
IPI Framework Falsification Testing System - GUI Application

A comprehensive tkinter-based GUI for the IPI Framework Falsification Testing System.
Provides tabbed interface for different falsification tests, parameter configuration,
progress tracking, and results visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTk
import numpy as np

# Import IPI Framework components
from ipi_framework.main_controller import MainApplicationController
from ipi_framework.config import ConfigManager, IPIParameters, ExperimentalConfig
from ipi_framework.exceptions import IPIFrameworkError


class LogHandler(logging.Handler):
    """Custom logging handler that sends logs to a queue for GUI display."""
    
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        log_entry = self.format(record)
        self.log_queue.put(log_entry)


class ParameterConfigPanel(ttk.Frame):
    """Panel for configuring IPI parameters and experimental settings."""
    
    def __init__(self, parent, config_manager: ConfigManager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.param_vars = {}
        self.exp_vars = {}
        
        self._create_widgets()
        self._load_current_config()
    
    def _create_widgets(self):
        """Create parameter configuration widgets."""
        # IPI Parameters section
        ipi_frame = ttk.LabelFrame(self, text="IPI Parameters")
        ipi_frame.pack(fill="x", padx=5, pady=5)
        
        ipi_params = [
            ("extero_precision", "Exteroceptive Precision", 2.0),
            ("intero_precision", "Interoceptive Precision", 1.5),
            ("extero_error", "Exteroceptive Error", 1.2),
            ("intero_error", "Interoceptive Error", 0.8),
            ("somatic_gain", "Somatic Gain", 1.3),
            ("threshold", "Threshold", 3.5),
            ("steepness", "Steepness", 2.0)
        ]
        
        for i, (param, label, default) in enumerate(ipi_params):
            ttk.Label(ipi_frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.DoubleVar(value=default)
            entry = ttk.Entry(ipi_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.param_vars[param] = var
        
        # Experimental Configuration section
        exp_frame = ttk.LabelFrame(self, text="Experimental Configuration")
        exp_frame.pack(fill="x", padx=5, pady=5)
        
        exp_params = [
            ("n_trials", "Number of Trials", 1000),
            ("n_participants", "Number of Participants", 100),
            ("random_seed", "Random Seed", None),
            ("p3b_threshold", "P3b Threshold (μV)", 5.0),
            ("gamma_plv_threshold", "Gamma PLV Threshold", 0.3),
            ("bold_z_threshold", "BOLD Z Threshold", 3.1),
            ("pci_threshold", "PCI Threshold", 0.4),
            ("alpha_level", "Alpha Level", 0.05),
            ("effect_size_threshold", "Effect Size Threshold", 0.5),
            ("power_threshold", "Power Threshold", 0.8)
        ]
        
        for i, (param, label, default) in enumerate(exp_params):
            ttk.Label(exp_frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            if param == "random_seed":
                var = tk.StringVar(value="")
                entry = ttk.Entry(exp_frame, textvariable=var, width=15)
            else:
                var = tk.DoubleVar(value=default) if isinstance(default, float) else tk.IntVar(value=default)
                entry = ttk.Entry(exp_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.exp_vars[param] = var
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Load Config", command=self._load_config).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Save Config", command=self._save_config).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Apply Changes", command=self._apply_changes).pack(side="right", padx=2)
    
    def _load_current_config(self):
        """Load current configuration into widgets."""
        ipi_params = self.config_manager.get_ipi_parameters()
        exp_config = self.config_manager.get_experimental_config()
        
        # Load IPI parameters
        for param, var in self.param_vars.items():
            if hasattr(ipi_params, param):
                var.set(getattr(ipi_params, param))
        
        # Load experimental configuration
        for param, var in self.exp_vars.items():
            if hasattr(exp_config, param):
                value = getattr(exp_config, param)
                if param == "random_seed" and value is None:
                    var.set("")
                else:
                    var.set(value)
    
    def _load_config(self):
        """Load configuration from file."""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.config_manager.load_config(filename)
                self._load_current_config()
                messagebox.showinfo("Success", "Configuration loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def _save_config(self):
        """Save configuration to file."""
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self._apply_changes()
                self.config_manager.save_config(filename)
                messagebox.showinfo("Success", "Configuration saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def _reset_defaults(self):
        """Reset all parameters to default values."""
        self.config_manager.ipi_params = IPIParameters()
        self.config_manager.experimental_config = ExperimentalConfig()
        self._load_current_config()
    
    def _apply_changes(self):
        """Apply current widget values to configuration."""
        try:
            # Update IPI parameters
            ipi_updates = {}
            for param, var in self.param_vars.items():
                ipi_updates[param] = var.get()
            self.config_manager.update_ipi_parameters(**ipi_updates)
            
            # Update experimental configuration
            exp_updates = {}
            for param, var in self.exp_vars.items():
                value = var.get()
                if param == "random_seed" and value == "":
                    value = None
                exp_updates[param] = value
            self.config_manager.update_experimental_config(**exp_updates)
            
            messagebox.showinfo("Success", "Configuration updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update configuration: {e}")


class FalsificationTestPanel(ttk.Frame):
    """Panel for running falsification tests."""
    
    def __init__(self, parent, test_name: str, controller: MainApplicationController, 
                 progress_callback, log_callback):
        super().__init__(parent)
        self.test_name = test_name
        self.controller = controller
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.is_running = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create test panel widgets."""
        # Test description
        desc_frame = ttk.LabelFrame(self, text="Test Description")
        desc_frame.pack(fill="x", padx=5, pady=5)
        
        descriptions = {
            "Primary": "Tests for full ignition signatures without consciousness",
            "Consciousness Without Ignition": "Tests for consciousness without ignition signatures",
            "Threshold Insensitivity": "Tests neuromodulatory threshold dynamics",
            "Soma-Bias": "Tests interoceptive vs exteroceptive bias"
        }
        
        desc_text = tk.Text(desc_frame, height=3, wrap="word")
        desc_text.pack(fill="x", padx=5, pady=5)
        desc_text.insert("1.0", descriptions.get(self.test_name, "Falsification test"))
        desc_text.config(state="disabled")
        
        # Test parameters
        params_frame = ttk.LabelFrame(self, text="Test Parameters")
        params_frame.pack(fill="x", padx=5, pady=5)
        
        # Common parameters
        ttk.Label(params_frame, text="Number of Trials:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.n_trials_var = tk.IntVar(value=1000)
        ttk.Entry(params_frame, textvariable=self.n_trials_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        if self.test_name in ["Soma-Bias", "Threshold Insensitivity"]:
            ttk.Label(params_frame, text="Number of Participants:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
            self.n_participants_var = tk.IntVar(value=100)
            ttk.Entry(params_frame, textvariable=self.n_participants_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        # Control buttons
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        self.run_button = ttk.Button(control_frame, text="Run Test", command=self._run_test)
        self.run_button.pack(side="left", padx=2)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Test", command=self._stop_test, state="disabled")
        self.stop_button.pack(side="left", padx=2)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self, text="Test Results")
        results_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.results_text = tk.Text(results_frame, wrap="word")
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _run_test(self):
        """Run the falsification test in a separate thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.run_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_var.set(0)
        self.results_text.delete("1.0", "end")
        
        # Start test in separate thread
        thread = threading.Thread(target=self._test_worker, daemon=True)
        thread.start()
    
    def _stop_test(self):
        """Stop the running test."""
        self.is_running = False
        self.run_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log_callback("Test stopped by user")
    
    def _test_worker(self):
        """Worker thread for running tests."""
        try:
            self.log_callback(f"Starting {self.test_name} falsification test...")
            
            # Simulate test execution with progress updates
            for i in range(101):
                if not self.is_running:
                    break
                
                # Update progress
                self.progress_callback(i)
                
                # Simulate work
                import time
                time.sleep(0.05)
                
                # Log progress
                if i % 20 == 0:
                    self.log_callback(f"Test progress: {i}%")
            
            if self.is_running:
                # Simulate test completion
                result = self._generate_mock_result()
                self._display_results(result)
                self.log_callback(f"{self.test_name} test completed successfully")
            
        except Exception as e:
            self.log_callback(f"Test failed: {e}")
        finally:
            self.after(0, self._test_complete)
    
    def _test_complete(self):
        """Called when test completes."""
        self.is_running = False
        self.run_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_var.set(100)
    
    def _generate_mock_result(self) -> Dict[str, Any]:
        """Generate mock test results for demonstration."""
        return {
            "test_type": self.test_name,
            "is_falsified": np.random.choice([True, False]),
            "confidence_level": np.random.uniform(0.8, 0.99),
            "effect_size": np.random.uniform(0.3, 1.2),
            "p_value": np.random.uniform(0.001, 0.049),
            "statistical_power": np.random.uniform(0.8, 0.95),
            "n_trials": self.n_trials_var.get(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _display_results(self, result: Dict[str, Any]):
        """Display test results in the results panel."""
        self.results_text.delete("1.0", "end")
        
        result_text = f"""
Test Type: {result['test_type']}
Falsification Status: {'FALSIFIED' if result['is_falsified'] else 'NOT FALSIFIED'}
Confidence Level: {result['confidence_level']:.3f}
Effect Size: {result['effect_size']:.3f}
P-value: {result['p_value']:.4f}
Statistical Power: {result['statistical_power']:.3f}
Number of Trials: {result['n_trials']}
Timestamp: {result['timestamp']}

{'=' * 50}
INTERPRETATION:
{'=' * 50}

"""
        
        if result['is_falsified']:
            result_text += """
The IPI Framework has been FALSIFIED based on this test.
This indicates that the framework's predictions do not
match the observed experimental data under the tested
conditions.

Statistical significance: p < 0.05
Effect size indicates a meaningful difference from
framework predictions.
"""
        else:
            result_text += """
The IPI Framework has NOT been falsified by this test.
The experimental data is consistent with framework
predictions within statistical confidence limits.

This does not prove the framework is correct, but
indicates it survives this particular falsification
attempt.
"""
        
        self.results_text.insert("1.0", result_text)


class ResultsVisualizationPanel(ttk.Frame):
    """Panel for visualizing test results and statistics."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.results_data = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create visualization widgets."""
        # Control frame
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(control_frame, text="Generate Sample Data", 
                  command=self._generate_sample_data).pack(side="left", padx=2)
        ttk.Button(control_frame, text="Clear Data", 
                  command=self._clear_data).pack(side="left", padx=2)
        ttk.Button(control_frame, text="Export Results", 
                  command=self._export_results).pack(side="right", padx=2)
        
        # Create matplotlib figure
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle("IPI Falsification Test Results")
        
        # Create canvas
        self.canvas = FigureCanvasTk(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initialize empty plots
        self._update_plots()
    
    def _generate_sample_data(self):
        """Generate sample data for demonstration."""
        test_types = ["Primary", "Consciousness Without Ignition", "Threshold Insensitivity", "Soma-Bias"]
        
        self.results_data = []
        for _ in range(20):
            result = {
                "test_type": np.random.choice(test_types),
                "is_falsified": np.random.choice([True, False]),
                "confidence_level": np.random.uniform(0.8, 0.99),
                "effect_size": np.random.uniform(0.1, 1.5),
                "p_value": np.random.uniform(0.001, 0.1),
                "statistical_power": np.random.uniform(0.7, 0.95),
                "timestamp": datetime.now().isoformat()
            }
            self.results_data.append(result)
        
        self._update_plots()
    
    def _clear_data(self):
        """Clear all results data."""
        self.results_data = []
        self._update_plots()
    
    def _update_plots(self):
        """Update all visualization plots."""
        # Clear all axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        
        if not self.results_data:
            # Show empty plots
            self.ax1.text(0.5, 0.5, "No data available", ha="center", va="center", transform=self.ax1.transAxes)
            self.ax2.text(0.5, 0.5, "No data available", ha="center", va="center", transform=self.ax2.transAxes)
            self.ax3.text(0.5, 0.5, "No data available", ha="center", va="center", transform=self.ax3.transAxes)
            self.ax4.text(0.5, 0.5, "No data available", ha="center", va="center", transform=self.ax4.transAxes)
        else:
            # Plot 1: Falsification rates by test type
            test_types = [r["test_type"] for r in self.results_data]
            falsified = [r["is_falsified"] for r in self.results_data]
            
            unique_tests = list(set(test_types))
            falsification_rates = []
            for test in unique_tests:
                test_results = [f for t, f in zip(test_types, falsified) if t == test]
                rate = sum(test_results) / len(test_results) if test_results else 0
                falsification_rates.append(rate)
            
            self.ax1.bar(unique_tests, falsification_rates)
            self.ax1.set_title("Falsification Rates by Test Type")
            self.ax1.set_ylabel("Falsification Rate")
            self.ax1.tick_params(axis='x', rotation=45)
            
            # Plot 2: Effect sizes distribution
            effect_sizes = [r["effect_size"] for r in self.results_data]
            self.ax2.hist(effect_sizes, bins=10, alpha=0.7)
            self.ax2.set_title("Effect Sizes Distribution")
            self.ax2.set_xlabel("Effect Size")
            self.ax2.set_ylabel("Frequency")
            
            # Plot 3: P-values vs Effect sizes
            p_values = [r["p_value"] for r in self.results_data]
            colors = ['red' if f else 'blue' for f in falsified]
            self.ax3.scatter(effect_sizes, p_values, c=colors, alpha=0.6)
            self.ax3.axhline(y=0.05, color='black', linestyle='--', label='α = 0.05')
            self.ax3.set_title("P-values vs Effect Sizes")
            self.ax3.set_xlabel("Effect Size")
            self.ax3.set_ylabel("P-value")
            self.ax3.legend()
            
            # Plot 4: Statistical power distribution
            powers = [r["statistical_power"] for r in self.results_data]
            self.ax4.hist(powers, bins=10, alpha=0.7)
            self.ax4.axvline(x=0.8, color='red', linestyle='--', label='Power = 0.8')
            self.ax4.set_title("Statistical Power Distribution")
            self.ax4.set_xlabel("Statistical Power")
            self.ax4.set_ylabel("Frequency")
            self.ax4.legend()
        
        # Adjust layout and refresh
        self.fig.tight_layout()
        self.canvas.draw()
    
    def add_result(self, result: Dict[str, Any]):
        """Add a new result to the visualization."""
        self.results_data.append(result)
        self._update_plots()
    
    def _export_results(self):
        """Export results to file."""
        if not self.results_data:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.results_data, f, indent=2)
                elif filename.endswith('.csv'):
                    import pandas as pd
                    df = pd.DataFrame(self.results_data)
                    df.to_csv(filename, index=False)
                
                messagebox.showinfo("Success", "Results exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {e}")


class LoggingPanel(ttk.Frame):
    """Panel for displaying system logs and messages."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.log_queue = queue.Queue()
        
        self._create_widgets()
        self._setup_logging()
        self._start_log_polling()
    
    def _create_widgets(self):
        """Create logging panel widgets."""
        # Control frame
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Button(control_frame, text="Clear Logs", command=self._clear_logs).pack(side="left", padx=2)
        ttk.Button(control_frame, text="Save Logs", command=self._save_logs).pack(side="left", padx=2)
        
        # Log level selection
        ttk.Label(control_frame, text="Log Level:").pack(side="right", padx=2)
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(control_frame, textvariable=self.log_level_var, 
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"], 
                                      state="readonly", width=10)
        log_level_combo.pack(side="right", padx=2)
        log_level_combo.bind("<<ComboboxSelected>>", self._change_log_level)
        
        # Log display
        log_frame = ttk.Frame(self)
        log_frame.pack(fill="both", expand=True, padx=5, pady=2)
        
        self.log_text = tk.Text(log_frame, wrap="word", height=15)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
    
    def _setup_logging(self):
        """Setup logging handler."""
        self.log_handler = LogHandler(self.log_queue)
        self.log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        
        # Add handler to root logger
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)
    
    def _start_log_polling(self):
        """Start polling for log messages."""
        self._poll_logs()
    
    def _poll_logs(self):
        """Poll for new log messages."""
        try:
            while True:
                log_message = self.log_queue.get_nowait()
                self._append_log(log_message)
        except queue.Empty:
            pass
        
        # Schedule next poll
        self.after(100, self._poll_logs)
    
    def _append_log(self, message: str):
        """Append log message to display."""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        
        # Limit log size
        lines = int(self.log_text.index("end-1c").split(".")[0])
        if lines > 1000:
            self.log_text.delete("1.0", "100.0")
    
    def _clear_logs(self):
        """Clear all log messages."""
        self.log_text.delete("1.0", "end")
    
    def _save_logs(self):
        """Save logs to file."""
        filename = filedialog.asksaveasfilename(
            title="Save Logs",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get("1.0", "end"))
                messagebox.showinfo("Success", "Logs saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save logs: {e}")
    
    def _change_log_level(self, event=None):
        """Change logging level."""
        level = getattr(logging, self.log_level_var.get())
        self.log_handler.setLevel(level)
        logging.getLogger().setLevel(level)
    
    def add_message(self, message: str):
        """Add a message directly to the log display."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._append_log(f"{timestamp} - GUI - INFO - {message}")


class IPIFalsificationGUI(tk.Tk):
    """Main GUI application for IPI Framework Falsification Testing System."""
    
    def __init__(self):
        super().__init__()
        
        self.title("IPI Framework Falsification Testing System")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.controller = None
        self.system_initialized = False
        
        # Create GUI components
        self._create_menu()
        self._create_main_interface()
        self._initialize_system()
        
        # Handle window closing
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Configuration...", command=self._load_config)
        file_menu.add_command(label="Save Configuration...", command=self._save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results...", command=self._export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # System menu
        system_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="System", menu=system_menu)
        system_menu.add_command(label="Initialize System", command=self._initialize_system)
        system_menu.add_command(label="System Status", command=self._show_system_status)
        system_menu.add_command(label="Validate System", command=self._validate_system)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_interface(self):
        """Create main interface with tabbed layout."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configuration tab
        self.config_panel = ParameterConfigPanel(self.notebook, self.config_manager)
        self.notebook.add(self.config_panel, text="Configuration")
        
        # Falsification test tabs
        test_names = ["Primary", "Consciousness Without Ignition", "Threshold Insensitivity", "Soma-Bias"]
        self.test_panels = {}
        
        for test_name in test_names:
            panel = FalsificationTestPanel(
                self.notebook, test_name, None,  # Controller will be set later
                self._update_progress, self._log_message
            )
            self.test_panels[test_name] = panel
            self.notebook.add(panel, text=test_name)
        
        # Results visualization tab
        self.results_panel = ResultsVisualizationPanel(self.notebook)
        self.notebook.add(self.results_panel, text="Results & Visualization")
        
        # Logging tab
        self.logging_panel = LoggingPanel(self.notebook)
        self.notebook.add(self.logging_panel, text="System Logs")
        
        # Status bar
        self.status_var = tk.StringVar(value="System not initialized")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken")
        status_bar.pack(side="bottom", fill="x")
    
    def _initialize_system(self):
        """Initialize the IPI Framework system."""
        try:
            self.status_var.set("Initializing system...")
            self._log_message("Starting system initialization...")
            
            # Create controller
            self.controller = MainApplicationController()
            
            # Initialize system in separate thread to avoid blocking GUI
            thread = threading.Thread(target=self._init_worker, daemon=True)
            thread.start()
            
        except Exception as e:
            self._log_message(f"Failed to start system initialization: {e}")
            self.status_var.set("Initialization failed")
            messagebox.showerror("Error", f"Failed to initialize system: {e}")
    
    def _init_worker(self):
        """Worker thread for system initialization."""
        try:
            self.controller.initialize_system()
            
            # Update test panels with controller
            for panel in self.test_panels.values():
                panel.controller = self.controller
            
            self.system_initialized = True
            self.after(0, lambda: self.status_var.set("System initialized and ready"))
            self.after(0, lambda: self._log_message("System initialization completed successfully"))
            
        except Exception as e:
            self.after(0, lambda: self.status_var.set("Initialization failed"))
            self.after(0, lambda: self._log_message(f"System initialization failed: {e}"))
            self.after(0, lambda: messagebox.showerror("Error", f"System initialization failed: {e}"))
    
    def _update_progress(self, value: float):
        """Update progress for current operation."""
        # This will be called from test panels
        pass
    
    def _log_message(self, message: str):
        """Log a message to the logging panel."""
        if hasattr(self, 'logging_panel'):
            self.logging_panel.add_message(message)
    
    def _load_config(self):
        """Load configuration from file."""
        self.config_panel._load_config()
    
    def _save_config(self):
        """Save configuration to file."""
        self.config_panel._save_config()
    
    def _export_results(self):
        """Export results from visualization panel."""
        self.results_panel._export_results()
    
    def _show_system_status(self):
        """Show system status dialog."""
        if self.controller:
            status = self.controller.get_system_status()
            status_text = "\n".join([f"{key}: {value}" for key, value in status.items()])
        else:
            status_text = "System not initialized"
        
        messagebox.showinfo("System Status", status_text)
    
    def _validate_system(self):
        """Validate system components."""
        if not self.system_initialized or not self.controller:
            messagebox.showwarning("Warning", "System not initialized")
            return
        
        try:
            self._log_message("Running system validation...")
            validation_results = self.controller.run_system_validation()
            
            result_text = "System Validation Results:\n\n"
            for component, result in validation_results.items():
                status = "PASS" if result else "FAIL"
                result_text += f"{component}: {status}\n"
            
            messagebox.showinfo("Validation Results", result_text)
            self._log_message("System validation completed")
            
        except Exception as e:
            self._log_message(f"System validation failed: {e}")
            messagebox.showerror("Error", f"System validation failed: {e}")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
IPI Framework Falsification Testing System
Version 0.1.0

A comprehensive platform for implementing and validating 
the Interoceptive Predictive Integration (IPI) Framework 
through systematic falsification testing.

This GUI provides an interface for:
- Configuring IPI parameters and experimental settings
- Running falsification tests
- Visualizing results and statistics
- Managing system logs

© 2024 IPI Research Team
"""
        messagebox.showinfo("About", about_text)
    
    def _on_closing(self):
        """Handle application closing."""
        try:
            if self.controller and self.system_initialized:
                self._log_message("Shutting down system...")
                self.controller.shutdown_system()
            
            self.destroy()
        except Exception as e:
            print(f"Error during shutdown: {e}")
            self.destroy()


def main():
    """Main entry point for the GUI application."""
    try:
        app = IPIFalsificationGUI()
        app.mainloop()
    except Exception as e:
        print(f"Failed to start GUI application: {e}")
        messagebox.showerror("Fatal Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()