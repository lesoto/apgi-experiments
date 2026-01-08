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

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TEMPLATE")

class TemplateGUI:
    """Simplified APGI Framework GUI Template."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("APGI Framework - Template GUI")
        self.root.geometry("800x600")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
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
            font=('Arial', 16, 'bold')
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
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Experiment selection
        ttk.Label(control_frame, text="Select Experiment:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.experiment_var = tk.StringVar(value="threshold_effects")
        experiments = [
            "Threshold Effects",
            "Somatic Markers", 
            "Precision Effects",
            "Dynamic Threshold"
        ]
        
        experiment_combo = ttk.Combobox(control_frame, textvariable=self.experiment_var, values=experiments, state="readonly")
        experiment_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Parameters
        ttk.Label(control_frame, text="Parameters:").grid(row=2, column=0, sticky=tk.W, pady=(20, 5))
        
        param_frame = ttk.Frame(control_frame)
        param_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Threshold parameter
        ttk.Label(param_frame, text="Threshold (θₜ):").grid(row=0, column=0, sticky=tk.W)
        self.threshold_var = tk.DoubleVar(value=5.0)
        threshold_spinbox = ttk.Spinbox(param_frame, from_=1.0, to=10.0, textvariable=self.threshold_var, width=10)
        threshold_spinbox.grid(row=0, column=1, padx=5)
        
        # Simulations parameter
        ttk.Label(param_frame, text="Simulations:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.simulations_var = tk.IntVar(value=10)
        simulations_spinbox = ttk.Spinbox(param_frame, from_=1, to=100, textvariable=self.simulations_var, width=10)
        simulations_spinbox.grid(row=1, column=1, padx=5)
        
        # Action buttons
        ttk.Label(control_frame, text="Actions:").grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.run_button = ttk.Button(button_frame, text="Run Experiment", command=self.run_experiment)
        self.run_button.grid(row=0, column=0, padx=2, pady=2)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Results", command=self.clear_results)
        self.clear_button.grid(row=0, column=1, padx=2, pady=2)
        
        self.export_button = ttk.Button(button_frame, text="Export Data", command=self.export_data)
        self.export_button.grid(row=1, column=0, padx=2, pady=2)
        
        self.load_button = ttk.Button(button_frame, text="Load Config", command=self.load_config)
        self.load_button.grid(row=1, column=1, padx=2, pady=2)
    
    def create_display_panel(self):
        """Create the right display panel."""
        display_frame = ttk.LabelFrame(self.main_frame, text="Results Display", padding="10")
        display_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create text widget for results
        self.results_text = tk.Text(display_frame, wrap=tk.WORD, width=50, height=20)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Initial message
        self.results_text.insert(tk.END, "Welcome to APGI Framework Template GUI\n\n")
        self.results_text.insert(tk.END, "Select an experiment and click 'Run Experiment' to begin.\n")
        self.results_text.insert(tk.END, "Results will appear here.\n")
    
    def create_status_panel(self):
        """Create the bottom status panel."""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
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
        self.results_text.insert(tk.END, f"  - Threshold (θₜ): {threshold}\n")
        self.results_text.insert(tk.END, f"  - Simulations: {simulations}\n\n")
        
        # Simulate experiment progress
        self.root.after(100, self.simulate_experiment_progress, 0)
    
    def simulate_experiment_progress(self, progress):
        """Simulate experiment progress."""
        if progress <= 100:
            self.progress_var.set(progress)
            self.status_label.config(text=f"Running experiment... {progress}%")
            
            if progress % 20 == 0:
                self.results_text.insert(tk.END, f"Progress: {progress}% - Processing data...\n")
                self.results_text.see(tk.END)
                self.root.update_idletasks()
            
            # Continue progress
            self.root.after(200, lambda: self.simulate_experiment_progress(progress + 10))
        else:
            self.complete_experiment()
    
    def complete_experiment(self):
        """Complete the experiment simulation."""
        self.progress_var.set(0)
        self.status_label.config(text="Experiment completed")
        
        # Show results
        self.results_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.results_text.insert(tk.END, "EXPERIMENT RESULTS\n")
        self.results_text.insert(tk.END, "="*50 + "\n\n")
        
        experiment = self.experiment_var.get()
        threshold = self.threshold_var.get()
        simulations = self.simulations_var.get()
        
        # Simulate some results based on experiment type
        if "Threshold" in experiment:
            self.results_text.insert(tk.END, f"Threshold Analysis Results:\n")
            self.results_text.insert(tk.END, f"  - Optimal threshold: {threshold:.2f}\n")
            self.results_text.insert(tk.END, f"  - Ignition probability: {0.75 + (threshold/20):.3f}\n")
            self.results_text.insert(tk.END, f"  - Convergence time: {150 + simulations:.0f} steps\n")
        elif "Somatic" in experiment:
            self.results_text.insert(tk.END, f"Somatic Marker Analysis:\n")
            self.results_text.insert(tk.END, f"  - Marker influence: {0.3 + (threshold/15):.3f}\n")
            self.results_text.insert(tk.END, f"  - Modulation effect: {0.6 + (simulations/200):.3f}\n")
            self.results_text.insert(tk.END, f"  - Response latency: {80 + threshold:.0f} ms\n")
        else:
            self.results_text.insert(tk.END, f"General Experiment Results:\n")
            self.results_text.insert(tk.END, f"  - Data points processed: {simulations * 100}\n")
            self.results_text.insert(tk.END, f"  - Success rate: {85 + (threshold/2):.1f}%\n")
            self.results_text.insert(tk.END, f"  - Processing time: {2.5 + (simulations/50):.2f}s\n")
        
        self.results_text.insert(tk.END, f"\nExperiment completed successfully!\n")
        self.results_text.see(tk.END)
        
        messagebox.showinfo("Experiment Complete", f"{experiment} completed successfully!")
    
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
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
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
                # Simple config loading simulation
                self.threshold_var.set(6.0)
                self.simulations_var.set(20)
                self.experiment_var.set("Precision Effects")
                
                self.status_label.config(text=f"Configuration loaded from {Path(filename).name}")
                messagebox.showinfo("Config Loaded", f"Configuration loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load configuration: {e}")
    
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
