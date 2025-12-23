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
        self.title("APGI Framework GUI")
        self.geometry("1600x900+10+10")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # ---------- master grid ----------
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.data_folder = "data"
        self.current_file = None
        self.current_data = None

        self.create_sidebar()
        self.create_main_area()

    # ------------------------------------------------------------------
    # SIDEBAR
    # ------------------------------------------------------------------
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#e0e0e0")
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)               # keep fixed 300 px
        sidebar.grid_rowconfigure(0, weight=1)      # uniform row expansion

        # wrapper inside sidebar – gives us one column to manage
        wrapper = ctk.CTkFrame(sidebar, fg_color="#e0e0e0")
        wrapper.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        wrapper.grid_columnconfigure(0, weight=1)
        for r in range(7):
            wrapper.grid_rowconfigure(r, weight=1)  # evenly expand all sections

        # build each section
        self.file_frame         = self._section(wrapper, "File", 0)
        self.motivation_frame   = self._section(wrapper, "APGI Models", 1)
        self.psy_concepts_frame = self._section(wrapper, "Psychological Parameters", 2)
        self.consciousness_frame= self._section(wrapper, "Consciousness Models", 3)
        self.export_frame       = self._section(wrapper, "Export", 4)

        self._populate_file()
        self._populate_motivation()
        self._populate_psy_concepts()
        self._populate_consciousness()
        self._populate_export()

    def _section(self, parent, title, row):
        frm = ctk.CTkFrame(parent, fg_color="#e0e0e0")
        frm.grid(row=row, column=0, sticky="nsew", padx=5, pady=5)
        frm.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frm, text=title, font=("Arial", 14, "bold"),
                     fg_color="#e0e0e0", text_color="black")\
            .grid(row=0, column=0, sticky="w", padx=5, pady=2)
        body = ctk.CTkFrame(frm, fg_color="#e0e0e0")
        body.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        body.grid_columnconfigure(0, weight=1)
        return body

    # ------------------------------------------------------------------
    # MAIN AREA
    # ------------------------------------------------------------------
    def create_main_area(self):
        main = ctk.CTkFrame(self, fg_color="white")
        main.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # chart
        self.fig, self.ax = plt.subplots(figsize=(10, 8), facecolor='black')
        self.canvas = FigureCanvasTkAgg(self.fig, master=main)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.ax.set_facecolor('black')
        self.ax.grid(True, color='gray', linestyle='--', alpha=0.5)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(-0.2, 0.2)
        self.ax.plot([0, 0.2, 0.5, 0.8, 1],
                     [0, 0.1, 0.15, 0.1, 0], color='cyan')

        # bottom button bar
        bar = ctk.CTkFrame(main, fg_color="#e0e0e0", height=40)
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
            ctk.CTkButton(bar, text=txt, fg_color="#3a7ebf",
                          hover_color="#1f538d", height=30, command=cmd)\
                .grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")

    # ------------------------------------------------------------------
    # SIDEBAR POPULATORS
    # ------------------------------------------------------------------
    def _add_line(self, parent, widget):
        """helper – add a widget in a new row, left aligned, fixed 200 px width"""
        row = parent.grid_size()[1]
        widget.grid(row=row, column=0, padx=10, pady=3, sticky="w")
        if hasattr(widget, "configure"):
            try:
                widget.configure(width=200)
            except Exception:
                pass


    def _populate_file(self):
        # Configuration management
        btn_load = ctk.CTkButton(self.file_frame, text="Load Configuration",
                               fg_color="#3a7ebf", hover_color="#1f538d",
                               command=self.load_config)
        self._add_line(self.file_frame, btn_load)

        btn_save = ctk.CTkButton(self.file_frame, text="Save Configuration",
                               fg_color="#3a7ebf", hover_color="#1f538d",
                               command=self.save_config)
        self._add_line(self.file_frame, btn_save)

        btn_export = ctk.CTkButton(self.file_frame, text="Export Results",
                                 fg_color="#3a7ebf", hover_color="#1f538d",
                                 command=self.export_results)
        self._add_line(self.file_frame, btn_export)

    def _populate_motivation(self):
        # APGI Parameters section
        lbl_apgi = ctk.CTkLabel(self.motivation_frame, 
                               text="APGI Parameters",
                               font=("Arial", 12, "bold"))
        self._add_line(self.motivation_frame, lbl_apgi)

        self.param_entries = {}
        params = [
            ("extero_precision", "Exteroceptive Precision"),
            ("intero_precision", "Interoceptive Precision"),
            ("somatic_gain", "Somatic Gain"),
            ("threshold", "Threshold"),
            ("steepness", "Steepness")
        ]

        for param, label in params:
            frame = ctk.CTkFrame(self.motivation_frame, fg_color="transparent")
            lbl = ctk.CTkLabel(frame, text=f"{label}:", width=120)
            lbl.pack(side=tk.LEFT, padx=2)
            
            entry = ctk.CTkEntry(frame, width=80)
            entry.pack(side=tk.RIGHT, padx=2)
            self.param_entries[param] = entry
            
            self._add_line(self.motivation_frame, frame)

    def _populate_psy_concepts(self):
        # Experimental Configuration
        lbl_exp = ctk.CTkLabel(self.psy_concepts_frame, 
                              text="Experimental Setup",
                              font=("Arial", 12, "bold"))
        self._add_line(self.psy_concepts_frame, lbl_exp)

        self.exp_entries = {}
        params = [
            ("n_trials", "Number of Trials"),
            ("n_participants", "Number of Participants"),
            ("random_seed", "Random Seed (optional)")
        ]

        for param, label in params:
            frame = ctk.CTkFrame(self.psy_concepts_frame, fg_color="transparent")
            lbl = ctk.CTkLabel(frame, text=f"{label}:", width=120)
            lbl.pack(side=tk.LEFT, padx=2)
            
            entry = ctk.CTkEntry(frame, width=80)
            entry.pack(side=tk.RIGHT, padx=2)
            self.exp_entries[param] = entry
            
            self._add_line(self.psy_concepts_frame, frame)

    def _populate_consciousness(self):
        # Falsification Tests
        lbl_tests = ctk.CTkLabel(self.consciousness_frame, 
                                text="Falsification Tests",
                                font=("Arial", 12, "bold"))
        self._add_line(self.consciousness_frame, lbl_tests)

        tests = [
            ("Run P3b Test", self.run_p3b_test),
            ("Run Gamma PLV Test", self.run_gamma_plv_test),
            ("Run BOLD Test", self.run_bold_test),
            ("Run PCI Test", self.run_pci_test)
        ]

        for test_name, command in tests:
            btn = ctk.CTkButton(self.consciousness_frame, text=test_name,
                              fg_color="#3a7ebf", hover_color="#1f538d",
                              command=command)
            self._add_line(self.consciousness_frame, btn)

    def _populate_export(self):
        # Export Buttons
        btn_export_png = ctk.CTkButton(self.export_frame, 
                                    text="Export as PNG",
                                    fg_color="#3a7ebf",
                                    hover_color="#1f538d",
                                    command=self.export_as_png)
        self._add_line(self.export_frame, btn_export_png)
        
        btn_export_pdf = ctk.CTkButton(self.export_frame,
                                    text="Export as PDF",
                                    fg_color="#3a7ebf",
                                    hover_color="#1f538d",
                                    command=self.export_as_pdf)
        self._add_line(self.export_frame, btn_export_pdf)
        
        btn_export_csv = ctk.CTkButton(self.export_frame,
                                    text="Export Data as CSV",
                                    fg_color="#3a7ebf",
                                    hover_color="#1f538d",
                                    command=self.export_as_csv)
        self._add_line(self.export_frame, btn_export_csv)
        
        btn_export_json = ctk.CTkButton(self.export_frame,
                                     text="Export Data as JSON",
                                     fg_color="#3a7ebf",
                                     hover_color="#1f538d",
                                     command=self.export_as_json)
        self._add_line(self.export_frame, btn_export_json)

    # ------------------------------------------------------------------
    # EXPORT METHODS
    # ------------------------------------------------------------------
    def export_as_png(self):
        """Export the current plot as a PNG file."""
        if not hasattr(self, 'canvas'):
            messagebox.showerror("Error", "No plot to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot saved as {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def export_as_pdf(self):
        """Export the current plot as a PDF file."""
        if not hasattr(self, 'canvas'):
            messagebox.showerror("Error", "No plot to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with PdfPages(file_path) as pdf:
                    pdf.savefig(self.fig, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot saved as {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def export_as_csv(self):
        """Export the current data as a CSV file."""
        if not hasattr(self, 'current_data') or self.current_data is None:
            messagebox.showerror("Error", "No data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                if isinstance(self.current_data, dict):
                    df = pd.DataFrame([self.current_data])
                else:
                    df = pd.DataFrame(self.current_data)
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Data saved as {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def export_as_json(self):
        """Export the current data as a JSON file."""
        if not hasattr(self, 'current_data') or self.current_data is None:
            messagebox.showerror("Error", "No data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.current_data, f, indent=4)
                messagebox.showinfo("Success", f"Data saved as {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    # ------------------------------------------------------------------
    # SESSION MANAGEMENT METHODS
    # ------------------------------------------------------------------
    def refresh_sessions(self):
        """Refresh the list of available sessions."""
        pass
        try:
            # Clear the current list
            self.session_list.delete('1.0', 'end')
            
            # Get all JSON files in the data folder
            session_files = self.get_json_files()
            
            if not session_files:
                self.session_list.insert('end', "No sessions found")
                return
                
            # Display each session file
            for i, session_file in enumerate(session_files, 1):
                self.session_list.insert('end', f"{i}. {session_file}\n")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh sessions: {str(e)}")
    
    def load_session(self, session_file):
        """Load a session from a file."""
        try:
            with open(os.path.join(self.data_folder, session_file), 'r') as f:
                self.current_data = json.load(f)
            self.update_display()
            messagebox.showinfo("Success", f"Loaded session: {session_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session: {str(e)}")
    
    def new_session(self):
        """Create a new session."""
        self.current_data = {
            'psychological_parameters': {},
            'consciousness_metrics': {},
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.update_display()
        messagebox.showinfo("Success", "Created new session")
        
    def update_display(self):
        """Update the UI with the current data."""
        if not hasattr(self, 'current_data') or not self.current_data:
            return
            
        # Update parameter entries
        if 'apgi_parameters' in self.current_data:
            for param, entry in self.param_entries.items():
                if param in self.current_data['apgi_parameters']:
                    entry.delete(0, 'end')
                    entry.insert(0, str(self.current_data['apgi_parameters'][param]))
                    
        # Update experimental entries if they exist
        if hasattr(self, 'exp_entries') and 'experimental' in self.current_data:
            for param, entry in self.exp_entries.items():
                if param in self.current_data['experimental']:
                    entry.delete(0, 'end')
                    entry.insert(0, str(self.current_data['experimental'][param]))

    # ------------------------------------------------------------------
    # EXISTING METHODS (UNCHANGED LOGIC)
    # ------------------------------------------------------------------
    def search(self, event=None):
        query = self.search_entry.get().lower()
        results = []
        for file in self.get_json_files():
            if query in file.lower():
                results.append(f"File: {file}")
        if self.current_data and 'psychological_parameters' in self.current_data:
            for param in self.current_data['psychological_parameters']:
                if query in param.lower():
                    results.append(f"Parameter: {param}")
        if results:
            messagebox.showinfo("Search Results", "\n".join(results))
        else:
            messagebox.showinfo("Search Results", "No results found.")

    def export_csv(self):
        if not self.current_data:
            messagebox.showerror("Error", "No data to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Name', 'Intensity', 'Duration'])
                    writer.writerow([self.current_data.get('name', ''),
                                     self.current_data.get('intensity', ''),
                                     self.current_data.get('duration', '')])
                    writer.writerow([])
                    writer.writerow(['Psychological Parameters'])
                    for param in self.current_data.get('psychological_parameters', []):
                        writer.writerow([param])
                messagebox.showinfo("Success", f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")

    def export_png(self):
        if not self.current_data:
            messagebox.showerror("Error", "No data to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")])
        if file_path:
            try:
                self.fig.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Chart exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export chart: {e}")

    def export_pdf(self):
        if not self.current_data:
            messagebox.showerror("Error", "No data to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                with PdfPages(file_path) as pdf:
                    pdf.savefig(self.fig)
                messagebox.showinfo("Success", f"Chart exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export chart: {e}")

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"),
                                                          ("JSON files", "*.json")])
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    self.current_data = {
                        'name': df['Name'][0],
                        'intensity': df['Intensity'][0],
                        'duration': df['Duration'][0],
                        'psychological_parameters': df['Psychological Parameters'].dropna().tolist()
                    }
                elif file_path.endswith('.json'):
                    with open(file_path, 'r') as file:
                        self.current_data = json.load(file)
                self.update_ui_with_data(self.current_data)
                messagebox.showinfo("Success", f"Data imported from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import data: {e}")

    def update_plot(self, data):
        self.ax.clear()
        self.ax.set_facecolor('black')
        self.ax.grid(True, color='gray', linestyle='--', alpha=0.5)
        self.ax.set_xlim(0, data.get('duration', 1))
        self.ax.set_ylim(0, data.get('intensity', 1))
        x = np.linspace(0, data.get('duration', 1), 100)
        y = data.get('intensity', 1) * np.sin(np.pi * x / data.get('duration', 1))
        self.ax.plot(x, y, color='cyan', label='APGI Model')
        self.ax.set_title(data.get('name', 'APGI Model'), color='white')
        self.ax.set_xlabel('Time', color='white')
        self.ax.set_ylabel('Intensity', color='white')
        self.canvas.draw()

    def show_help(self):
        help_text = """
APGI Framework GUI Help:

1. Search: Use the search bar to find APGI files or psychological parameters.
2. File Operations: Open, create, or delete APGI model files.
3. APGI Parameters: Modify name, intensity, and duration.
4. Psychological Parameters: Add and view parameters related to APGI models.
5. Visualization: View APGI model data in line charts.
6. Export: Export your data as CSV, PNG, or PDF.
7. Import: Import data from CSV or JSON files.
8. Interactive Chart: Click on the chart to get point values, scroll to zoom.

For more detailed information, please refer to the user manual.
"""
        messagebox.showinfo("Help", help_text)

    # ---------- file handling ----------
    def get_json_files(self):
        return [f for f in os.listdir(self.data_folder) if f.endswith('.json')]

    def get_python_files(self):
        return [f for f in os.listdir() if f.endswith('.py')]

    def update_files_list(self):
        self.files_listbox.delete("1.0", "end")
        self.files_listbox.insert("end", "JSON Files:\n")
        for file in self.get_json_files():
            self.files_listbox.insert("end", f"  {file}\n")
        self.files_listbox.insert("end", "\nPython Scripts:\n")
        for file in self.get_python_files():
            self.files_listbox.insert("end", f"  {file}\n")

    def on_file_double_click(self, event):
        index = self.files_listbox.index(f"@{event.x},{event.y}")
        line_start = self.files_listbox.index(f"{index} linestart")
        line_end = self.files_listbox.index(f"{index} lineend")
        line = self.files_listbox.get(line_start, line_end).strip()
        if line.endswith('.json'):
            self.current_file = line
            self.open_file()
        elif line.endswith('.py'):
            self.open_python_script(line)

    def update_file_selection(self, choice):
        self.current_file = choice

    def open_file(self):
        if self.current_file:
            file_path = os.path.join(self.data_folder, self.current_file)
            try:
                with open(file_path, 'r') as file:
                    self.current_data = json.load(file)
                    self.update_ui_with_data(self.current_data)
                messagebox.showinfo("Success", f"File {self.current_file} loaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {e}")

    def open_python_script(self, script_name):
        try:
            subprocess.Popen(['python', script_name])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open {script_name}: {str(e)}")

    def save_file(self):
        if self.current_file and self.current_data:
            file_path = os.path.join(self.data_folder, self.current_file)
            try:
                with open(file_path, 'w') as file:
                    json.dump(self.current_data, file, indent=4)
                messagebox.showinfo("Success", f"File {self.current_file} saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {e}")

    def update_ui_with_data(self, data):
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, data.get('name', ''))
        self.intensity_entry.delete(0, 'end')
        self.intensity_entry.insert(0, str(data.get('intensity', '')))
        self.duration_entry.delete(0, 'end')
        self.duration_entry.insert(0, str(data.get('duration', '')))

        self.psy_concepts_listbox.delete("1.0", "end")
        for param in data.get('psychological_parameters', []):
            self.psy_concepts_listbox.insert("end", f"{param}\n")

        self.update_plot(data)

    def modify_parameters(self):
        if self.current_data:
            self.current_data['name'] = self.name_entry.get()
            self.current_data['intensity'] = float(self.intensity_entry.get())
            self.current_data['duration'] = float(self.duration_entry.get())
            self.update_plot(self.current_data)
            messagebox.showinfo("Success", "Parameters updated successfully.")

    def add_psy_parameter(self):
        param = ctk.CTkInputDialog(text="Enter a psychological parameter:",
                                   title="Add Parameter").get_input()
        if param:
            if 'psychological_parameters' not in self.current_data:
                self.current_data['psychological_parameters'] = []
            self.current_data['psychological_parameters'].append(param)
            self.psy_concepts_listbox.insert("end", f"{param}\n")

    def new_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    json.dump({"name": "", "intensity": 0, "duration": 0,
                               "psychological_parameters": []}, file)
                self.update_files_list()
                messagebox.showinfo("Success", "New file created successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error creating file: {e}")

    def delete_file(self):
        if self.current_file:
            confirm = messagebox.askyesno("Confirm Delete",
                                          f"Are you sure you want to delete {self.current_file}?")
            if confirm:
                try:
                    os.remove(os.path.join(self.data_folder, self.current_file))
                    self.update_files_list()
                    self.current_file = None
                    self.current_data = None
                    messagebox.showinfo("Success", "File deleted successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error deleting file: {e}")

    # ---------- script runners ----------
    def load_test_data(self):
        self.execute_script("Access-Mocked-Data.py")

    def run_consciousness_evaluation(self):
        self.execute_script("Consciousness-Evaluator.py")

    def short_term_apgi_model(self):
        self.execute_script("Short-Term-Model.py")

    def combined_apgi_analysis(self):
        self.execute_script("Combined-Model-Motivation.py")

    def execute_script(self, script_name):
        if script_name in self.get_python_files():
            self.open_python_script(script_name)
        else:
            messagebox.showerror("Error", f"Script {script_name} not found.")

    def run_p3b_test(self):
        """Run the P3b test analysis."""
        self.execute_script("P3b-Test.py")

    def run_gamma_plv_test(self):
        """Run the Gamma Phase-Locking Value test analysis."""
        self.execute_script("Gamma-PLV-Test.py")

    def run_bold_test(self):
        """Run the BOLD signal test analysis."""
        self.execute_script("BOLD-Test.py")

    def run_pci_test(self):
        """Run the Perturbational Complexity Index test analysis."""
        self.execute_script("PCI-Test.py")


# ----------------------------------------------------------------------
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
                # Update parameter entries
                for param, entry in self.param_entries.items():
                    if param in config.get('apgi_parameters', {}):
                        entry.delete(0, 'end')
                        entry.insert(0, str(config['apgi_parameters'][param]))
                # Update experimental entries if they exist
                if hasattr(self, 'exp_entries'):
                    for param, entry in self.exp_entries.items():
                        if param in config.get('experimental', {}):
                            entry.delete(0, 'end')
                            entry.insert(0, str(config['experimental'][param]))
                messagebox.showinfo("Success", "Configuration loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def save_config(self):
        """Save current configuration to a JSON file."""
        config = {
            'apgi_parameters': {},
            'experimental': {}
        }
        
        # Get APGI parameters
        for param, entry in self.param_entries.items():
            try:
                config['apgi_parameters'][param] = float(entry.get())
            except ValueError:
                messagebox.showerror("Error", f"Invalid value for {param}")
                return
        
        # Get experimental parameters if they exist
        if hasattr(self, 'exp_entries'):
            for param, entry in self.exp_entries.items():
                try:
                    if param == 'random_seed':
                        val = entry.get()
                        config['experimental'][param] = int(val) if val else None
                    else:
                        config['experimental'][param] = float(entry.get())
                except ValueError:
                    messagebox.showerror("Error", f"Invalid value for {param}")
                    return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="apgi_config.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=4)
                messagebox.showinfo("Success", "Configuration saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def export_results(self):
        """Export current results to a file."""
        if not hasattr(self, 'current_results'):
            messagebox.showinfo("Info", "No results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            initialfile="apgi_results.json"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    if 'metrics' in self.current_results:
                        writer.writerow(['Metric', 'Value'])
                        for metric, value in self.current_results['metrics'].items():
                            writer.writerow([metric, value])
            else:
                with open(file_path, 'w') as f:
                    json.dump(self.current_results, f, indent=4)
            
            messagebox.showinfo("Success", "Results exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")


if __name__ == "__main__":
    app = APGIFrameworkGUI()
    app.mainloop()