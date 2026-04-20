import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np

# ==================== APGI COLOR SYSTEM ====================
APGI_BLUE = "#00B4FF"  # Threshold (Bt)
APGI_RED = "#FF3366"  # Precision (PI)
APGI_YELLOW = "#FFCC00"  # Prediction Error (|ε|)
APGI_GREEN = "#00CC99"  # Neuromodulator
APGI_PURPLE = "#9966FF"  # Global Workspace / Ignition
APGI_DARK = "#2C3E50"  # Background / Structure
APGI_BG = "#1A2634"  # Main background
APGI_TEXT = "#E8F4FD"

PARAM_COLORS = {
    "threshold": APGI_BLUE,
    "precision": APGI_RED,
    "prediction_error": APGI_YELLOW,
    "neuromodulator": APGI_GREEN,
    "ignition": APGI_PURPLE,
}


# ==================== APGI GUI CLASS ====================
class APGITinkerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("APGI — Active Predictive Global Ignition")
        self.root.geometry("1400x900")
        self.root.configure(bg=APGI_BG)

        # Fonts (system fallbacks - Inter/Crimson recommended)
        self.font_header = (
            ("Inter", 18, "bold")
            if "Inter" in tk.font.families()
            else ("Helvetica", 18, "bold")
        )
        self.font_body = ("Inter", 11)
        self.font_mono = (
            ("JetBrains Mono", 10)
            if "JetBrains Mono" in tk.font.families()
            else ("Courier", 10)
        )
        self.font_section = (
            ("Crimson Pro", 15, "bold")
            if "Crimson Pro" in tk.font.families()
            else ("Helvetica", 15, "bold")
        )

        self.setup_styles()
        self.build_ui()
        self.start_live_updates()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=APGI_DARK)
        style.configure(
            "TLabel", background=APGI_DARK, foreground=APGI_TEXT, font=self.font_body
        )
        style.configure(
            "Header.TLabel",
            background=APGI_DARK,
            foreground=APGI_BLUE,
            font=self.font_header,
        )
        style.configure(
            "Badge.TLabel",
            background=APGI_DARK,
            foreground=APGI_TEXT,
            font=self.font_mono,
            padding=6,
        )
        style.configure("TButton", background=APGI_BLUE, foreground="white")

    def build_ui(self):
        # ===================== HEADER ZONE =====================
        header = tk.Frame(self.root, bg=APGI_DARK, height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # APGI Wordmark
        tk.Label(
            header, text="APGI", font=self.font_header, bg=APGI_DARK, fg=APGI_BLUE
        ).pack(side="left", padx=20)

        # Subtitle
        tk.Label(
            header,
            text="Neuroscape Tinker",
            font=("Inter", 12),
            bg=APGI_DARK,
            fg=APGI_TEXT,
        ).pack(side="left", padx=5)

        # Live Equation
        self.equation_label = tk.Label(
            header,
            text="Π × |ε| > Bt",
            font=("JetBrains Mono", 13, "bold"),
            bg=APGI_DARK,
            fg=APGI_PURPLE,
        )
        self.equation_label.pack(side="left", padx=30)

        # Parameter Badges
        badge_frame = tk.Frame(header, bg=APGI_DARK)
        badge_frame.pack(side="right", padx=20)

        self.badges = {}
        for param, color in PARAM_COLORS.items():
            if param == "ignition":
                continue
            frame = tk.Frame(badge_frame, bg=APGI_DARK)
            frame.pack(side="left", padx=8)
            tk.Label(
                frame,
                text=param[:3].upper(),
                font=self.font_mono,
                bg=APGI_DARK,
                fg=color,
            ).pack(side="left")
            lbl = tk.Label(
                frame,
                text="0.00",
                font=self.font_mono,
                bg=APGI_DARK,
                fg=APGI_TEXT,
                width=6,
            )
            lbl.pack(side="left")
            self.badges[param] = lbl

        # Session Indicator
        self.session_frame = tk.Frame(header, bg=APGI_DARK)
        self.session_frame.pack(side="right", padx=20)
        self.dot = tk.Label(
            self.session_frame, text="●", font=("Arial", 16), bg=APGI_DARK, fg="gray"
        )
        self.dot.pack(side="left")
        self.session_label = tk.Label(
            self.session_frame,
            text="IDLE",
            font=self.font_mono,
            bg=APGI_DARK,
            fg=APGI_TEXT,
        )
        self.session_label.pack(side="left", padx=5)

        # ===================== MAIN BODY =====================
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Canvas (65%)
        canvas_frame = tk.Frame(paned, bg=APGI_BG)
        paned.add(canvas_frame, weight=65)

        # Matplotlib Figure
        plt.rcParams.update(
            {
                "figure.facecolor": APGI_BG,
                "axes.facecolor": APGI_BG,
                "axes.edgecolor": APGI_DARK,
                "axes.labelcolor": APGI_TEXT,
                "xtick.color": APGI_TEXT,
                "ytick.color": APGI_TEXT,
                "text.color": APGI_TEXT,
                "grid.color": APGI_DARK,
                "grid.alpha": 0.4,
                "font.family": "sans-serif",
            }
        )

        self.fig = Figure(figsize=(9, 7), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, canvas_frame)
        toolbar.update()

        # Right: Control Panel (35%)
        control_frame = tk.Frame(paned, bg=APGI_DARK, width=420)
        paned.add(control_frame, weight=35)

        # Sliders
        self.create_control_panel(control_frame)

        # Initial Plot
        self.update_plot()

    def create_control_panel(self, parent):
        tk.Label(
            parent,
            text="NEUROMODULATORY CONTROLS",
            font=self.font_section,
            bg=APGI_DARK,
            fg=APGI_PURPLE,
        ).pack(pady=(20, 10))

        # Threshold (Bt) - Blue
        self.create_slider(
            parent, "Threshold (Bt)", "threshold", 0.0, 1.0, 0.65, APGI_BLUE
        )

        # Precision (PI) - Red
        self.create_slider(
            parent, "Precision (PI)", "precision", 0.0, 1.0, 0.82, APGI_RED
        )

        # Prediction Error (|ε|) - Yellow
        self.create_slider(
            parent, "Pred. Error (|ε|)", "prediction_error", 0.0, 0.5, 0.12, APGI_YELLOW
        )

        # Neuromodulator Tone - Green
        self.create_slider(
            parent, "Neuromodulator (β)", "neuromodulator", 0.0, 1.0, 0.45, APGI_GREEN
        )

        # Ignition Trigger
        tk.Button(
            parent,
            text="TRIGGER IGNITION",
            bg=APGI_PURPLE,
            fg="white",
            font=("Inter", 11, "bold"),
            command=self.trigger_ignition,
        ).pack(pady=20, ipadx=20, ipady=8)

        # Live Values
        self.live_values = {}
        for param in ["threshold", "precision", "prediction_error", "neuromodulator"]:
            frame = tk.Frame(parent, bg=APGI_DARK)
            frame.pack(fill="x", padx=20, pady=4)
            tk.Label(
                frame,
                text=param.replace("_", " ").title(),
                bg=APGI_DARK,
                fg=PARAM_COLORS[param],
                width=20,
                anchor="w",
            ).pack(side="left")
            val = tk.Label(
                frame, text="0.00", bg=APGI_DARK, fg=APGI_TEXT, font=self.font_mono
            )
            val.pack(side="right")
            self.live_values[param] = val

    def create_slider(self, parent, label, param_key, minv, maxv, default, color):
        frame = tk.Frame(parent, bg=APGI_DARK)
        frame.pack(fill="x", padx=20, pady=8)

        tk.Label(
            frame, text=label, bg=APGI_DARK, fg=APGI_TEXT, font=self.font_body
        ).pack(anchor="w")

        slider = ttk.Scale(
            frame,
            from_=minv,
            to=maxv,
            value=default,
            orient="horizontal",
            style="Horizontal.TScale",
            command=lambda v: self.on_slider_change(param_key, v),
        )
        slider.pack(fill="x", pady=4)

        setattr(self, f"slider_{param_key}", slider)
        setattr(self, f"value_{param_key}", tk.DoubleVar(value=default))

    def on_slider_change(self, param, val):
        var = getattr(self, f"value_{param}")
        if hasattr(var, "set"):
            var.set(float(val))
        else:
            setattr(self, f"value_{param}", float(val))
        self.live_values[param].config(text=f"{float(val):.3f}")
        self.update_badges()
        self.update_plot()

    def update_badges(self):
        for param in self.badges:
            val = getattr(self, f"value_{param}")
            if hasattr(val, "get"):
                val = val.get()
            self.badges[param].config(text=f"{val:.2f}")

    def update_plot(self):
        self.ax.clear()

        # Simulate Free Energy / Surprise landscape
        x = np.linspace(0, 10, 400)
        bt = getattr(self, "value_threshold", tk.DoubleVar(value=0.65)).get()
        pi = getattr(self, "value_precision", tk.DoubleVar(value=0.82)).get()
        eps = getattr(self, "value_prediction_error", tk.DoubleVar(value=0.12)).get()

        surprise = (
            np.exp(-((x - 5) ** 2) / (0.5 + eps * 10)) * (1.0 - pi) + np.sin(x) * 0.3
        )

        self.ax.plot(
            x, surprise, color=APGI_YELLOW, linewidth=2.5, label="Surprise / |ε|"
        )
        self.ax.axhline(
            bt, color=APGI_BLUE, linestyle="--", linewidth=2, label="Bt Threshold"
        )
        self.ax.fill_between(
            x,
            surprise,
            bt,
            where=(surprise > bt),
            color=APGI_PURPLE,
            alpha=0.3,
            label="Ignition Region",
        )

        self.ax.set_title(
            "Active Inference Landscape — Global Workspace Ignition",
            color=APGI_TEXT,
            fontsize=14,
        )
        self.ax.set_xlabel("Time / Evidence Accumulation", color=APGI_TEXT)
        self.ax.set_ylabel("Free Energy / Prediction Error", color=APGI_TEXT)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(facecolor=APGI_BG, edgecolor=APGI_DARK)

        # Watermark
        self.fig.text(
            0.02,
            0.02,
            "APGI Framework • Friston 2010 | Barrett 2017 | Dehaene 2014",
            fontsize=7,
            color="#4A5568",
            alpha=0.7,
        )

        self.canvas.draw()

    def trigger_ignition(self):
        self.dot.config(fg=APGI_PURPLE)
        self.session_label.config(text="IGNITION!", fg=APGI_PURPLE)

        # Flash effect
        original = self.ax.get_facecolor()
        self.ax.set_facecolor(APGI_PURPLE)
        self.canvas.draw()
        self.root.after(
            300, lambda: self.ax.set_facecolor(original) or self.canvas.draw()
        )

        self.root.after(
            1500,
            lambda: self.dot.config(fg="gray")
            or self.session_label.config(text="IDLE", fg=APGI_TEXT),
        )

    def start_live_updates(self):
        # Use root.after() instead of threading to avoid GIL issues
        self._live_update_loop()

    def _live_update_loop(self):
        # Simulate slow drift
        current_eps = getattr(self, "value_prediction_error", tk.DoubleVar(value=0.12))
        if hasattr(current_eps, "get"):
            current_eps = current_eps.get()
        new_eps = max(0.0, min(0.5, current_eps + np.random.normal(0, 0.008)))
        eps_var = getattr(self, "value_prediction_error")
        if hasattr(eps_var, "set"):
            eps_var.set(new_eps)
        else:
            setattr(self, "value_prediction_error", new_eps)

        if hasattr(self, "live_values"):
            try:
                self.live_values["prediction_error"].config(text=f"{new_eps:.3f}")
                self.update_badges()
                self.update_plot()
            except Exception:
                pass

        # Schedule next update
        self.root.after(800, self._live_update_loop)

    def run(self):
        self.root.mainloop()


# ==================== RUN THE APP ====================
if __name__ == "__main__":
    app = APGITinkerApp()
    app.run()
