"""
APGI Framework Falsification Testing System - GUI Application

A comprehensive tkinter-based GUI for the APGI Framework Falsification Testing System.
Provides tabbed interface for different falsification tests, parameter configuration,
progress tracking, and results visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
import json
from apgi_framework.logging.standardized_logging import get_logger

logger = get_logger("apgi_falsification_gui")
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTk
import numpy as np

# Import APGI Framework components
from apgi_framework.main_controller import MainApplicationController
from apgi_framework.config import ConfigManager, APGIParameters, ExperimentalConfig
from apgi_framework.exceptions import APGIFrameworkError


class LogHandler(logging.Handler):
    """Custom logging handler that sends logs to a queue for GUI display."""
    
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        log_entry = self.format(record)
        self.log_queue.put(log_entry)


class ParameterConfigPanel(ttk.Frame):
    """Panel for configuring APGI parameters and experimental settings."""
    
    def __init__(self, parent, config_manager: ConfigManager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.param_vars = {}
        self.exp_vars = {}
        self.param_entries = {}  # Store entry widgets for validation feedback
        self.exp_entries = {}
        
        # Import validator
        from apgi_framework.validation import get_validator
        self.validator = get_validator()
        
        self._create_widgets()
        self._load_current_config()
        self._setup_validation()
    
    def _create_widgets(self):
        """Create parameter configuration widgets."""
        # APGI Parameters section
        apgi_frame = ttk.LabelFrame(self, text="APGI Parameters")
        apgi_frame.pack(fill="x", padx=5, pady=5)
        
        # Get parameter info from validator
        apgi_params = [
            ("extero_precision", "Exteroceptive Precision", 2.0, "Precision of exteroceptive signals (0.01-10.0, typical: 0.5-5.0)"),
            ("intero_precision", "Interoceptive Precision", 1.5, "Precision of interoceptive signals (0.01-10.0, typical: 0.5-5.0)"),
            ("extero_error", "Exteroceptive Error", 1.2, "Exteroceptive prediction error as z-score (-10 to 10, typical: -3 to 3)"),
            ("intero_error", "Interoceptive Error", 0.8, "Interoceptive prediction error as z-score (-10 to 10, typical: -3 to 3)"),
            ("somatic_gain", "Somatic Gain", 1.3, "Somatic marker gain modulating interoceptive precision (0.01-5.0, typical: 0.5-2.0)"),
            ("threshold", "Threshold", 3.5, "Ignition threshold for conscious access (0.1-10.0, typical: 2.0-5.0)"),
            ("steepness", "Steepness", 2.0, "Steepness of sigmoid function (0.1-10.0, typical: 1.0-3.0)")
        ]
        
        for i, (param, label, default, tooltip) in enumerate(apgi_params):
            # Label
            label_widget = ttk.Label(apgi_frame, text=f"{label}:")
            label_widget.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            self._create_tooltip(label_widget, tooltip)
            
            # Entry with validation
            var = tk.DoubleVar(value=default)
            entry = ttk.Entry(apgi_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.param_vars[param] = var
            self.param_entries[param] = entry
            
            # Validation indicator
            indicator = ttk.Label(apgi_frame, text="✓", foreground="green", width=2)
            indicator.grid(row=i, column=2, padx=2, pady=2)
            self.param_entries[f"{param}_indicator"] = indicator
        
        # Experimental Configuration section
        exp_frame = ttk.LabelFrame(self, text="Experimental Configuration")
        exp_frame.pack(fill="x", padx=5, pady=5)
        
        exp_params = [
            ("n_trials", "Number of Trials", 1000, "Number of trials per test (1-100000, typical: 50-1000)"),
            ("n_participants", "Number of Participants", 100, "Number of participants (1-10000, typical: 20-200)"),
            ("random_seed", "Random Seed", None, "Random seed for reproducibility (optional)"),
            ("p3b_threshold", "P3b Threshold (μV)", 5.0, "P3b amplitude threshold in μV (1.0-20.0, typical: 3.0-7.0)"),
            ("gamma_plv_threshold", "Gamma PLV Threshold", 0.3, "Gamma phase-locking value threshold (0.05-0.8, typical: 0.2-0.4)"),
            ("bold_z_threshold", "BOLD Z Threshold", 3.1, "BOLD Z-score threshold (1.0-5.0, typical: 2.3-3.5)"),
            ("pci_threshold", "PCI Threshold", 0.4, "Perturbational Complexity Index threshold (0.1-0.8, typical: 0.3-0.5)"),
            ("alpha_level", "Alpha Level", 0.05, "Statistical significance level (0.001-0.1, typical: 0.05)"),
            ("effect_size_threshold", "Effect Size Threshold", 0.5, "Minimum effect size threshold (0.1-2.0, typical: 0.3-0.8)"),
            ("power_threshold", "Power Threshold", 0.8, "Statistical power threshold (0.5-0.99, typical: 0.8-0.95)")
        ]
        
        for i, (param, label, default, tooltip) in enumerate(exp_params):
            # Label
            label_widget = ttk.Label(exp_frame, text=f"{label}:")
            label_widget.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            self._create_tooltip(label_widget, tooltip)
            
            # Entry
            if param == "random_seed":
                var = tk.StringVar(value="")
                entry = ttk.Entry(exp_frame, textvariable=var, width=15)
            else:
                var = tk.DoubleVar(value=default) if isinstance(default, float) else tk.IntVar(value=default)
                entry = ttk.Entry(exp_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.exp_vars[param] = var
            self.exp_entries[param] = entry
            
            # Validation indicator (skip for random_seed)
            if param != "random_seed":
                indicator = ttk.Label(exp_frame, text="✓", foreground="green", width=2)
                indicator.grid(row=i, column=2, padx=2, pady=2)
                self.exp_entries[f"{param}_indicator"] = indicator
        
        # Validation status frame
        validation_frame = ttk.LabelFrame(self, text="Validation Status")
        validation_frame.pack(fill="x", padx=5, pady=5)
        
        self.validation_text = tk.Text(validation_frame, height=4, wrap="word", font=("Courier", 9))
        validation_scrollbar = ttk.Scrollbar(validation_frame, orient="vertical", command=self.validation_text.yview)
        self.validation_text.configure(yscrollcommand=validation_scrollbar.set)
        self.validation_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        validation_scrollbar.pack(side="right", fill="y")
        self.validation_text.insert("1.0", "✓ All parameters valid")
        self.validation_text.config(state="disabled")
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Load Config", command=self._load_config).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Save Config", command=self._save_config).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Validate All", command=self._validate_all_parameters).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Apply Changes", command=self._apply_changes).pack(side="right", padx=2)
    
    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1, font=("Arial", 9),
                           wraplength=300, justify="left", padx=5, pady=3)
            label.pack()
            
            widget._tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                del widget._tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _setup_validation(self):
        """Setup real-time validation for all parameters."""
        # Add trace callbacks for APGI parameters
        for param, var in self.param_vars.items():
            var.trace_add("write", lambda *args, p=param: self._validate_apgi_parameter(p))
        
        # Add trace callbacks for experimental parameters
        for param, var in self.exp_vars.items():
            if param != "random_seed":  # Skip random seed validation
                var.trace_add("write", lambda *args, p=param: self._validate_exp_parameter(p))
    
    def _validate_apgi_parameter(self, param_name):
        """Validate a single APGI parameter in real-time."""
        try:
            value = self.param_vars[param_name].get()
            result = self.validator.validate_apgi_parameters(**{param_name: value})
            
            indicator = self.param_entries.get(f"{param_name}_indicator")
            if indicator:
                if result.is_valid:
                    indicator.config(text="✓", foreground="green")
                    if result.warnings:
                        indicator.config(text="⚠", foreground="orange")
                        self._create_tooltip(indicator, "\n".join(result.warnings))
                else:
                    indicator.config(text="✗", foreground="red")
                    self._create_tooltip(indicator, "\n".join(result.errors))
        except (tk.TclError, ValueError):
            # Invalid input (e.g., not a number)
            indicator = self.param_entries.get(f"{param_name}_indicator")
            if indicator:
                indicator.config(text="✗", foreground="red")
    
    def _validate_exp_parameter(self, param_name):
        """Validate a single experimental parameter in real-time."""
        try:
            value = self.exp_vars[param_name].get()
            
            # Determine which validator to use
            if param_name in ['n_trials', 'n_participants', 'alpha_level', 'effect_size_threshold', 'power_threshold']:
                result = self.validator.validate_experimental_config(**{param_name: value})
            elif param_name in ['p3b_threshold', 'gamma_plv_threshold', 'bold_z_threshold', 'pci_threshold']:
                result = self.validator.validate_neural_thresholds(**{param_name: value})
            else:
                return
            
            indicator = self.exp_entries.get(f"{param_name}_indicator")
            if indicator:
                if result.is_valid:
                    indicator.config(text="✓", foreground="green")
                    if result.warnings:
                        indicator.config(text="⚠", foreground="orange")
                        self._create_tooltip(indicator, "\n".join(result.warnings))
                else:
                    indicator.config(text="✗", foreground="red")
                    self._create_tooltip(indicator, "\n".join(result.errors))
        except (tk.TclError, ValueError):
            # Invalid input (e.g., not a number)
            indicator = self.exp_entries.get(f"{param_name}_indicator")
            if indicator:
                indicator.config(text="✗", foreground="red")
    
    def _validate_all_parameters(self):
        """Validate all parameters and display comprehensive results."""
        try:
            # Collect all parameter values
            apgi_params = {param: var.get() for param, var in self.param_vars.items()}
            exp_config = {}
            neural_thresholds = {}
            
            for param, var in self.exp_vars.items():
                if param == "random_seed":
                    continue
                value = var.get()
                if param in ['n_trials', 'n_participants', 'alpha_level', 'effect_size_threshold', 'power_threshold']:
                    exp_config[param] = value
                elif param in ['p3b_threshold', 'gamma_plv_threshold', 'bold_z_threshold', 'pci_threshold']:
                    neural_thresholds[param] = value
            
            # Run comprehensive validation
            result = self.validator.validate_all(
                apgi_params=apgi_params,
                experimental_config=exp_config,
                neural_thresholds=neural_thresholds
            )
            
            # Update validation status display
            self.validation_text.config(state="normal")
            self.validation_text.delete("1.0", "end")
            
            if result.is_valid:
                self.validation_text.insert("1.0", "✓ All parameters valid\n\n")
                self.validation_text.tag_add("valid", "1.0", "1.end")
                self.validation_text.tag_config("valid", foreground="green", font=("Courier", 9, "bold"))
            else:
                self.validation_text.insert("1.0", "✗ Validation failed\n\n")
                self.validation_text.tag_add("invalid", "1.0", "1.end")
                self.validation_text.tag_config("invalid", foreground="red", font=("Courier", 9, "bold"))
            
            # Add detailed messages
            message = result.get_message()
            if message:
                self.validation_text.insert("end", message)
            
            self.validation_text.config(state="disabled")
            
            # Show dialog with results
            if result.is_valid:
                if result.warnings or result.suggestions:
                    messagebox.showwarning("Validation Complete", 
                                         f"Parameters are valid but have warnings:\n\n{result.get_message()}")
                else:
                    messagebox.showinfo("Validation Complete", "All parameters are valid!")
            else:
                messagebox.showerror("Validation Failed", 
                                   f"Parameter validation failed:\n\n{result.get_message()}")
            
        except Exception as e:
            messagebox.showerror("Validation Error", f"Failed to validate parameters: {e}")
    
    def _load_current_config(self):
        """Load current configuration into widgets."""
        apgi_params = self.config_manager.get_apgi_parameters()
        exp_config = self.config_manager.get_experimental_config()
        
        # Load APGI parameters
        for param, var in self.param_vars.items():
            if hasattr(apgi_params, param):
                var.set(getattr(apgi_params, param))
        
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
        self.config_manager.apgi_params = APGIParameters()
        self.config_manager.experimental_config = ExperimentalConfig()
        self._load_current_config()
    
    def _apply_changes(self):
        """Apply current widget values to configuration."""
        try:
            # First validate all parameters
            apgi_params = {param: var.get() for param, var in self.param_vars.items()}
            exp_config = {}
            neural_thresholds = {}
            
            for param, var in self.exp_vars.items():
                if param == "random_seed":
                    continue
                value = var.get()
                if param in ['n_trials', 'n_participants', 'alpha_level', 'effect_size_threshold', 'power_threshold']:
                    exp_config[param] = value
                elif param in ['p3b_threshold', 'gamma_plv_threshold', 'bold_z_threshold', 'pci_threshold']:
                    neural_thresholds[param] = value
            
            # Run validation
            result = self.validator.validate_all(
                apgi_params=apgi_params,
                experimental_config=exp_config,
                neural_thresholds=neural_thresholds
            )
            
            if not result.is_valid:
                messagebox.showerror("Validation Failed", 
                                   f"Cannot apply changes - validation failed:\n\n{result.get_message()}")
                return
            
            # Show warnings if any
            if result.warnings:
                response = messagebox.askyesno("Warnings Detected", 
                                              f"Parameters have warnings:\n\n{result.get_message()}\n\nApply anyway?")
                if not response:
                    return
            
            # Update APGI parameters
            apgi_updates = {}
            for param, var in self.param_vars.items():
                apgi_updates[param] = var.get()
            self.config_manager.update_apgi_parameters(**apgi_updates)
            
            # Update experimental configuration
            exp_updates = {}
            for param, var in self.exp_vars.items():
                value = var.get()
                if param == "random_seed" and value == "":
                    value = None
                exp_updates[param] = value
            self.config_manager.update_experimental_config(**exp_updates)
            
            success_msg = "Configuration updated successfully!"
            if result.suggestions:
                success_msg += f"\n\nSuggestions:\n" + "\n".join(f"• {s}" for s in result.suggestions)
            
            messagebox.showinfo("Success", success_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update configuration: {e}")


class FalsificationTestPanel(ttk.Frame):
    """Panel for running falsification tests."""
    
    def __init__(self, parent, test_name: str, controller: MainApplicationController, 
                 progress_callback, log_callback, results_callback):
        super().__init__(parent)
        self.test_name = test_name
        self.controller = controller
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.results_callback = results_callback
        self.is_running = False
        self.test_controller = None
        
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
        
        if not self.test_controller:
            self.log_callback("Error: Test controller not initialized")
            messagebox.showerror("Error", "Test controller not initialized. Please initialize the system first.")
            return
        
        # Validate test parameters before running
        try:
            from apgi_framework.validation import get_validator
            validator = get_validator()
            
            n_trials = self.n_trials_var.get()
            n_participants = getattr(self, 'n_participants_var', None)
            n_participants = n_participants.get() if n_participants else 20
            
            # Validate parameters
            result = validator.validate_experimental_config(
                n_trials=n_trials,
                n_participants=n_participants
            )
            
            if not result.is_valid:
                messagebox.showerror("Invalid Parameters", 
                                   f"Test parameters are invalid:\n\n{result.get_message()}")
                return
            
            # Show warnings if any
            if result.warnings:
                response = messagebox.askyesno("Parameter Warnings", 
                                              f"Test parameters have warnings:\n\n{result.get_message()}\n\nRun test anyway?")
                if not response:
                    return
            
        except Exception as e:
            self.log_callback(f"Warning: Parameter validation failed: {e}")
        
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
            
            # Get test parameters
            n_trials = self.n_trials_var.get()
            n_participants = getattr(self, 'n_participants_var', None)
            n_participants = n_participants.get() if n_participants else 20
            
            # Calculate total operations for progress tracking
            if self.test_name == "Threshold Insensitivity":
                # 5 drug conditions by default
                total_operations = n_trials * n_participants * 5
            else:
                total_operations = n_trials * n_participants
            
            # Run the actual test based on test type with progress tracking
            result = None
            
            if self.test_name == "Primary":
                self.log_callback(f"Running primary falsification test with {n_trials} trials, {n_participants} participants...")
                result = self._run_test_with_progress(
                    lambda: self.test_controller.run_falsification_test(
                        n_trials=n_trials,
                        n_participants=n_participants
                    ),
                    total_operations
                )
            
            elif self.test_name == "Consciousness Without Ignition":
                self.log_callback(f"Running consciousness without ignition test with {n_trials} trials, {n_participants} participants...")
                result = self._run_test_with_progress(
                    lambda: self.test_controller.run_consciousness_without_ignition_test(
                        n_trials=n_trials,
                        n_participants=n_participants
                    ),
                    total_operations
                )
            
            elif self.test_name == "Threshold Insensitivity":
                self.log_callback(f"Running threshold insensitivity test with {n_trials} trials per condition, {n_participants} participants...")
                result = self._run_test_with_progress(
                    lambda: self.test_controller.run_threshold_insensitivity_test(
                        n_trials_per_condition=n_trials,
                        n_participants=n_participants
                    ),
                    total_operations
                )
            
            elif self.test_name == "Soma-Bias":
                self.log_callback(f"Running soma-bias test with {n_trials} trials per participant, {n_participants} participants...")
                result = self._run_test_with_progress(
                    lambda: self.test_controller.run_soma_bias_test(
                        n_trials_per_participant=n_trials,
                        n_participants=n_participants
                    ),
                    total_operations
                )
            
            if self.is_running and result:
                # Display results
                self.after(0, lambda: self._display_results(result))
                self.log_callback(f"{self.test_name} test completed successfully")
                
                # Send results to visualization panel
                if self.results_callback:
                    self.after(0, lambda: self.results_callback(result))
            
        except Exception as e:
            import traceback
            error_msg = f"Test failed: {e}\n{traceback.format_exc()}"
            self.log_callback(error_msg)
            self.after(0, lambda: messagebox.showerror("Test Error", f"Test failed: {e}"))
        finally:
            self.after(0, self._test_complete)
    
    def _run_test_with_progress(self, test_func, total_operations):
        """Run test with simulated progress tracking."""
        import time
        
        # Start progress monitoring thread
        progress_thread = threading.Thread(
            target=self._simulate_progress,
            args=(total_operations,),
            daemon=True
        )
        progress_thread.start()
        
        # Run the actual test
        result = test_func()
        
        # Ensure progress reaches 100%
        self.after(0, lambda: self._update_progress_bar(100))
        
        return result
    
    def _simulate_progress(self, total_operations):
        """Simulate progress updates during test execution."""
        import time
        
        # Estimate time per operation (in seconds)
        time_per_operation = 0.01  # 10ms per operation
        total_time = total_operations * time_per_operation
        
        start_time = time.time()
        last_log_progress = 0
        
        while self.is_running:
            elapsed = time.time() - start_time
            progress = min(95, int((elapsed / total_time) * 100))  # Cap at 95% until complete
            
            # Update progress bar
            self.after(0, lambda p=progress: self._update_progress_bar(p))
            
            # Log progress at 10% intervals
            if progress >= last_log_progress + 10:
                last_log_progress = progress
                completed_ops = int((progress / 100) * total_operations)
                self.log_callback(f"Progress: {progress}% ({completed_ops}/{total_operations} operations)")
            
            # Check if test is complete
            if elapsed >= total_time:
                break
            
            time.sleep(0.1)  # Update every 100ms
    
    def _test_complete(self):
        """Called when test completes."""
        self.is_running = False
        self.run_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_var.set(100)
    
    def set_test_controller(self, test_controller):
        """Set the test controller for this panel."""
        self.test_controller = test_controller
    
    def _update_progress_bar(self, value: float):
        """Update the progress bar value."""
        self.progress_var.set(value)
    
    def _display_results(self, result):
        """Display test results in the results panel."""
        self.results_text.delete("1.0", "end")
        
        # Extract common fields from result object
        if hasattr(result, 'is_framework_falsified'):
            is_falsified = result.is_framework_falsified
        else:
            is_falsified = False
        
        # Build result text based on test type
        result_text = f"""
Test Type: {self.test_name}
Test ID: {result.test_id}
Falsification Status: {'FALSIFIED' if is_falsified else 'NOT FALSIFIED'}
Number of Trials: {result.n_trials}
Number of Participants: {result.n_participants}
Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 50}
STATISTICAL ANALYSIS:
{'=' * 50}

P-value: {result.p_value:.4f}
Effect Size: {result.effect_size:.3f}
Statistical Power: {result.statistical_power:.3f}

"""
        
        # Add test-specific details
        if self.test_name == "Primary":
            result_text += f"""
Falsifying Trials: {result.total_falsifying_trials}
Falsification Rate: {result.falsification_rate:.2%}
Mean Confidence: {result.mean_confidence:.3f}
"""
        
        elif self.test_name == "Consciousness Without Ignition":
            result_text += f"""
Falsifying Trials: {result.total_falsifying_trials}
Falsification Rate: {result.falsification_rate:.2%}
Participants with Falsification: {result.participants_with_falsification}/{result.n_participants}
Meets Threshold Criterion (>20%): {result.meets_threshold_criterion}
Mean Confidence: {result.mean_confidence:.3f}
"""
        
        elif self.test_name == "Threshold Insensitivity":
            result_text += f"""
Insensitive Trials: {result.total_insensitive_trials}
Insensitivity Rate: {result.insensitivity_rate:.2%}
Mean Confidence: {result.mean_confidence:.3f}

Drug Sensitivity Results:
"""
            for drug, drug_result in result.drug_sensitivity_results.items():
                result_text += f"  {drug}: {drug_result['insensitivity_rate']:.2%} insensitive\n"
        
        elif self.test_name == "Soma-Bias":
            result_text += f"""
Mean Beta: {result.mean_beta:.3f}
Median Beta: {result.median_beta:.3f}
Beta Std Dev: {result.beta_std:.3f}
Beta 95% CI: ({result.beta_confidence_interval[0]:.3f}, {result.beta_confidence_interval[1]:.3f})

Bias Distribution:
  Interoceptive Bias: {result.intero_bias_participants} participants ({result.bias_distribution['intero']:.1%})
  Exteroceptive Bias: {result.extero_bias_participants} participants ({result.bias_distribution['extero']:.1%})
  No Bias: {result.no_bias_participants} participants ({result.bias_distribution['none']:.1%})

Sample Size Requirement Met (n>100): {result.meets_sample_size_requirement}
"""
        
        result_text += f"""
{'=' * 50}
INTERPRETATION:
{'=' * 50}

{result.interpretation}
"""
        
        self.results_text.insert("1.0", result_text)


class ResultsVisualizationPanel(ttk.Frame):
    """Panel for visualizing test results and statistics."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.results_data = []
        self.test_run_history = []  # Track multiple runs for comparison
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create visualization widgets."""
        # Control frame
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(control_frame, text="Clear Data", 
                  command=self._clear_data).pack(side="left", padx=2)
        ttk.Button(control_frame, text="Export Results", 
                  command=self._export_results).pack(side="left", padx=2)
        ttk.Button(control_frame, text="Compare Runs", 
                  command=self._show_comparison_view).pack(side="left", padx=2)
        ttk.Button(control_frame, text="Refresh Plots", 
                  command=self._update_plots).pack(side="left", padx=2)
        
        # Visualization mode selector
        ttk.Label(control_frame, text="View:").pack(side="right", padx=2)
        self.view_mode_var = tk.StringVar(value="Overview")
        view_mode_combo = ttk.Combobox(control_frame, textvariable=self.view_mode_var,
                                      values=["Overview", "Statistical Details", "Time Series", "Comparison"],
                                      state="readonly", width=15)
        view_mode_combo.pack(side="right", padx=2)
        view_mode_combo.bind("<<ComboboxSelected>>", lambda e: self._update_plots())
        
        # Summary statistics frame with detailed metrics
        summary_frame = ttk.LabelFrame(self, text="Statistical Summary")
        summary_frame.pack(fill="x", padx=5, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=6, wrap="word", font=("Courier", 9))
        summary_scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scrollbar.set)
        self.summary_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        summary_scrollbar.pack(side="right", fill="y")
        self.summary_text.insert("1.0", "No test results yet. Run tests to see summary statistics.")
        self.summary_text.config(state="disabled")
        
        # Create matplotlib figure with better layout
        self.fig = plt.figure(figsize=(14, 9))
        self.fig.suptitle("APGI Falsification Test Results - Real-Time Analysis", fontsize=14, fontweight='bold')
        
        # Create subplots
        gs = self.fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)
        self.ax1 = self.fig.add_subplot(gs[0, 0])  # Falsification rates
        self.ax2 = self.fig.add_subplot(gs[0, 1])  # Effect sizes
        self.ax3 = self.fig.add_subplot(gs[1, 0])  # P-values
        self.ax4 = self.fig.add_subplot(gs[1, 1])  # Statistical power
        
        # Create canvas
        self.canvas = FigureCanvasTk(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initialize empty plots
        self._update_plots()
    
    def _show_comparison_view(self):
        """Show comparison view for multiple test runs."""
        if len(self.test_run_history) < 2:
            messagebox.showinfo("Info", "Need at least 2 test runs to compare. Run more tests to enable comparison.")
            return
        
        # Switch to comparison view
        self.view_mode_var.set("Comparison")
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
            # Show empty plots with instructions
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.text(0.5, 0.5, "No data available\nRun tests to see results", 
                       ha="center", va="center", transform=ax.transAxes, fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
        else:
            # Extract data
            test_types = [r["test_type"] for r in self.results_data]
            falsified = [r["is_falsified"] for r in self.results_data]
            effect_sizes = [r["effect_size"] for r in self.results_data]
            p_values = [r["p_value"] for r in self.results_data]
            powers = [r["statistical_power"] for r in self.results_data]
            confidence_levels = [r.get("confidence_level", 0.5) for r in self.results_data]
            
            # Plot 1: Falsification rates by test type
            unique_tests = sorted(list(set(test_types)))
            falsification_rates = []
            test_counts = []
            
            for test in unique_tests:
                test_results = [f for t, f in zip(test_types, falsified) if t == test]
                rate = sum(test_results) / len(test_results) if test_results else 0
                falsification_rates.append(rate)
                test_counts.append(len(test_results))
            
            bars = self.ax1.bar(range(len(unique_tests)), falsification_rates, 
                              color=['red' if r > 0.5 else 'green' for r in falsification_rates])
            self.ax1.set_xticks(range(len(unique_tests)))
            self.ax1.set_xticklabels([t.replace('_', '\n') for t in unique_tests], 
                                    rotation=0, ha='center', fontsize=8)
            self.ax1.set_ylabel("Falsification Rate")
            self.ax1.set_title("Falsification Rates by Test Type")
            self.ax1.set_ylim(0, 1.0)
            self.ax1.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
            
            # Add count labels on bars
            for i, (bar, count) in enumerate(zip(bars, test_counts)):
                height = bar.get_height()
                self.ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'n={count}', ha='center', va='bottom', fontsize=8)
            
            # Plot 2: Effect sizes distribution
            self.ax2.hist(effect_sizes, bins=min(10, len(effect_sizes)), 
                         alpha=0.7, color='steelblue', edgecolor='black')
            self.ax2.axvline(x=0.5, color='orange', linestyle='--', 
                           label='Medium effect (0.5)', linewidth=2)
            self.ax2.axvline(x=0.8, color='red', linestyle='--', 
                           label='Large effect (0.8)', linewidth=2)
            self.ax2.set_title("Effect Sizes Distribution")
            self.ax2.set_xlabel("Effect Size (Cohen's d)")
            self.ax2.set_ylabel("Frequency")
            self.ax2.legend(fontsize=8)
            
            # Plot 3: P-values vs Effect sizes (volcano-style plot)
            colors = ['red' if f else 'blue' for f in falsified]
            self.ax3.scatter(effect_sizes, p_values, c=colors, alpha=0.6, s=50)
            self.ax3.axhline(y=0.05, color='black', linestyle='--', 
                           label='α = 0.05', linewidth=2)
            self.ax3.set_title("Statistical Significance vs Effect Size")
            self.ax3.set_xlabel("Effect Size")
            self.ax3.set_ylabel("P-value")
            self.ax3.set_yscale('log')
            self.ax3.legend(['α = 0.05', 'Falsified', 'Not Falsified'], fontsize=8)
            self.ax3.grid(True, alpha=0.3)
            
            # Plot 4: Confidence levels vs Statistical power
            scatter = self.ax4.scatter(confidence_levels, powers, 
                                     c=effect_sizes, cmap='viridis', 
                                     alpha=0.6, s=50)
            self.ax4.axhline(y=0.8, color='red', linestyle='--', 
                           label='Power = 0.8', linewidth=2)
            self.ax4.axvline(x=0.8, color='orange', linestyle='--', 
                           label='Confidence = 0.8', linewidth=2)
            self.ax4.set_title("Confidence vs Statistical Power")
            self.ax4.set_xlabel("Mean Confidence Level")
            self.ax4.set_ylabel("Statistical Power")
            self.ax4.set_xlim(0, 1.0)
            self.ax4.set_ylim(0, 1.0)
            self.ax4.legend(fontsize=8)
            self.ax4.grid(True, alpha=0.3)
            
            # Add colorbar for effect sizes
            cbar = self.fig.colorbar(scatter, ax=self.ax4)
            cbar.set_label('Effect Size', fontsize=8)
        
        # Adjust layout and refresh
        self.fig.tight_layout()
        self.canvas.draw()
    
    def add_result(self, result: Dict[str, Any]):
        """Add a new result to the visualization."""
        self.results_data.append(result)
        self._update_plots()
        self._update_summary_stats()
    
    def _update_summary_stats(self):
        """Update summary statistics display."""
        if not self.results_data:
            self.summary_text.config(state="normal")
            self.summary_text.delete("1.0", "end")
            self.summary_text.insert("1.0", "No test results yet. Run tests to see summary statistics.")
            self.summary_text.config(state="disabled")
            return
        
        # Calculate summary statistics
        total_tests = len(self.results_data)
        falsified_count = sum(1 for r in self.results_data if r["is_falsified"])
        falsification_rate = falsified_count / total_tests
        
        mean_effect_size = np.mean([r["effect_size"] for r in self.results_data])
        mean_p_value = np.mean([r["p_value"] for r in self.results_data])
        mean_power = np.mean([r["statistical_power"] for r in self.results_data])
        mean_confidence = np.mean([r.get("confidence_level", 0.5) for r in self.results_data])
        
        # Count by test type
        test_types = {}
        for r in self.results_data:
            test_type = r["test_type"]
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "falsified": 0}
            test_types[test_type]["total"] += 1
            if r["is_falsified"]:
                test_types[test_type]["falsified"] += 1
        
        # Build summary text
        summary = f"Total Tests: {total_tests} | Falsified: {falsified_count} ({falsification_rate:.1%}) | "
        summary += f"Mean Effect Size: {mean_effect_size:.3f} | Mean P-value: {mean_p_value:.4f} | "
        summary += f"Mean Power: {mean_power:.3f} | Mean Confidence: {mean_confidence:.3f}\n\n"
        
        summary += "By Test Type:\n"
        for test_type, stats in sorted(test_types.items()):
            rate = stats["falsified"] / stats["total"] if stats["total"] > 0 else 0
            summary += f"  {test_type}: {stats['falsified']}/{stats['total']} ({rate:.1%})\n"
        
        # Update display
        self.summary_text.config(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", summary)
        self.summary_text.config(state="disabled")
    
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


class APGIFalsificationGUI(tk.Tk):
    """Main GUI application for APGI Framework Falsification Testing System."""
    
    def __init__(self):
        super().__init__()
        
        self.title("APGI Framework Falsification Testing System")
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
                self._update_progress, self._log_message, self._add_result_to_visualization
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
        """Initialize the APGI Framework system."""
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
            # Import test controllers
            from apgi_framework.falsification.primary_falsification_test import PrimaryFalsificationTest
            from apgi_framework.falsification.consciousness_without_ignition_test import ConsciousnessWithoutIgnitionTest
            from apgi_framework.falsification.threshold_insensitivity_test import ThresholdInsensitivityTest
            from apgi_framework.falsification.soma_bias_test import SomaBiasTest
            
            self.after(0, lambda: self._log_message("Initializing falsification test controllers..."))
            
            # Initialize test controllers
            test_controllers = {
                "Primary": PrimaryFalsificationTest(),
                "Consciousness Without Ignition": ConsciousnessWithoutIgnitionTest(),
                "Threshold Insensitivity": ThresholdInsensitivityTest(),
                "Soma-Bias": SomaBiasTest()
            }
            
            # Update test panels with their respective controllers
            for test_name, panel in self.test_panels.items():
                panel.set_test_controller(test_controllers[test_name])
                self.after(0, lambda name=test_name: self._log_message(f"Initialized {name} test controller"))
            
            self.system_initialized = True
            self.after(0, lambda: self.status_var.set("System initialized and ready"))
            self.after(0, lambda: self._log_message("System initialization completed successfully"))
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.after(0, lambda: self.status_var.set("Initialization failed"))
            self.after(0, lambda: self._log_message(f"System initialization failed: {e}\n{error_details}"))
            self.after(0, lambda: messagebox.showerror("Error", f"System initialization failed: {e}"))
    
    def _update_progress(self, value: float):
        """Update progress for current operation."""
        # This can be used to update a global progress indicator if needed
        # Currently, each test panel manages its own progress bar
        pass
    
    def _log_message(self, message: str):
        """Log a message to the logging panel."""
        if hasattr(self, 'logging_panel'):
            self.logging_panel.add_message(message)
    
    def _add_result_to_visualization(self, result):
        """Add test result to visualization panel."""
        if hasattr(self, 'results_panel'):
            # Convert result object to dictionary for visualization
            result_dict = self._convert_result_to_dict(result)
            self.results_panel.add_result(result_dict)
    
    def _convert_result_to_dict(self, result) -> Dict[str, Any]:
        """Convert result object to dictionary for visualization."""
        result_dict = {
            "test_type": getattr(result, 'test_id', 'Unknown').split('_')[0],
            "is_falsified": getattr(result, 'is_framework_falsified', False),
            "effect_size": getattr(result, 'effect_size', 0.0),
            "p_value": getattr(result, 'p_value', 1.0),
            "statistical_power": getattr(result, 'statistical_power', 0.0),
            "timestamp": getattr(result, 'timestamp', datetime.now()).isoformat()
        }
        
        # Add confidence level based on test type
        if hasattr(result, 'mean_confidence'):
            result_dict["confidence_level"] = result.mean_confidence
        else:
            result_dict["confidence_level"] = 0.5
        
        return result_dict
    
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
APGI Framework Falsification Testing System
Version 0.1.0

A comprehensive platform for implementing and validating 
the Interoceptive Predictive Integration (APGI) Framework 
through systematic falsification testing.

This GUI provides an interface for:
- Configuring APGI parameters and experimental settings
- Running falsification tests
- Visualizing results and statistics
- Managing system logs

© 2024 APGI Research Team
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
            logger.error(f"Error during shutdown: {e}")
            self.destroy()


def main():
    """Main entry point for the GUI application."""
    try:
        app = APGIFalsificationGUI()
        app.mainloop()
    except Exception as e:
        logger.error(f"Failed to start GUI application: {e}")
        messagebox.showerror("Fatal Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()