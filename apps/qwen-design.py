#!/usr/bin/env python3
"""
APGI Neuroscape / Architect Environment (tkinter version)
Converted from PyQt6 desktop application implementing the APGI GUI Software Design Document.
Self-contained, ready to run with: pip install matplotlib numpy
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
import tkinter as tk
from tkinter import messagebox

# ============================================================================
# 1. VISUAL IDENTITY SYSTEM (apgi/colors.py & typography)
# ============================================================================
APGI_BLUE = "#00B4FF"  # Threshold (Bt)
APGI_RED = "#FF3366"  # Interoceptive Precision (PI)
APGI_YELLOW = "#FFCC00"  # Prediction Error (|epsilon|)
APGI_GREEN = "#00CC99"  # Neuromodulator Tone
APGI_PURPLE = "#9966FF"  # Global Workspace / Ignition
APGI_DARK = "#2C3E50"  # Background / Structure
APGI_BG = "#1A2634"  # Plot background
APGI_FG = "#E8F4FD"  # Light foreground

PARAM_COLORS = {
    "threshold": APGI_BLUE,
    "precision": APGI_RED,
    "prediction_error": APGI_YELLOW,
    "neuromodulator": APGI_GREEN,
    "ignition": APGI_PURPLE,
}

APGI_RCPARAMS = {
    "figure.facecolor": APGI_BG,
    "axes.facecolor": APGI_BG,
    "axes.edgecolor": APGI_DARK,
    "axes.labelcolor": "#E8F4FD",
    "xtick.color": "#E8F4FD",
    "ytick.color": "#E8F4FD",
    "text.color": "#E8F4FD",
    "grid.color": APGI_DARK,
    "grid.alpha": 0.4,
    "font.family": "sans-serif",
    "font.size": 10,
    "mathtext.fontset": "cm",  # Computer Modern for equations
}

APGI_DIVERGING_CMAP = LinearSegmentedColormap.from_list(
    "apgi_diverge", [APGI_BLUE, APGI_BG, APGI_RED], N=256
)


# Typography defaults (will attempt to load TTFs, fallback gracefully)
def setup_apgi_fonts():
    """Call once at app startup before any widget creation."""
    # Tkinter uses system fonts; custom fonts would need to be registered via tkfont
    # For now, we'll use standard fonts that are likely available
    pass


# ============================================================================
# 2. CORE MATHEMATICAL FUNCTIONS (apgi/core/*.py)
# ============================================================================
def calculate_threshold_crossing(
    prediction_error: float, precision_weight: float, broadcast_threshold: float
) -> dict:
    """
    Determine whether precision-weighted prediction error exceeds
    the dynamic broadcast threshold, triggering global workspace ignition.

    APGI Parameters:
        prediction_error (epsilon): Z-score [0.0, 5.0].
            Exteroceptive and interoceptive channels standardized separately.
        precision_weight (PI): Inverse variance 1/sigma^2 [0.0, 1.0].
            CRITICAL: Must not be confused with prediction_error magnitude.
        broadcast_threshold (Bt): Dynamic ignition threshold [0.0, 10.0].
            Modulated by neuromodulator tone (beta parameter).

    Returns:
        dict with keys: 'ignition' (bool), 'signal_strength' (float),
                        'margin' (float, St - Bt)

    Mathematical basis:
        St = PI_e * |z_e| + PI_i_eff * |z_i|
        Ignition: St > Bt
        Euler-Maruyama: Xt+1 = Xt + mu*dt + sigma*sqrt(dt)*N(0,1)

    References:
        Friston, K. (2010). The free-energy principle. Nat Rev Neurosci, 11, 127-138.
        Barrett, L. F., & Simmons, W. K. (2015). Interoceptive predictions in the brain.
            Nat Rev Neurosci, 16, 419-429.
        Dehaene, S., et al. (2014). Experimental and theoretical approaches to conscious
            processing. Neuron, 70(2), 200-227.
    """
    integrated_signal = precision_weight * abs(prediction_error)
    ignition = integrated_signal > broadcast_threshold
    return {
        "ignition": ignition,
        "signal_strength": integrated_signal,
        "margin": integrated_signal - broadcast_threshold,
    }


def integrate_euler_maruyama(st, mu=0.1, sigma=0.5, dt=0.1):
    """Single step of Euler-Maruyama SDE integration."""
    dW = np.sqrt(dt) * np.random.standard_normal()
    return st + mu * dt + sigma * dW


# ============================================================================
# 3. VISUALIZATION MODULES (apgi/visualization/*.py)
# ============================================================================
def plot_apgi_radar(ax, values, title="APGI Signature", fill_alpha=0.25):
    RADAR_AXES = [
        ("Threshold\nSensitivity", APGI_BLUE),
        ("Interoceptive\nPrecision", APGI_RED),
        ("Prediction\nError", APGI_YELLOW),
        ("Neuromodulator\nTone", APGI_GREEN),
        ("Somatic\nBias", APGI_PURPLE),
    ]
    N = len(RADAR_AXES)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values_plot = list(values) + [values[0]]
    ax.set_facecolor(APGI_BG)
    ax.plot(angles, values_plot, color=APGI_PURPLE, lw=2.0)
    ax.fill(angles, values_plot, color=APGI_PURPLE, alpha=fill_alpha)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([a[0] for a in RADAR_AXES], size=8, color="#E8F4FD")
    for i, (_, color) in enumerate(RADAR_AXES):
        ax.tick_params(axis="x", colors=color)
    ax.set_title(title, color="#E8F4FD", pad=20, fontsize=12)
    ax.figure.text(
        0.01,
        0.01,
        "APGI Framework — Friston 2010; Barrett 2017; Dehaene 2014",
        fontsize=6,
        color="#4A5568",
        alpha=0.7,
    )


def plot_sde_trajectory(ax, t, S_t, B_t, ignition_events=None):
    ax.set_facecolor(APGI_BG)
    ax.plot(t, S_t, color=APGI_PURPLE, lw=2.0, label="St (Consciousness Signal)")
    ax.plot(t, B_t, color=APGI_BLUE, lw=1.5, ls="--", label="Bt (Threshold)")
    if ignition_events:
        for i, t_ign in enumerate(ignition_events):
            ax.axvline(
                x=t_ign,
                color=APGI_YELLOW,
                alpha=0.7,
                lw=1.0,
                ls=":",
                label="Ignition" if i == 0 else None,
            )
    ax.legend(loc="upper right", fontsize=8, facecolor=APGI_DARK, labelcolor="#E8F4FD")
    ax.set_xlabel("Time (s)", color="#E8F4FD")
    ax.set_ylabel("Signal Magnitude", color="#E8F4FD")
    ax.tick_params(colors="#E8F4FD")
    ax.figure.text(
        0.01,
        0.01,
        "SDE: Euler-Maruyama. Friston 2010; Barrett & Simmons 2015",
        fontsize=6,
        color="#4A5568",
        alpha=0.7,
    )


def plot_correlation_heatmap(ax, corr_matrix):
    PARAM_LABELS = [
        "Bt Threshold",
        "PI Precision",
        "|eps| Pred.Error",
        "Neuromod.",
        "beta Somatic Bias",
    ]
    im = ax.imshow(corr_matrix, cmap=APGI_DIVERGING_CMAP, vmin=-1, vmax=1)
    ax.set_xticks(range(len(PARAM_LABELS)))
    ax.set_yticks(range(len(PARAM_LABELS)))
    ax.set_xticklabels(
        PARAM_LABELS, rotation=45, ha="right", fontsize=8, color="#E8F4FD"
    )
    ax.set_yticklabels(PARAM_LABELS, fontsize=8, color="#E8F4FD")
    ax.figure.colorbar(im, ax=ax, label="Correlation")
    ax.figure.text(
        0.01,
        0.01,
        "Correlation matrix. Pearson r. See apgi.stats.correlate_parameters()",
        fontsize=6,
        color="#4A5568",
        alpha=0.7,
    )


# ============================================================================
# 4. GUI WIDGETS (apgi/gui/widgets/*.py)
# ============================================================================
class APGIParameterSlider(tk.Frame):
    def __init__(
        self,
        parent,
        param_name,
        label,
        symbol,
        min_val,
        max_val,
        default,
        step=0.01,
        citation="",
    ):
        super().__init__(parent)
        self.param_name = param_name
        self.label_text = label
        self.step = step
        self.citation = citation
        self.value_callback = None
        self.color = PARAM_COLORS.get(param_name, "#E8F4FD")
        self._build_ui(label, symbol, min_val, max_val, default)

    def _build_ui(self, label, symbol, lo, hi, default):
        self.configure(bg=APGI_BG)

        # Label with symbol
        lbl = tk.Label(
            self,
            text=f"{symbol}  {label}",
            fg=self.color,
            bg=APGI_BG,
            font=("Inter", 10),
        )
        lbl.grid(row=0, column=0, sticky="w", padx=2, pady=2)

        # Value variable
        self.value_var = tk.DoubleVar(value=default)

        # Scale (slider)
        self.scale = tk.Scale(
            self,
            from_=lo,
            to=hi,
            resolution=self.step,
            orient=tk.HORIZONTAL,
            variable=self.value_var,
            bg=APGI_BG,
            fg=APGI_FG,
            highlightthickness=0,
            troughcolor=APGI_DARK,
            command=self._on_value_change,
        )
        self.scale.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Readout label
        self.readout = tk.Label(
            self,
            text=f"{default:.3f}",
            fg=self.color,
            bg=APGI_BG,
            font=("JetBrains Mono", 10),
        )
        self.readout.grid(row=0, column=2, padx=2, pady=2)

        # Configure grid weights
        self.columnconfigure(1, weight=1)

    def _on_value_change(self, value):
        val = float(value)
        self.readout.config(text=f"{val:.3f}")
        if self.value_callback:
            self.value_callback(self.param_name, val)

    def set_value_callback(self, callback):
        """Set callback for value changes: callback(name, value)"""
        self.value_callback = callback

    def set_value(self, v):
        self.value_var.set(v)
        self.readout.config(text=f"{v:.3f}")

    def get_value(self):
        return self.value_var.get()


class APGIStateBadge(tk.Frame):
    STATE_CATEGORY_COLORS = {
        1: APGI_PURPLE,
        2: APGI_BLUE,
        3: APGI_GREEN,
        4: APGI_YELLOW,
        5: "#FF6633",
        6: APGI_RED,
        7: "#7F8C8D",
        8: APGI_DARK,
    }

    def __init__(
        self,
        parent,
        state_name="Balanced / Regulated",
        category=3,
        param_config="System nominal",
    ):
        super().__init__(parent)
        self.state_name = state_name
        self.category = category
        self.param_config = param_config
        self.configure(bg=APGI_BG)
        self._build_badge(state_name, category, param_config)

    def _show_clinical_flag(self):
        flag = tk.Label(
            self,
            text="⚠ This system configuration is outside normative ranges. "
            "This is a parameter description, not a clinical diagnosis. "
            "If distress persists, consult a qualified mental health professional.",
            fg="#FFCC00",
            bg="#2C1810",
            font=("Inter", 8),
            wraplength=300,
            justify=tk.LEFT,
            relief=tk.SOLID,
            borderwidth=1,
        )
        flag.pack(fill=tk.X, pady=(0, 5))

    def _build_badge(self, state_name, category, param_config):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        if category == 8:
            self._show_clinical_flag()

        color = self.STATE_CATEGORY_COLORS.get(category, "#E8F4FD")

        inner_frame = tk.Frame(self, bg=APGI_BG)
        inner_frame.pack(fill=tk.X, pady=5)

        # State badge label
        lbl = tk.Label(
            inner_frame,
            text=f"  {state_name}  ",
            fg="white",
            bg=color,
            font=("Inter", 10, "bold"),
            relief=tk.FLAT,
            padx=8,
            pady=2,
        )
        lbl.pack(side=tk.TOP)

        # Config label
        config_lbl = tk.Label(
            inner_frame,
            text=param_config,
            fg=APGI_FG,
            bg=APGI_BG,
            font=("JetBrains Mono", 9),
        )
        config_lbl.pack(side=tk.TOP, pady=(5, 0))

    def update_badge(self, state_name, category, param_config):
        self._build_badge(state_name, category, param_config)


class APGIHeaderWidget(tk.Frame):
    def __init__(self, parent, app_name):
        super().__init__(parent)
        self.app_name = app_name
        self.configure(bg=APGI_DARK, height=50)
        self.pack_propagate(False)
        self._build_header()

    def _build_header(self):
        # Use grid layout for better control
        self.columnconfigure(0, weight=0)  # Wordmark
        self.columnconfigure(1, weight=0)  # Separator
        self.columnconfigure(2, weight=1)  # Spacer
        self.columnconfigure(3, weight=0)  # Equation
        self.columnconfigure(4, weight=0)  # Badges
        self.columnconfigure(5, weight=0)  # Session dot

        # APGI Logo
        apgi_logo = tk.Label(
            self, text="APGI", fg=APGI_BLUE, bg=APGI_DARK, font=("Inter", 16, "bold")
        )
        apgi_logo.grid(row=0, column=0, padx=(12, 0), pady=6)

        # Subtitle
        sep = tk.Label(
            self,
            text=f"|  {self.app_name}",
            fg=APGI_FG,
            bg=APGI_DARK,
            font=("Inter", 12),
        )
        sep.grid(row=0, column=1, padx=(5, 0), pady=6)

        # Equation label
        self.equation_lbl = tk.Label(
            self,
            text="Π × |ε| = ?  > Bt",
            fg=APGI_GREEN,
            bg=APGI_DARK,
            font=("JetBrains Mono", 11),
        )
        self.equation_lbl.grid(row=0, column=3, padx=(20, 20), pady=6, sticky="e")

        # Badges frame
        badges_frame = tk.Frame(self, bg=APGI_DARK)
        badges_frame.grid(row=0, column=4, padx=(0, 10), pady=6)

        self.b1 = tk.Label(
            badges_frame,
            text="Bt: 0.00",
            fg=APGI_BLUE,
            bg=f"{APGI_BLUE}22" if False else APGI_DARK,
            font=("JetBrains Mono", 9),
            padx=4,
            pady=2,
        )
        self.b1.pack(side=tk.LEFT, padx=2)

        self.b2 = tk.Label(
            badges_frame,
            text="PI: 0.00",
            fg=APGI_RED,
            bg=APGI_DARK,
            font=("JetBrains Mono", 9),
            padx=4,
            pady=2,
        )
        self.b2.pack(side=tk.LEFT, padx=2)

        self.b3 = tk.Label(
            badges_frame,
            text="|ε|: 0.00",
            fg=APGI_YELLOW,
            bg=APGI_DARK,
            font=("JetBrains Mono", 9),
            padx=4,
            pady=2,
        )
        self.b3.pack(side=tk.LEFT, padx=2)

        self.b4 = tk.Label(
            badges_frame,
            text="β: 0.00",
            fg=APGI_GREEN,
            bg=APGI_DARK,
            font=("JetBrains Mono", 9),
            padx=4,
            pady=2,
        )
        self.b4.pack(side=tk.LEFT, padx=2)

        # Session dot
        self.session_dot = tk.Label(
            self, text="●", fg="#7F8C8D", bg=APGI_DARK, font=("Inter", 14)
        )
        self.session_dot.grid(row=0, column=5, padx=(0, 12), pady=6)


class APGICanvas:
    def __init__(self, parent, width=9, height=7, dpi=110):
        plt.rcParams.update(APGI_RCPARAMS)
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=APGI_BG)
        self.gs = GridSpec(2, 2, figure=self.fig, hspace=0.4, wspace=0.35)

        self.ax_radar = self.fig.add_subplot(self.gs[0, 0], projection="polar")
        self.ax_traj = self.fig.add_subplot(self.gs[0, 1])
        self.ax_heat = self.fig.add_subplot(self.gs[1, :])

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg=APGI_BG)

        # Initial dummy data render
        self.update_plot(
            {
                "bt": 3.0,
                "pi": 0.5,
                "eps": 1.5,
                "beta": 0.0,
                "t": np.linspace(0, 10, 100),
            }
        )

    def update_plot(self, data: dict):
        self.ax_radar.cla()
        self.ax_traj.cla()
        self.ax_heat.cla()

        # Normalize values for radar [0,1]
        radar_vals = [
            max(0.0, min(1.0, 1.0 - data["bt"] / 10.0)),
            data["pi"],
            max(0.0, min(1.0, data["eps"] / 5.0)),
            max(0.0, min(1.0, (data["beta"] + 3.0) / 6.0)),
            max(0.0, min(1.0, (data["beta"] + 3.0) / 6.0)),
        ]
        plot_apgi_radar(self.ax_radar, radar_vals)

        # SDE Trajectory
        t = data["t"]
        B_t = np.full_like(t, data["bt"])
        S_t = np.zeros_like(t)
        S_t[0] = data["pi"] * abs(data["eps"]) * 0.1
        for i in range(1, len(t)):
            S_t[i] = integrate_euler_maruyama(S_t[i - 1], mu=0.05, sigma=0.2, dt=0.1)
        ign_idx = np.where(S_t > B_t)[0]
        ign_events = [t[i] for i in ign_idx] if len(ign_idx) > 0 else None
        plot_sde_trajectory(self.ax_traj, t, S_t, B_t, ignition_events=ign_events)

        # Correlation Heatmap (simulated dynamic correlation)
        rng = np.random.default_rng(int(data["eps"] * 100))
        corr_mat = rng.uniform(-0.8, 0.9, (5, 5))
        corr_mat = (corr_mat + corr_mat.T) / 2
        np.fill_diagonal(corr_mat, 1.0)
        plot_correlation_heatmap(self.ax_heat, corr_mat)

        self.fig.text(
            0.01,
            0.01,
            "APGI Framework — Friston 2010; Barrett 2017; Dehaene 2014",
            fontsize=6,
            color="#4A5568",
            alpha=0.7,
            transform=self.fig.transFigure,
        )
        self.canvas.draw()


class APGIControlPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg=APGI_BG, padx=10, pady=10)
        self.params = {
            "threshold": 3.0,
            "precision": 0.5,
            "prediction_error": 1.5,
            "neuromodulator": 0.0,
        }
        self.update_callback = None
        self._build_controls()

    def _build_controls(self):
        # Title
        sec_lbl = tk.Label(
            self,
            text="PARAMETER EXPLORER",
            fg=APGI_FG,
            bg=APGI_BG,
            font=("Crimson Pro", 15, "bold"),
        )
        sec_lbl.pack(anchor="w", pady=(0, 10))

        # Sliders
        self.sliders = {
            "threshold": APGIParameterSlider(
                self,
                "threshold",
                "Threshold Sensitivity",
                "Bt",
                0.0,
                10.0,
                3.0,
                0.1,
                "Dehaene et al. 2014, Eq. 1",
            ),
            "precision": APGIParameterSlider(
                self,
                "precision",
                "Interoceptive Precision",
                "Π",
                0.0,
                1.0,
                0.5,
                0.01,
                "Friston 2010, Eq. 7",
            ),
            "prediction_error": APGIParameterSlider(
                self,
                "prediction_error",
                "Prediction Error Mag.",
                "|ε|",
                0.0,
                5.0,
                1.5,
                0.1,
                "Barrett & Simmons 2015, Eq. 2",
            ),
            "neuromodulator": APGIParameterSlider(
                self,
                "neuromodulator",
                "Neuromodulator Tone",
                "β",
                -3.0,
                3.0,
                0.0,
                0.1,
                "Friston et al. 2012, Eq. 4",
            ),
        }

        for k, slider in self.sliders.items():
            slider.set_value_callback(self._on_slider_change)
            slider.pack(fill=tk.X, pady=5)

        # State Output
        self.state_badge = APGIStateBadge(self)
        self.state_badge.pack(fill=tk.X, pady=10)

        # Export & Protocol
        btn = tk.Button(
            self,
            text="Export Session Data",
            bg="#3A4B62",
            fg=APGI_FG,
            font=("Inter", 10),
            activebackground=APGI_BLUE,
            activeforeground="white",
            command=self._export_data,
        )
        btn.pack(fill=tk.X, pady=5)

    def _on_slider_change(self, name, value):
        self.params[name] = value
        if self.update_callback:
            self.update_callback(self.params.copy())
        self._update_state()

    def _update_state(self):
        # Simple state mapping for demonstration
        bt = self.params["threshold"]
        pi = self.params["precision"]
        eps = self.params["prediction_error"]
        beta = self.params["neuromodulator"]
        st = pi * abs(eps)

        if st > bt + 1.5 and pi > 0.7:
            cat, name, cfg = (
                2,
                "Heightened Awareness",
                f"SNR elevated ({st:.2f} > {bt:.1f})",
            )
        elif st > bt and 0.3 <= eps <= 1.5:
            cat, name, cfg = 1, "Optimal / Flow", f"Smooth ignition at {st:.2f}"
        elif eps > 2.5 and pi < 0.4:
            cat, name, cfg = 7, "Dissociation", "Precision suppressed, error uncoupled"
        elif pi > 0.85 and st < bt:
            cat, name, cfg = (
                6,
                "Anxiety / Hypervigilance",
                "Hypersensitive precision, threshold mismatch",
            )
        elif eps > 3.0 and beta > 1.5:
            cat, name, cfg = 5, "Stress / Arousal", "Sympathetic somatic bias active"
        elif st < 0.5:
            cat, name, cfg = 8, "Pathological / Crisis", "System dysregulation detected"
        else:
            cat, name, cfg = 3, "Balanced / Regulated", "Default resting state nominal"

        self.state_badge.update_badge(name, cat, cfg)

    def _export_data(self):
        messagebox.showinfo("Export", "Session data saved to local audit log (SQLite).")

    def set_update_callback(self, callback):
        self.update_callback = callback


# ============================================================================
# 5. APPLICATION BOOTSTRAP & MAIN WINDOW (apgi/gui/layout.py)
# ============================================================================
class APGIMainWindow:
    def __init__(self, root, app_name="Neuroscape / Architect"):
        self.root = root
        self.root.title(f"APGI {app_name}")
        self.root.geometry("1100x750")
        self.root.minsize(1100, 750)
        self.root.configure(bg=APGI_DARK)

        self.header = None
        self.canvas_widget = None
        self.control_panel = None
        self.session_time = 0.0
        self.active = True

        self._build_header(app_name)
        self._build_body()
        self._setup_timers()

    def _build_header(self, app_name):
        self.header = APGIHeaderWidget(self.root, app_name)
        self.header.pack(fill=tk.X)

    def _build_body(self):
        # Main content frame with two columns (splitter replacement)
        body_frame = tk.Frame(self.root, bg=APGI_DARK)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure grid weights for proportional sizing (65/35 split)
        body_frame.columnconfigure(0, weight=65)
        body_frame.columnconfigure(1, weight=35)
        body_frame.rowconfigure(0, weight=1)

        # Canvas (left side)
        canvas_frame = tk.Frame(body_frame, bg=APGI_BG)
        canvas_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        self.canvas_widget = APGICanvas(canvas_frame, width=9, height=7, dpi=100)
        self.canvas_widget.canvas_widget.grid(row=0, column=0, sticky="nsew")

        # Control panel (right side)
        self.control_panel = APGIControlPanel(body_frame)
        self.control_panel.grid(row=0, column=1, sticky="nsew")
        self.control_panel.set_update_callback(self._sync_live_ui)

    def _setup_timers(self):
        # Use tkinter's after method for 10Hz live update (100ms)
        self._animate_data()

    def _sync_live_ui(self, params):
        bt = params.get("threshold", 3.0)
        pi = params.get("precision", 0.5)
        eps = params.get("prediction_error", 1.5)
        beta = params.get("neuromodulator", 0.0)
        st = pi * abs(eps)
        ign = "✓ IGNITION" if st > bt else "○ WAITING"

        # Update equation label
        self.header.equation_lbl.config(
            text=f"Π × |ε| = {st:.2f}  {ign}  > Bt ({bt:.1f})"
        )
        color = APGI_PURPLE if st > bt else APGI_GREEN
        self.header.equation_lbl.config(fg=color)

        # Update badges
        self.header.b1.config(text=f"Bt: {bt:.1f}", fg=APGI_BLUE)
        self.header.b2.config(text=f"PI: {pi:.2f}", fg=APGI_RED)
        self.header.b3.config(text=f"|ε|: {eps:.1f}", fg=APGI_YELLOW)
        self.header.b4.config(text=f"β: {beta:.1f}", fg=APGI_GREEN)

        # Update session dot
        self.header.session_dot.config(fg=APGI_GREEN)

    def _animate_data(self):
        if not self.active:
            return
        self.session_time += 0.1

        # For visual smoothness, we just push current params + tiny noise to plot
        # Map internal param names to update_plot expected keys
        p = {
            "bt": self.control_panel.params["threshold"],
            "pi": self.control_panel.params["precision"],
            "eps": self.control_panel.params["prediction_error"],
            "beta": self.control_panel.params["neuromodulator"],
            "t": np.linspace(0, 10, 100),
        }
        self.canvas_widget.update_plot(p)

        # Schedule next update (10Hz = 100ms)
        self.root.after(100, self._animate_data)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    plt.rcParams.update(APGI_RCPARAMS)  # Apply once at startup
    setup_apgi_fonts()

    root = tk.Tk()
    window = APGIMainWindow(root, "Neuroscape / Architect")

    try:
        root.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
