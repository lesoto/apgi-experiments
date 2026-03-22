"""APGI Experiment Runner GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os

# List of all 29 experiments
EXPERIMENTS = [
    ("AI Benchmarking", "run_ai_benchmarking.py"),
    ("Artificial Grammar Learning", "run_artificial_grammar_learning.py"),
    ("Attentional Blink", "run_attentional_blink.py"),
    ("Binocular Rivalry", "run_binocular_rivalry.py"),
    ("Change Blindness", "run_change_blindness.py"),
    ("DRM False Memory", "run_drm_false_memory.py"),
    ("Dual N-Back", "run_dual_n_back.py"),
    ("Eriksen Flanker", "run_eriksen_flanker.py"),
    ("Go/No-Go", "run_go_no_go.py"),
    ("IGT", "run_igt.py"),
    ("Inattentional Blindness", "run_inattentional_blindness.py"),
    ("Interoceptive Gating", "run_interoceptive_gating.py"),
    ("Iowa Gambling Task", "run_iowa_gambling_task.py"),
    ("Masking", "run_masking.py"),
    ("Metabolic Cost", "run_metabolic_cost.py"),
    ("Multisensory Integration", "run_multisensory_integration.py"),
    ("Navon Task", "run_navon_task.py"),
    ("Posner Cueing", "run_posner_cueing.py"),
    ("Probabilistic Category Learning", "run_probabilistic_category_learning.py"),
    ("Serial Reaction Time", "run_serial_reaction_time.py"),
    ("Simon Effect", "run_simon_effect.py"),
    ("Somatic Marker Priming", "run_somatic_marker_priming.py"),
    ("Sternberg Memory", "run_sternberg_memory.py"),
    ("Stop Signal", "run_stop_signal.py"),
    ("Stroop Effect", "run_stroop_effect.py"),
    ("Time Estimation", "run_time_estimation.py"),
    ("Virtual Navigation", "run_virtual_navigation.py"),
    ("Visual Search", "run_visual_search.py"),
    ("Working Memory Span", "run_working_memory_span.py"),
]


class ExperimentRunnerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("APGI Experiment Runner")
        self.root.geometry("1200x800")

        # Get the auto-improvement directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.auto_improvement_dir = os.path.join(self.script_dir, "auto-improvement")

        # Running experiments set
        self.running_experiments = set()
        self.experiment_buttons = {}

        self._create_ui()

    def _create_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title = ttk.Label(
            main_frame,
            text="APGI Auto-Improvement Experiment Runner",
            font=("Helvetica", 16, "bold"),
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        # Left panel - Buttons
        button_frame = ttk.LabelFrame(
            main_frame, text="Experiments (29 total)", padding="10"
        )
        button_frame.grid(
            row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10)
        )

        # Add scrollbar for buttons
        button_canvas = tk.Canvas(button_frame, width=250)
        scrollbar = ttk.Scrollbar(
            button_frame, orient="vertical", command=button_canvas.yview
        )
        scrollable_frame = ttk.Frame(button_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: button_canvas.configure(scrollregion=button_canvas.bbox("all")),
        )

        button_canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw", width=230
        )
        button_canvas.configure(yscrollcommand=scrollbar.set)

        button_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create buttons for each experiment
        for i, (name, script) in enumerate(EXPERIMENTS):
            btn = ttk.Button(
                scrollable_frame,
                text=f"{i + 1}. {name}",
                command=lambda n=name, s=script: self._run_experiment(n, s),
            )
            btn.pack(fill=tk.X, pady=2)
            self.experiment_buttons[name] = btn

        # Bulk action buttons
        bulk_frame = ttk.Frame(main_frame)
        bulk_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(
            bulk_frame, text="Run All Experiments", command=self._run_all_experiments
        ).pack(fill=tk.X, pady=2)

        ttk.Button(bulk_frame, text="Clear Output", command=self._clear_output).pack(
            fill=tk.X, pady=2
        )

        # Right panel - Output
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(
            output_frame, wrap=tk.WORD, width=80, height=40, font=("Courier", 10)
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN
        )
        status_bar.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 0))

    def _run_experiment(self, name, script):
        """Run a single experiment in a separate thread."""
        if name in self.running_experiments:
            messagebox.showwarning("Already Running", f"{name} is already running!")
            return

        self.running_experiments.add(name)
        self.experiment_buttons[name].configure(state="disabled")
        self._log_output(f"\n{'=' * 60}\n")
        self._log_output(f"STARTING: {name}\n")
        self._log_output(f"Script: {script}\n")
        self._log_output(f"{'-' * 60}\n")
        self.status_var.set(f"Running: {name}...")

        thread = threading.Thread(target=self._execute_script, args=(name, script))
        thread.daemon = True
        thread.start()

    def _execute_script(self, name, script):
        """Execute the experiment script and capture output."""
        script_path = os.path.join(self.auto_improvement_dir, script)

        try:
            result = subprocess.run(
                ["uv", "run", script],
                cwd=self.auto_improvement_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Log stdout
            if result.stdout:
                self.root.after(0, lambda: self._log_output(result.stdout))

            # Log stderr if any
            if result.stderr:
                self.root.after(
                    0, lambda: self._log_output(f"\nSTDERR:\n{result.stderr}\n")
                )

            # Log completion status
            status = (
                "COMPLETED"
                if result.returncode == 0
                else f"FAILED (code {result.returncode})"
            )
            self.root.after(
                0,
                lambda: self._log_output(
                    f"\n{'-' * 60}\n{name}: {status}\n{'=' * 60}\n"
                ),
            )

        except subprocess.TimeoutExpired:
            self.root.after(
                0,
                lambda: self._log_output(
                    f"\nTIMEOUT: {name} exceeded 5 minutes\n{'=' * 60}\n"
                ),
            )
        except Exception as e:
            error_msg = str(e)
            self.root.after(
                0,
                lambda: self._log_output(
                    f"\nERROR running {name}: {error_msg}\n{'=' * 60}\n"
                ),
            )
        finally:
            self.root.after(0, lambda: self._finish_experiment(name))

    def _finish_experiment(self, name):
        """Clean up after experiment finishes."""
        self.running_experiments.discard(name)
        if name in self.experiment_buttons:
            self.experiment_buttons[name].configure(state="normal")

        if not self.running_experiments:
            self.status_var.set("Ready")
        else:
            self.status_var.set(
                f"Running: {len(self.running_experiments)} experiment(s)..."
            )

    def _run_all_experiments(self):
        """Run all experiments sequentially."""
        if self.running_experiments:
            messagebox.showwarning(
                "Experiments Running", "Some experiments are already running!"
            )
            return

        self._log_output(f"\n{'#' * 60}\n")
        self._log_output("# RUNNING ALL 29 EXPERIMENTS\n")
        self._log_output(f"{'#' * 60}\n\n")

        thread = threading.Thread(target=self._run_all_sequential)
        thread.daemon = True
        thread.start()

    def _run_all_sequential(self):
        """Run all experiments one by one in background thread."""
        for name, script in EXPERIMENTS:
            script_path = os.path.join(self.auto_improvement_dir, script)
            self.root.after(0, lambda n=name: self._update_button_state(n, "disabled"))
            self.root.after(0, lambda n=name: self.status_var.set(f"Running: {n}..."))

            script_path = os.path.join(self.auto_improvement_dir, script)

            try:
                self.root.after(
                    0,
                    lambda n=name: self._log_output(
                        f"\n{'=' * 60}\nSTARTING: {n}\n{'-' * 60}\n"
                    ),
                )

                result = subprocess.run(
                    ["uv", "run", script],
                    cwd=self.auto_improvement_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                stdout = result.stdout
                stderr = result.stderr

                self.root.after(
                    0, lambda out=stdout: self._log_output(out) if out else None
                )
                if stderr:
                    self.root.after(
                        0, lambda err=stderr: self._log_output(f"\nSTDERR:\n{err}\n")
                    )

                status = (
                    "COMPLETED"
                    if result.returncode == 0
                    else f"FAILED (code {result.returncode})"
                )
                self.root.after(
                    0,
                    lambda n=name, s=status: self._log_output(
                        f"\n{n}: {s}\n{'=' * 60}\n"
                    ),
                )

            except Exception as e:
                error_msg = str(e)
                self.root.after(
                    0,
                    lambda n=name, msg=error_msg: self._log_output(
                        f"\nERROR running {n}: {msg}\n{'=' * 60}\n"
                    ),
                )
            finally:
                self.root.after(
                    0, lambda n=name: self._update_button_state(n, "normal")
                )

        self.root.after(0, lambda: self.status_var.set("All experiments completed"))
        self.root.after(
            0,
            lambda: self._log_output(
                f"\n{'#' * 60}\n# ALL EXPERIMENTS COMPLETE\n{'#' * 60}\n"
            ),
        )

    def _update_button_state(self, name, state):
        """Update button state from any thread."""
        if name in self.experiment_buttons:
            self.experiment_buttons[name].configure(state=state)

    def _log_output(self, text):
        """Append text to the output area."""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def _clear_output(self):
        """Clear the output text area."""
        self.output_text.delete(1.0, tk.END)


def main():
    root = tk.Tk()
    ExperimentRunnerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
