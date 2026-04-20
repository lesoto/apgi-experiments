import tkinter as tk
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use("TkAgg")

# ==========================================
# APGI VISUAL IDENTITY & COLOR CONSTANTS
# ==========================================

APGI_BLUE = "#00B4FF"  # Threshold (Bt)
APGI_RED = "#FF3366"  # Interoceptive Precision (PI)
APGI_YELLOW = "#FFCC00"  # Prediction Error (|epsilon|)
APGI_GREEN = "#00CC99"  # Neuromodulator Tone
APGI_PURPLE = "#9966FF"  # Global Workspace / Ignition
APGI_DARK = "#2C3E50"  # Background / Structure
BG_MAIN = "#1A2634"  # App Background
TEXT_MAIN = "#E8F4FD"  # Main Text Color

PARAM_COLORS = {
    "threshold": APGI_BLUE,
    "precision": APGI_RED,
    "prediction_error": APGI_YELLOW,
    "neuromodulator": APGI_GREEN,
    "ignition": APGI_PURPLE,
}

APGI_RCPARAMS = {
    "figure.facecolor": BG_MAIN,
    "axes.facecolor": BG_MAIN,
    "axes.edgecolor": APGI_DARK,
    "axes.labelcolor": TEXT_MAIN,
    "xtick.color": TEXT_MAIN,
    "ytick.color": TEXT_MAIN,
    "text.color": TEXT_MAIN,
    "grid.color": APGI_DARK,
    "grid.alpha": 0.4,
    # Font settings (Standard matplotlib fallback to sans-serif if Inter is missing)
    "font.family": "sans-serif",
    "mathtext.fontset": "cm",
}

# Typography mappings for Tkinter
# Use system font fallbacks to avoid requiring font checking at module level
FONT_UI_BODY = ("Helvetica", 11)
FONT_UI_HEADER = ("Helvetica", 13, "bold")
FONT_WORDMARK = ("Helvetica", 18, "bold")
FONT_EQUATION = ("Courier", 12, "bold")
FONT_BADGE = ("Courier", 10)


# ==========================================
# GUI ARCHITECTURE: THREE-ZONE LAYOUT
# ==========================================


class APGIHeaderWidget(tk.Frame):
    """Header Zone: Provocative branding, live equation, and status."""

    def __init__(self, parent, app_name):
        super().__init__(parent, bg=APGI_DARK, height=60)
        self.pack_propagate(False)

        # 1. Wordmark & Subtitle
        brand_frame = tk.Frame(self, bg=APGI_DARK)
        brand_frame.pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            brand_frame, text="APGI", font=FONT_WORDMARK, fg=APGI_BLUE, bg=APGI_DARK
        ).pack(side=tk.LEFT)
        tk.Label(
            brand_frame, text=" | ", font=FONT_UI_HEADER, fg=TEXT_MAIN, bg=APGI_DARK
        ).pack(side=tk.LEFT)
        tk.Label(
            brand_frame, text=app_name, font=("Inter", 12), fg=TEXT_MAIN, bg=APGI_DARK
        ).pack(side=tk.LEFT)

        # 2. Live Equation Display (Π × |ε| > Bt)
        eq_frame = tk.Frame(self, bg=APGI_DARK)
        eq_frame.pack(side=tk.LEFT, expand=True)

        tk.Label(
            eq_frame, text="Π", font=FONT_EQUATION, fg=APGI_RED, bg=APGI_DARK
        ).pack(side=tk.LEFT)
        tk.Label(
            eq_frame, text=" × ", font=FONT_EQUATION, fg=TEXT_MAIN, bg=APGI_DARK
        ).pack(side=tk.LEFT)
        tk.Label(
            eq_frame, text="|ε|", font=FONT_EQUATION, fg=APGI_YELLOW, bg=APGI_DARK
        ).pack(side=tk.LEFT)

        self.eq_operator = tk.Label(
            eq_frame, text=" < ", font=FONT_EQUATION, fg=TEXT_MAIN, bg=APGI_DARK
        )
        self.eq_operator.pack(side=tk.LEFT)

        tk.Label(
            eq_frame, text="Bt", font=FONT_EQUATION, fg=APGI_BLUE, bg=APGI_DARK
        ).pack(side=tk.LEFT)

        # 3. Session Indicator & Parameter Badges
        status_frame = tk.Frame(self, bg=APGI_DARK)
        status_frame.pack(side=tk.RIGHT, padx=20, pady=10)

        # Session Dot
        self.session_canvas = tk.Canvas(
            status_frame, width=16, height=16, bg=APGI_DARK, highlightthickness=0
        )
        self.session_canvas.pack(side=tk.LEFT, padx=(0, 15))
        self.session_dot = self.session_canvas.create_oval(
            2, 2, 14, 14, fill="gray", outline=""
        )

        # Badges
        self.badges = {}
        for param, color, label in [
            ("bt", APGI_BLUE, "Bt"),
            ("pi", APGI_RED, "Π"),
            ("eps", APGI_YELLOW, "|ε|"),
            ("beta", APGI_GREEN, "β"),
        ]:
            f = tk.Frame(status_frame, bg=color, padx=1, pady=1)
            f.pack(side=tk.LEFT, padx=4)
            lbl = tk.Label(
                f, text=f"{label}: 0.0", font=FONT_BADGE, bg=BG_MAIN, fg=color, width=8
            )
            lbl.pack()
            self.badges[param] = lbl

    def update_status(self, data):
        """Update live equation status and parameter badges."""
        pi, eps, bt, beta = data["pi"], data["eps"], data["bt"], data["beta"]

        # Badges
        self.badges["pi"].config(text=f"Π: {pi:.2f}")
        self.badges["eps"].config(text=f"|ε|: {eps:.2f}")
        self.badges["bt"].config(text=f"Bt: {bt:.2f}")
        self.badges["beta"].config(text=f"β: {beta:.2f}")

        # Equation Logic
        is_ignition = (pi * eps) > bt
        self.eq_operator.config(
            text=" > " if is_ignition else " < ",
            fg=APGI_PURPLE if is_ignition else TEXT_MAIN,
        )

        # Session Indicator (Green for running, Purple for ignition)
        dot_color = APGI_PURPLE if is_ignition else APGI_GREEN
        self.session_canvas.itemconfig(self.session_dot, fill=dot_color)


class APGICanvas(tk.Frame):
    """Authoritative Zone: Embedded Matplotlib Visualization."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_MAIN)

        # Apply strict RCPARAMS
        plt.rcParams.update(APGI_RCPARAMS)

        self.fig = Figure(
            figsize=(8, 6), dpi=100, facecolor=APGI_RCPARAMS["figure.facecolor"]
        )
        self.axes = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Time series data history
        self.time_data = np.linspace(0, 10, 100)
        self.history = {
            "signal": np.zeros(100),
            "bt": np.zeros(100),
            "pi_x_eps": np.zeros(100),
        }
        self.t_offset = 0

    def update_plot(self, current_data: dict):
        """Clear and re-render the plot as mandated by the design pattern."""
        self.axes.cla()

        # Advance data
        self.t_offset += 0.1
        new_eps = current_data["eps"] + (
            np.sin(self.t_offset * 5) * 0.2 * current_data["beta"]
        )  # add noise based on beta
        new_signal = current_data["pi"] * abs(new_eps)

        self.history["signal"] = np.roll(self.history["signal"], -1)
        self.history["bt"] = np.roll(self.history["bt"], -1)
        self.history["pi_x_eps"] = np.roll(self.history["pi_x_eps"], -1)

        self.history["signal"][-1] = new_eps
        self.history["bt"][-1] = current_data["bt"]
        self.history["pi_x_eps"][-1] = new_signal

        self._render()

        # Mandatory citation watermark
        self.fig.text(
            0.01,
            0.01,
            "APGI Framework — Friston 2010; Barrett 2017; Dehaene 2014",
            fontsize=7,
            color="#4A5568",
            alpha=0.7,
        )
        self.canvas.draw()

    def _render(self):
        # Plot Threshold (Bt)
        self.axes.plot(
            self.time_data,
            self.history["bt"],
            color=PARAM_COLORS["threshold"],
            label="Threshold ($B_t$)",
            lw=2,
            linestyle="--",
        )

        # Plot Prediction Error Signal
        self.axes.plot(
            self.time_data,
            self.history["signal"],
            color=PARAM_COLORS["prediction_error"],
            alpha=0.5,
            label=r"Pred. Error ($|\epsilon|$)",
        )

        # Plot Integrated Signal
        self.axes.plot(
            self.time_data,
            self.history["pi_x_eps"],
            color=PARAM_COLORS["precision"],
            label=r"Integrated ($\Pi \times |\epsilon|$)",
            lw=2,
        )

        # Global Workspace Ignition Fill (Purple)
        self.axes.fill_between(
            self.time_data,
            self.history["bt"],
            self.history["pi_x_eps"],
            where=(self.history["pi_x_eps"] > self.history["bt"]),
            color=PARAM_COLORS["ignition"],
            alpha=0.3,
            label="Ignition Event",
        )

        self.axes.set_ylim(-0.5, 5.5)
        self.axes.set_xlim(0, 10)
        self.axes.set_title(
            "Active Inference & Global Workspace Dynamics",
            fontdict={"family": "sans-serif", "weight": "bold", "size": 12},
        )
        self.axes.set_ylabel("Amplitude")
        self.axes.set_xlabel("Time (s)")

        # Clean up borders
        self.axes.spines["top"].set_visible(False)
        self.axes.spines["right"].set_visible(False)
        self.axes.legend(
            loc="upper right",
            facecolor=BG_MAIN,
            edgecolor=APGI_DARK,
            labelcolor=TEXT_MAIN,
        )


class APGIControlPanel(tk.Frame):
    """Compassionate Zone: Sliders, controls, and configuration."""

    def __init__(self, parent):
        super().__init__(parent, bg=APGI_DARK)

        lbl = tk.Label(
            self,
            text="Control Panel",
            font=("Crimson Pro", 15, "bold"),
            fg=TEXT_MAIN,
            bg=APGI_DARK,
        )
        lbl.pack(pady=(20, 10), anchor="w", padx=20)

        # Dictionary to store Tk variables mapped to their values
        self.vars = {
            "pi": tk.DoubleVar(value=2.0),
            "eps": tk.DoubleVar(value=1.0),
            "bt": tk.DoubleVar(value=3.5),
            "beta": tk.DoubleVar(value=1.0),
        }

        # Build Sliders
        self._create_slider(
            "Interoceptive Precision (Π)",
            self.vars["pi"],
            PARAM_COLORS["precision"],
            0.1,
            5.0,
        )
        self._create_slider(
            "Prediction Error (|ε|)",
            self.vars["eps"],
            PARAM_COLORS["prediction_error"],
            0.0,
            3.0,
        )
        self._create_slider(
            "Threshold (Bt)", self.vars["bt"], PARAM_COLORS["threshold"], 0.5, 5.0
        )
        self._create_slider(
            "Neuromodulator Tone (β)",
            self.vars["beta"],
            PARAM_COLORS["neuromodulator"],
            0.1,
            2.0,
        )

        # Protocol Button
        btn = tk.Button(
            self,
            text="Execute Protocol Queue",
            font=FONT_UI_BODY,
            bg=APGI_DARK,
            fg=TEXT_MAIN,
            activebackground=BG_MAIN,
            activeforeground=TEXT_MAIN,
            relief="ridge",
            bd=2,
        )
        btn.pack(fill=tk.X, padx=20, pady=30)

    def _create_slider(self, label_text, variable, color, from_, to):
        container = tk.Frame(self, bg=APGI_DARK)
        container.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            container, text=label_text, font=FONT_UI_BODY, fg=TEXT_MAIN, bg=APGI_DARK
        ).pack(anchor="w")

        slider = tk.Scale(
            container,
            variable=variable,
            from_=from_,
            to=to,
            resolution=0.01,
            orient="horizontal",
            bg=APGI_DARK,
            fg=TEXT_MAIN,
            troughcolor=BG_MAIN,
            highlightthickness=0,
            activebackground=color,
        )
        slider.pack(fill=tk.X)

    def get_current_data(self):
        return {k: v.get() for k, v in self.vars.items()}


class APGIMainWindow(tk.Tk):
    """Main Application coordinating the architecture."""

    def __init__(self):
        super().__init__()
        self.title("APGI Research Suite")
        self.geometry("1200x800")
        self.configure(bg=BG_MAIN)

        # 1. Header
        self.header = APGIHeaderWidget(self, "Research Suite")
        self.header.pack(side=tk.TOP, fill=tk.X)

        # 2. Body Splitter (PanedWindow for ratio adjustment)
        self.splitter = tk.PanedWindow(
            self, orient=tk.HORIZONTAL, bg=BG_MAIN, sashwidth=4, sashpad=2
        )
        self.splitter.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas (65%)
        self.canvas_panel = APGICanvas(self.splitter)
        self.splitter.add(self.canvas_panel, minsize=600, stretch="always")

        # Control Panel (35%)
        self.control_panel = APGIControlPanel(self.splitter)
        self.splitter.add(self.control_panel, minsize=300, stretch="never")

        # Initial Layout Enforcement (65/35)
        self.update_idletasks()
        total_width = self.winfo_width()
        self.splitter.sash_place(0, int(total_width * 0.65), 0)

        # 3. Start Application Loop (10Hz = 100ms)
        self._update_loop()

    def _update_loop(self):
        """Central loop driving 10Hz updates as specified."""
        # 1. Gather current state from controls
        current_params = self.control_panel.get_current_data()

        # 2. Update Header elements (Equation + Badges)
        self.header.update_status(current_params)

        # 3. Update Embedded Canvas
        self.canvas_panel.update_plot(current_params)

        # 4. Schedule next tick
        self.after(100, self._update_loop)


if __name__ == "__main__":
    app = APGIMainWindow()
    app.mainloop()
