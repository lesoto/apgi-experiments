import os

os.environ.setdefault("MPLBACKEND", "Agg")

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import inspect
import importlib
import sys
import queue
from typing import Any, Dict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

# Add tools directory to Python path
tools_dir = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

from run_experiments import get_available_experiments, run_experiment


class StreamRedirector:
    def __init__(self, stream, q: queue.Queue):
        self._stream = stream
        self._q = q

    def write(self, data):
        if data:
            self._q.put(data)
        return self._stream.write(data)

    def flush(self):
        return self._stream.flush()


class ExperimentGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("APGI Experiments Runner")
        self.geometry("900x600")

        self.experiments = get_available_experiments()
        self.param_widgets: Dict[str, Any] = {}
        self.log_queue: queue.Queue[str] = queue.Queue()
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        sys.stdout = StreamRedirector(sys.stdout, self.log_queue)
        sys.stderr = StreamRedirector(sys.stderr, self.log_queue)

        self._build_ui()
        self.after(100, self._poll_log_queue)

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(top, text="Experiment:").pack(side=tk.LEFT)
        self.exp_var = tk.StringVar()
        self.exp_combo = ttk.Combobox(top, textvariable=self.exp_var, state="readonly")
        self.exp_combo["values"] = list(self.experiments.keys())
        if self.exp_combo["values"]:
            self.exp_combo.current(0)
        self.exp_combo.pack(side=tk.LEFT, padx=8)
        self.exp_combo.bind("<<ComboboxSelected>>", lambda e: self._rebuild_params())

        self.run_btn = ttk.Button(top, text="Run", command=self._on_run)
        self.run_btn.pack(side=tk.LEFT, padx=8)

        self.status_var = tk.StringVar(value="Idle")
        self.status_lbl = ttk.Label(top, textvariable=self.status_var)
        self.status_lbl.pack(side=tk.RIGHT)

        self.params_frame = ttk.LabelFrame(self, text="Parameters")
        self.params_frame.pack(fill=tk.X, padx=10, pady=5)

        log_frame = ttk.LabelFrame(self, text="Logs")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self._rebuild_params()

    def _clear_params(self):
        for child in self.params_frame.winfo_children():
            child.destroy()
        self.param_widgets.clear()

    def _rebuild_params(self):
        self._clear_params()
        name = self.exp_var.get() or (
            self.exp_combo["values"][0] if self.exp_combo["values"] else ""
        )
        if not name:
            return
        try:
            module_path = self.experiments[name]
            module = importlib.import_module(module_path)
            run_func_name = f"run_{name}_experiment"
            if not hasattr(module, run_func_name):
                raise AttributeError(f"{module_path} missing {run_func_name}")
            run_func = getattr(module, run_func_name)
            sig = inspect.signature(run_func)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        row = 0
        for pname, param in sig.parameters.items():
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            ttk.Label(self.params_frame, text=pname).grid(
                row=row, column=0, sticky=tk.W, padx=6, pady=4
            )
            default = None if param.default is inspect._empty else param.default
            widget: Any
            if isinstance(default, bool):
                var = tk.BooleanVar(value=default)
                widget = ttk.Checkbutton(self.params_frame, variable=var)
                widget.var = var
            else:
                var = tk.StringVar(value="" if default is None else str(default))
                widget = ttk.Entry(self.params_frame, textvariable=var, width=20)
                widget.var = var
            widget.grid(row=row, column=1, sticky=tk.W, padx=6, pady=4)
            self.param_widgets[pname] = widget
            row += 1

    def _parse_value(self, text: str):
        s = text.strip()
        if s == "":
            return None
        if s.lower() in ("true", "false"):
            return s.lower() == "true"
        try:
            if "." in s:
                return float(s)
            return int(s)
        except ValueError:
            return s

    def _collect_kwargs(self) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {}
        for name, widget in self.param_widgets.items():
            var = getattr(widget, "var", None)
            if var is None:
                continue
            val = var.get()
            if isinstance(var, tk.BooleanVar):
                kwargs[name] = bool(val)
            else:
                parsed = self._parse_value(val)
                if parsed is not None:
                    kwargs[name] = parsed
        return kwargs

    def _on_run(self):
        if hasattr(self, "_worker") and self._worker.is_alive():
            messagebox.showinfo("Busy", "An experiment is already running.")
            return
        name = self.exp_var.get()
        if not name:
            messagebox.showerror("Error", "Select an experiment.")
            return
        kwargs = self._collect_kwargs()
        self.status_var.set("Running...")
        self.run_btn.config(state=tk.DISABLED)
        self._append_log(f"\n=== Running {name} with {kwargs} ===\n")
        self._worker = threading.Thread(
            target=self._run_worker, args=(name, kwargs), daemon=True
        )
        self._worker.start()

    def _run_worker(self, name: str, kwargs: Dict[str, Any]):
        try:
            run_experiment(name, **kwargs)
            self.log_queue.put("\n=== Completed ===\n")
        except Exception as e:
            self.log_queue.put(f"\nError: {e}\n")
        finally:
            self.after(0, self._on_complete)

    def _on_complete(self):
        self.status_var.set("Idle")
        self.run_btn.config(state=tk.NORMAL)

    def _append_log(self, text: str):
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)

    def _poll_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self._append_log(msg)
        except queue.Empty:
            pass
        self.after(100, self._poll_log_queue)

    def destroy(self):
        sys.stdout = self._orig_stdout
        sys.stderr = self._orig_stderr
        super().destroy()


if __name__ == "__main__":
    app = ExperimentGUI()
    app.mainloop()
