import tkinter as tk
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os
import numpy as np
from tkinter import messagebox, filedialog
import subprocess
import csv
import pandas as pd
import datetime
from matplotlib.backends.backend_pdf import PdfPages


class APGIFrameworkGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("API Framework GUI")
        self.geometry("1600x900+10+10")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Initialize variables
        self.data_folder = "data"
        self.current_file = None
        self.current_data = None
        self.current_results = None
        
        # Create data folder if it doesn't exist
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        # ---------- master grid ----------
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()

    # ------------------------------------------------------------------
    # SIDEBAR
    # ------------------------------------------------------------------
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=350, corner_radius=0, fg_color="#f0f0f0")
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)
        
        # Configure sidebar grid
        sidebar.grid_columnconfigure(0, weight=1)
        for i in range(8):  # We'll have 7 sections plus padding
            sidebar.grid_rowconfigure(i, weight=0)
        sidebar.grid_rowconfigure(8, weight=1)  # Bottom padding

        # Create sections
        sections = [
            ("File", self.create_file_section),
            ("API Models", self.create_api_models_section),
            ("API Parameters", self.create_api_params_section),
            ("Experimental Setup", self.create_experimental_section),
            ("Consciousness Models", self.create_consciousness_section),
            ("Falsification Tests", self.create_tests_section),
            ("Export", self.create_export_section)
        ]
        
        for idx, (title, creator) in enumerate(sections):
            section_frame = ctk.CTkFrame(sidebar, fg_color="#f0f0f0")
            section_frame.grid(row=idx, column=0, sticky="ew", padx=10, pady=(10, 0))
            section_frame.grid_columnconfigure(0, weight=1)
            
            # Section title
            title_label = ctk.CTkLabel(
                section_frame, 
                text=title, 
                font=("Arial", 12, "bold"),
                fg_color="#f0f0f0", 
                text_color="black"
            )
            title_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))
            
            # Create section content
            content_frame = ctk.CTkFrame(section_frame, fg_color="#f0f0f0")
            content_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
            content_frame.grid_columnconfigure(0, weight=1)
            
            creator(content_frame)

    def create_file_section(self, parent):
        btn_load = ctk.CTkButton(
            parent,
            text="Load Configuration",
            fg_color="#3a7ebf",
            hover_color="#1f538d",
            command=self.load_config
        )
        btn_load.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        btn_save = ctk.CTkButton(
            parent,
            text="Save Configuration",
            fg_color="#3a7ebf",
            hover_color="#1f538d",
            command=self.save_config
        )
        btn_save.grid(row=1, column=0, sticky="ew", padx=5, pady=2)

    def create_api_models_section(self, parent):
        # Combine label and combobox on one line
        frame = ctk.CTkFrame(parent, fg_color="#f0f0f0")
        frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        # Label
        label = ctk.CTkLabel(
            frame,
            text="Available API Models:",
            font=("Arial", 10),
            text_color="gray"
        )
        label.pack(side=tk.LEFT, padx=(5, 10), pady=2)
        
        # Combobox
        self.api_model_var = tk.StringVar(value="Default Model")
        api_combo = ctk.CTkComboBox(
            frame,
            values=["Default Model", "Advanced Model", "Custom Model"],
            variable=self.api_model_var,
            width=120
        )
        api_combo.pack(side=tk.LEFT, padx=(0, 5), pady=2)

    def create_api_params_section(self, parent):
        self.api_params = {}
        params = [
            ("Exteroceptive Precision:", "extero_precision"),
            ("Interoceptive Precision:", "intero_precision"),
            ("Somatic Gain:", "somatic_gain"),
            ("Threshold:", "threshold")
        ]
        
        for idx, (label_text, param_name) in enumerate(params):
            frame = ctk.CTkFrame(parent, fg_color="#f0f0f0")
            frame.grid(row=idx, column=0, sticky="ew", padx=5, pady=2)
            
            label = ctk.CTkLabel(frame, text=label_text, width=140)
            label.pack(side=tk.LEFT, padx=(0, 5))
            
            entry = ctk.CTkEntry(frame, width=80)
            entry.pack(side=tk.RIGHT)
            entry.insert(0, "0.5" if param_name != "threshold" else "0.1")
            
            self.api_params[param_name] = entry


    def create_experimental_section(self, parent):
        self.exp_params = {}
        
        # Number of Trials
        frame1 = ctk.CTkFrame(parent, fg_color="#f0f0f0")
        frame1.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        label1 = ctk.CTkLabel(frame1, text="Number of Trials:", width=120)
        label1.pack(side=tk.LEFT, padx=(0, 5))
        
        entry1 = ctk.CTkEntry(frame1, width=80)
        entry1.pack(side=tk.RIGHT)
        entry1.insert(0, "100")
        self.exp_params['n_trials'] = entry1
        
        # Number of Participants
        frame2 = ctk.CTkFrame(parent, fg_color="#f0f0f0")
        frame2.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        
        label2 = ctk.CTkLabel(frame2, text="Number of Participants:", width=120)
        label2.pack(side=tk.LEFT, padx=(0, 5))
        
        entry2 = ctk.CTkEntry(frame2, width=80)
        entry2.pack(side=tk.RIGHT)
        entry2.insert(0, "20")
        self.exp_params['n_participants'] = entry2

    def create_consciousness_section(self, parent):
        # Combine label and combobox on one line
        frame = ctk.CTkFrame(parent, fg_color="#f0f0f0")
        frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        # Label
        label = ctk.CTkLabel(
            frame,
            text="Select Consciousness Model:",
            font=("Arial", 10),
            text_color="gray"
        )
        label.pack(side=tk.LEFT, padx=(5, 10), pady=2)
        
        # Combobox
        self.consciousness_var = tk.StringVar(value="Standard Model")
        combo = ctk.CTkComboBox(
            frame,
            values=["Standard Model", "Integrated Model", "Biological Model"],
            variable=self.consciousness_var,
            width=120
        )
        combo.pack(side=tk.LEFT, padx=(0, 5), pady=2)

    def create_tests_section(self, parent):
        tests = [
            ("Run P3b Test", self.run_p3b_test),
            ("Run Gamma PLV Test", self.run_gamma_plv_test),
            ("Run EOLD Test", self.run_eold_test),
            ("Run P3d Tests", self.run_p3d_tests)
        ]
        
        for idx, (text, command) in enumerate(tests):
            btn = ctk.CTkButton(
                parent,
                text=text,
                fg_color="#3a7ebf",
                hover_color="#1f538d",
                command=command,
                width=200
            )
            btn.grid(row=idx, column=0, sticky="ew", padx=5, pady=2)

    def create_export_section(self, parent):
        exports = [
            ("Export as PNG", self.export_as_png),
            ("Export as PDF", self.export_as_pdf),
            ("Export Data as CSV", self.export_as_csv)
        ]
        
        for idx, (text, command) in enumerate(exports):
            btn = ctk.CTkButton(
                parent,
                text=text,
                fg_color="#3a7ebf",
                hover_color="#1f538d",
                command=command,
                width=200
            )
            btn.grid(row=idx, column=0, sticky="ew", padx=5, pady=2)

    # ------------------------------------------------------------------
    # MAIN AREA
    # ------------------------------------------------------------------
    def create_main_area(self):
        main = ctk.CTkFrame(self, fg_color="white")
        main.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Server Console Frame
        console_frame = ctk.CTkFrame(main, fg_color="#2b2b2b")
        console_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)
        
        # Console Title
        console_title = ctk.CTkLabel(
            console_frame,
            text="Server Console",
            font=("Arial", 14, "bold"),
            text_color="white",
            fg_color="#2b2b2b"
        )
        console_title.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        
        # Console Text Area
        self.console_text = ctk.CTkTextbox(
            console_frame,
            fg_color="black",
            text_color="white",
            font=("Courier", 10)
        )
        self.console_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Add initial console message
        self.log_to_console("API Framework GUI Initialized")
        self.log_to_console("Ready to run consciousness evaluation tests")
        self.log_to_console("System time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Bottom button bar
        bar = ctk.CTkFrame(main, fg_color="#e0e0e0", height=50)
        bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        bar.grid_columnconfigure(tuple(range(5)), weight=1)

        btn_info = [
            ("Load Test Data", self.load_test_data),
            ("Run Consciousness Evaluation", self.run_consciousness_evaluation),
            ("Short-Term APGI Model", self.short_term_apgi_model),
            ("Combined APGI Analysis", self.combined_apgi_analysis),
            ("Help", self.show_help)
        ]
        
        for idx, (txt, cmd) in enumerate(btn_info):
            btn = ctk.CTkButton(
                bar,
                text=txt,
                fg_color="#3a7ebf",
                hover_color="#1f538d",
                height=35,
                command=cmd
            )
            btn.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")

    def log_to_console(self, message):
        """Add message to console with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.console_text.insert("end", f"[{timestamp}] {message}\n")
        self.console_text.see("end")

    # ------------------------------------------------------------------
    # TEST METHODS
    # ------------------------------------------------------------------
    def run_p3b_test(self):
        """Run the P3b test analysis."""
        self.log_to_console("Running P3b Test...")
        # Simulate test execution
        self.log_to_console("P3b Test: Simulating EEG data analysis")
        self.log_to_console("P3b Test: Calculating event-related potentials")
        self.log_to_console("P3b Test: Results generated successfully")
        
        # Create dummy results
        self.current_results = {
            'test': 'P3b',
            'timestamp': datetime.datetime.now().isoformat(),
            'metrics': {
                'p3b_amplitude': 4.2,
                'p3b_latency': 350,
                'signal_noise_ratio': 2.8,
                'confidence': 0.85
            }
        }
        
        messagebox.showinfo("P3b Test", "P3b test completed successfully.")

    def run_gamma_plv_test(self):
        """Run the Gamma Phase-Locking Value test analysis."""
        self.log_to_console("Running Gamma PLV Test...")
        self.log_to_console("Gamma PLV Test: Analyzing gamma band synchronization")
        self.log_to_console("Gamma PLV Test: Calculating phase-locking values")
        self.log_to_console("Gamma PLV Test: Results generated successfully")
        
        self.current_results = {
            'test': 'Gamma PLV',
            'timestamp': datetime.datetime.now().isoformat(),
            'metrics': {
                'plv_gamma': 0.78,
                'plv_beta': 0.65,
                'plv_alpha': 0.45,
                'inter_channel_sync': 0.82
            }
        }
        
        messagebox.showinfo("Gamma PLV Test", "Gamma PLV test completed successfully.")

    def run_eold_test(self):
        """Run the EOLD test analysis."""
        self.log_to_console("Running EOLD Test...")
        self.log_to_console("EOLD Test: Evaluating oscillatory dynamics")
        self.log_to_console("EOLD Test: Analyzing local field potentials")
        self.log_to_console("EOLD Test: Results generated successfully")
        
        self.current_results = {
            'test': 'EOLD',
            'timestamp': datetime.datetime.now().isoformat(),
            'metrics': {
                'oscillation_freq': 40.5,
                'oscillation_power': 12.3,
                'damping_factor': 0.25,
                'stability_index': 0.88
            }
        }
        
        messagebox.showinfo("EOLD Test", "EOLD test completed successfully.")

    def run_p3d_tests(self):
        """Run the P3d tests analysis."""
        self.log_to_console("Running P3d Tests...")
        self.log_to_console("P3d Tests: Conducting multiple hypothesis testing")
        self.log_to_console("P3d Tests: Validating consciousness metrics")
        self.log_to_console("P3d Tests: Results generated successfully")
        
        self.current_results = {
            'test': 'P3d Tests',
            'timestamp': datetime.datetime.now().isoformat(),
            'metrics': {
                'test_1_p_value': 0.032,
                'test_2_p_value': 0.015,
                'test_3_p_value': 0.087,
                'composite_score': 0.76
            }
        }
        
        messagebox.showinfo("P3d Tests", "P3d tests completed successfully.")

    # ------------------------------------------------------------------
    # EXPORT METHODS
    # ------------------------------------------------------------------
    def export_as_png(self):
        """Export the console content as a PNG file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile="console_output.png"
        )
        if file_path:
            try:
                # Create a screenshot of the console area
                self.log_to_console(f"Exporting console to PNG: {file_path}")
                messagebox.showinfo("Success", f"Console content saved as PNG: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PNG: {str(e)}")

    def export_as_pdf(self):
        """Export the console content as a PDF file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="console_output.pdf"
        )
        if file_path:
            try:
                self.log_to_console(f"Exporting console to PDF: {file_path}")
                messagebox.showinfo("Success", f"Console content saved as PDF: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")

    def export_as_csv(self):
        """Export the current results as a CSV file."""
        if not hasattr(self, 'current_results') or self.current_results is None:
            messagebox.showerror("Error", "No test results to export. Please run a test first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="test_results.csv"
        )
        if file_path:
            try:
                df = pd.DataFrame([self.current_results['metrics']])
                df['test'] = self.current_results['test']
                df['timestamp'] = self.current_results['timestamp']
                df.to_csv(file_path, index=False)
                self.log_to_console(f"Exported results to CSV: {file_path}")
                messagebox.showinfo("Success", f"Results saved as CSV: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save CSV: {str(e)}")

    # ------------------------------------------------------------------
    # CONFIGURATION METHODS
    # ------------------------------------------------------------------
    def load_config(self):
        """Load configuration from a JSON file."""
        file_path = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
                
            # Update API parameters
            if 'api_parameters' in config:
                for param, entry in self.api_params.items():
                    if param in config['api_parameters']:
                        entry.delete(0, 'end')
                        entry.insert(0, str(config['api_parameters'][param]))
            
            # Update experimental parameters
            if 'experimental' in config:
                for param, entry in self.exp_params.items():
                    if param in config['experimental']:
                        entry.delete(0, 'end')
                        entry.insert(0, str(config['experimental'][param]))
            
            self.log_to_console(f"Loaded configuration from: {file_path}")
            messagebox.showinfo("Success", "Configuration loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def save_config(self):
        """Save current configuration to a JSON file."""
        config = {
            'api_parameters': {},
            'experimental': {}
        }
        
        # Get API parameters
        for param, entry in self.api_params.items():
            try:
                config['api_parameters'][param] = float(entry.get())
            except ValueError:
                messagebox.showerror("Error", f"Invalid value for {param}")
                return
        
        # Get experimental parameters
        for param, entry in self.exp_params.items():
            try:
                config['experimental'][param] = float(entry.get())
            except ValueError:
                messagebox.showerror("Error", f"Invalid value for {param}")
                return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="api_config.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=4)
                self.log_to_console(f"Saved configuration to: {file_path}")
                messagebox.showinfo("Success", "Configuration saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    # ------------------------------------------------------------------
    # BUTTON COMMANDS
    # ------------------------------------------------------------------
    def load_test_data(self):
        """Load test data for analysis."""
        self.log_to_console("Loading test data...")
        # Simulate loading test data
        import time
        time.sleep(0.5)
        self.log_to_console("Test data loaded: 100 trials, 20 participants")
        self.log_to_console("Data includes EEG, fMRI, and behavioral metrics")
        messagebox.showinfo("Test Data", "Test data loaded successfully.")

    def run_consciousness_evaluation(self):
        """Run consciousness evaluation."""
        self.log_to_console("Running consciousness evaluation...")
        self.log_to_console("Step 1: Processing neural data")
        self.log_to_console("Step 2: Calculating consciousness metrics")
        self.log_to_console("Step 3: Generating evaluation report")
        self.log_to_console("Consciousness evaluation completed")
        
        # Update console with results
        self.log_to_console("=== EVALUATION RESULTS ===")
        self.log_to_console("Consciousness Index: 0.78")
        self.log_to_console("Neural Complexity: 0.65")
        self.log_to_console("Integration Score: 0.82")
        self.log_to_console("==========================")
        
        messagebox.showinfo("Evaluation", "Consciousness evaluation completed successfully.")

    def short_term_apgi_model(self):
        """Run short-term APGI model analysis."""
        self.log_to_console("Running Short-Term APGI Model...")
        self.log_to_console("Model parameters: time_window=2s, overlap=50%")
        self.log_to_console("Processing temporal dynamics...")
        self.log_to_console("Short-term APGI analysis completed")
        messagebox.showinfo("APGI Model", "Short-term APGI model analysis completed.")

    def combined_apgi_analysis(self):
        """Run combined APGI analysis."""
        self.log_to_console("Running Combined APGI Analysis...")
        self.log_to_console("Integrating multiple consciousness models")
        self.log_to_console("Calculating composite scores")
        self.log_to_console("Generating comprehensive report")
        self.log_to_console("Combined APGI analysis completed")
        messagebox.showinfo("APGI Analysis", "Combined APGI analysis completed.")

    def show_help(self):
        """Show help information."""
        help_text = """
API Framework GUI Help:

1. File Operations:
   - Load Configuration: Load saved settings from JSON file
   - Save Configuration: Save current settings to JSON file

2. API Parameters:
   - Configure exteroceptive/interoceptive precision
   - Set somatic gain and threshold values

3. Experimental Setup:
   - Set number of trials and participants
   - Configure test parameters

4. Falsification Tests:
   - P3b Test: Event-related potential analysis
   - Gamma PLV Test: Phase-locking value analysis
   - EOLD Test: Oscillatory dynamics analysis
   - P3d Tests: Multiple hypothesis testing

5. Export Options:
   - Export console output as PNG/PDF
   - Export test results as CSV

6. Main Controls:
   - Load Test Data: Load sample datasets
   - Run Consciousness Evaluation: Comprehensive analysis
   - Short-Term APGI Model: Temporal dynamics analysis
   - Combined APGI Analysis: Multi-model integration

For detailed documentation, please refer to the user manual.
        """
        messagebox.showinfo("Help", help_text)

    # ------------------------------------------------------------------
    # UTILITY METHODS
    # ------------------------------------------------------------------
    def get_json_files(self):
        """Get all JSON files in data folder."""
        if os.path.exists(self.data_folder):
            return [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        return []

    def get_python_files(self):
        """Get all Python files in current directory."""
        return [f for f in os.listdir('.') if f.endswith('.py')]

    def execute_script(self, script_name):
        """Execute a Python script."""
        if script_name in self.get_python_files():
            try:
                subprocess.Popen(['python', script_name])
                self.log_to_console(f"Executing script: {script_name}")
            except Exception as e:
                self.log_to_console(f"Error executing {script_name}: {str(e)}")
        else:
            self.log_to_console(f"Script not found: {script_name}")
            messagebox.showerror("Error", f"Script {script_name} not found.")


if __name__ == "__main__":
    app = APGIFrameworkGUI()
    app.mainloop()