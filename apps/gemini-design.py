#!/usr/bin/env python3
"""
APGI Framework - Core Implementation and GUI Architecture
Last updated: Apr 19, 2026

This module serves as the consolidated implementation of the APGI Software Design
Document, covering the Research Suite core, visual identity, visualization standards,
and the tkinter desktop architecture (Neuroscape/Architect).

Dependencies: tkinter (built-in), matplotlib, numpy, ipywidgets (optional for Jupyter)
"""

import numpy as np

# --- APGI CORE / MATH IMPLEMENTATION ---


def calculate_threshold_crossing(
    prediction_error: float,
    precision_weight: float,
    broadcast_threshold: float,
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


# --- VISUAL IDENTITY SYSTEM (apgi/colors.py) ---

APGI_BLUE = "#00B4FF"  # Threshold (Bt)
APGI_RED = "#FF3366"  # Interoceptive Precision (PI)
APGI_YELLOW = "#FFCC00"  # Prediction Error (|epsilon|)
APGI_GREEN = "#00CC99"  # Neuromodulator Tone
APGI_PURPLE = "#9966FF"  # Global Workspace / Ignition
APGI_DARK = "#2C3E50"  # Background / Structure

PARAM_COLORS = {
    "threshold": APGI_BLUE,
    "precision": APGI_RED,
    "prediction_error": APGI_YELLOW,
    "neuromodulator": APGI_GREEN,
    "ignition": APGI_PURPLE,
    "somatic_bias": APGI_PURPLE,  # Somatic Bias falls under global workspace/integration context visually
}

APGI_RCPARAMS = {
    "figure.facecolor": "#1A2634",
    "axes.facecolor": "#1A2634",
    "axes.edgecolor": "#2C3E50",
    "axes.labelcolor": "#E8F4FD",
    "xtick.color": "#E8F4FD",
    "ytick.color": "#E8F4FD",
    "text.color": "#E8F4FD",
    "grid.color": "#2C3E50",
    "grid.alpha": 0.4,
    "font.family": "sans-serif",  # Fallback from Inter if not installed system-wide
}

# --- Tkinter / GUI ARCHITECTURE ---

import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap


# Setup Fonts
def setup_apgi_fonts():
    """Call once at app startup before any widget creation."""
    # In a real environment, these assets must be present.
    # For tkinter, we use system fonts with fallbacks
    pass


# tkinter uses font tuples: (family, size, weight)
FONT_UI_BODY = ("Helvetica", 11, "normal")
FONT_UI_HEADER = ("Helvetica", 13, "bold")
FONT_EQUATION = ("Courier", 11, "normal")
FONT_SECTION = ("Times", 15, "bold")

# --- WIDGETS ---


class APGIParameterSlider(tk.Frame):
    """
    Branded parameter slider. Color-codes to APGI semantic palette.
    """

    def __init__(
        self,
        param_name,
        label,
        symbol,
        min_val,
        max_val,
        default,
        step=0.01,
        citation="",
        parent=None,
        callback=None,
    ):
        super().__init__(parent)
        self.param_name = param_name
        self.callback = callback
        self.step = step
        color = PARAM_COLORS.get(param_name, "#E8F4FD")
        self._build_ui(label, symbol, color, min_val, max_val, default, step, citation)

    def _build_ui(self, label, symbol, color, lo, hi, default, step, citation):
        self.configure(bg="#1A2634")

        # Label
        lbl = tk.Label(
            self, text=f"{symbol}  {label}", font=FONT_UI_BODY, bg="#1A2634", fg=color
        )
        lbl.pack(side=tk.LEFT, padx=5)

        # Slider
        slider = tk.Scale(
            self,
            from_=lo,
            to=hi,
            orient=tk.HORIZONTAL,
            resolution=step,
            length=300,
            bg="#2C3E50",
            fg=color,
            highlightthickness=0,
            troughcolor="#2C3E50",
            activebackground=color,
        )
        slider.set(default)
        slider.pack(side=tk.LEFT, padx=5)

        # Readout
        readout = tk.Label(
            self,
            text=f"{default:.3f}",
            font=FONT_EQUATION,
            bg="#1A2634",
            fg=color,
            width=8,
        )
        readout.pack(side=tk.LEFT, padx=5)

        # Bind slider event
        def on_slider_change(val):
            value = float(val)
            readout.config(text=f"{value:.3f}")
            if self.callback:
                self.callback(self.param_name, value)

        slider.config(command=on_slider_change)


STATE_CATEGORY_COLORS = {
    1: "#9966FF",  # Optimal / Flow
    2: "#00B4FF",  # Heightened Awareness
    3: "#00CC99",  # Balanced / Regulated
    4: "#FFCC00",  # Transitional / Learning
    5: "#FF6633",  # Stress / Arousal
    6: "#FF3366",  # Anxiety / Hypervigilance
    7: "#7F8C8D",  # Dissociation
    8: "#2C3E50",  # Pathological / Crisis
}


class APGIStateBadge(tk.Frame):
    """Current APGI psychological state display."""

    def __init__(self, state_name, category, param_config, parent=None):
        super().__init__(parent)
        self.configure(bg="#1A2634")

        if category == 8:
            self._show_clinical_flag()

        color = STATE_CATEGORY_COLORS.get(category, "#E8F4FD")
        self._build_badge(state_name, color, param_config)

    def _show_clinical_flag(self):
        """Category 8: mandatory clinical context note."""
        flag = tk.Label(
            self,
            text="⚠ This system configuration is outside normative ranges. "
            "This is a parameter description, not a clinical diagnosis. "
            "If distress persists, consult a qualified mental health professional.",
            bg="#2C1810",
            fg="#FFCC00",
            font=("Helvetica", 10),
            wraplength=400,
            justify=tk.LEFT,
            padx=8,
            pady=8,
            relief=tk.SOLID,
            borderwidth=1,
            bordercolor="#FF6633",
        )
        flag.pack(pady=5, padx=5, fill=tk.X)

    def _build_badge(self, state_name, color, param_config):
        lbl = tk.Label(
            self,
            text=f"  {state_name}  ",
            font=("Helvetica", 11, "bold"),
            bg=color,
            fg="white",
            padx=12,
            pady=4,
        )
        lbl.pack(pady=5)

        config_lbl = tk.Label(
            self, text=param_config, font=("Courier", 9), bg="#1A2634", fg="#E8F4FD"
        )
        config_lbl.pack(pady=2)


# --- VISUALIZATION STANDARDS ---

RADAR_AXES = [
    ("Threshold\nSensitivity", "#00B4FF"),
    ("Interoceptive\nPrecision", "#FF3366"),
    ("Prediction\nError", "#FFCC00"),
    ("Neuromodulator\nTone", "#00CC99"),
    ("Somatic\nBias", "#9966FF"),
]


def plot_apgi_radar(ax, values, title="APGI Signature", fill_alpha=0.25):
    """Primary representation of an individual's APGI state profile."""
    N = len(RADAR_AXES)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values_plot = list(values) + [values[0]]

    ax.set_facecolor("#1A2634")
    ax.plot(angles, values_plot, color="#9966FF", lw=2.0)
    ax.fill(angles, values_plot, color="#9966FF", alpha=fill_alpha)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([a[0] for a in RADAR_AXES], size=8, color="#E8F4FD")
    for i, (_, color) in enumerate(RADAR_AXES):
        ax.tick_params(axis="x", colors=color)
    ax.set_title(title, color="#E8F4FD", pad=20, fontsize=12)


def plot_sde_trajectory(ax, t, S_t, B_t, ignition_events=None):
    """Stochastic differential equation trajectory visualization."""
    ax.set_facecolor("#1A2634")
    ax.plot(t, S_t, color="#9966FF", lw=2.0, label="St (Consciousness Signal)")
    ax.plot(t, B_t, color="#00B4FF", lw=1.5, ls="--", label="Bt (Threshold)")
    if ignition_events:
        for i, t_ign in enumerate(ignition_events):
            ax.axvline(
                x=t_ign,
                color="#FFCC00",
                alpha=0.7,
                lw=1.0,
                ls=":",
                label="Ignition" if i == 0 else None,
            )
    ax.legend(loc="upper right", fontsize=8, facecolor="#2C3E50", labelcolor="#E8F4FD")
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


APGI_DIVERGING_CMAP = LinearSegmentedColormap.from_list(
    "apgi_diverge", ["#00B4FF", "#1A2634", "#FF3366"], N=256  # Blue -> Dark -> Red
)

PARAM_LABELS = [
    "Bt Threshold",
    "PI Precision",
    "|eps| Pred.Error",
    "Neuromod.",
    "beta Somatic Bias",
]


def plot_correlation_heatmap(ax, corr_matrix):
    """Displays cross-parameter relationships."""
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


class APGICanvas(tk.Frame):
    """Embedded matplotlib canvas. Mandatory pattern."""

    def __init__(self, parent=None, width=8, height=6, dpi=120):
        super().__init__(parent)
        self.configure(bg="#1A2634")
        plt.rcParams.update(APGI_RCPARAMS)
        self.fig = Figure(
            figsize=(width, height),
            dpi=dpi,
            facecolor=APGI_RCPARAMS["figure.facecolor"],
        )
        # Use polar axes by default for the APGI Signature Radar
        self.axes = self.fig.add_subplot(111, polar=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plot(self, data: dict):
        self.axes.cla()

        # Extract normalized values for radar (assuming data comes from sliders)
        # Radar order: Bt, PI, |eps|, Beta, Somatic Bias (using beta again here for demo)
        bt_norm = data.get("threshold", 3.0) / 10.0
        pi_norm = data.get("precision", 0.5) / 1.0
        eps_norm = data.get("prediction_error", 1.5) / 5.0
        beta_norm = (data.get("neuromodulator", 0.0) + 3.0) / 6.0

        values = [bt_norm, pi_norm, eps_norm, beta_norm, beta_norm]
        plot_apgi_radar(self.axes, values)

        # Mandatory citation watermark on every figure
        self.fig.text(
            0.01,
            0.01,
            "APGI Framework — Friston 2010; Barrett 2017; Dehaene 2014",
            fontsize=6,
            color="#4A5568",
            alpha=0.7,
        )
        self.canvas.draw()


# --- LAYOUT / MAIN WINDOW ---


class APGIHeaderWidget(tk.Frame):
    """Header Zone: Provocative - app name | live equation | param badges"""

    def __init__(self, app_name: str):
        super().__init__()
        self.configure(bg="#2C3E50")

        # APGI Wordmark
        wordmark = tk.Label(
            self,
            text="APGI",
            font=("Helvetica", 18, "bold"),
            bg="#2C3E50",
            fg=APGI_BLUE,
        )
        wordmark.pack(side=tk.LEFT, padx=10)

        # Subtitle
        subtitle = tk.Label(
            self,
            text=f"|  {app_name}",
            font=("Helvetica", 12),
            bg="#2C3E50",
            fg="#E8F4FD",
        )
        subtitle.pack(side=tk.LEFT, padx=5)

        # Live Equation
        eq = tk.Label(
            self,
            text="Π × |ε| > Bt",
            font=("Times", 14, "bold"),
            bg="#2C3E50",
            fg="#E8F4FD",
        )
        eq.pack(side=tk.RIGHT, padx=20)

        # Session Indicator
        indicator = tk.Label(
            self,
            text="● Session Active",
            font=("Helvetica", 10, "bold"),
            bg="#2C3E50",
            fg="#00CC99",
        )
        indicator.pack(side=tk.RIGHT, padx=10)


class APGIControlPanel(tk.Frame):
    """Control Panel Zone: Compassionate - sliders, state, queue."""

    def __init__(self, parent=None, canvas=None):
        super().__init__(parent)
        self.configure(bg="#1A2634")
        self.canvas = canvas
        self.current_params = {}
        self._build_panel()

    def _build_panel(self):
        title = tk.Label(
            self,
            text="System Parameters",
            font=FONT_SECTION,
            bg="#1A2634",
            fg="#E8F4FD",
        )
        title.pack(pady=(0, 10), anchor=tk.W)

        # Parameter Sliders
        sliders = [
            (
                "prediction_error",
                "Prediction Error",
                "ε",
                0.0,
                5.0,
                1.5,
                0.01,
                "Barrett & Simmons 2015, Eq. 2",
            ),
            (
                "precision",
                "Precision Weight",
                "Π",
                0.0,
                1.0,
                0.5,
                0.001,
                "Friston 2010, Eq. 7",
            ),
            (
                "threshold",
                "Broadcast Threshold",
                "Bt",
                0.0,
                10.0,
                3.0,
                0.01,
                "Dehaene et al. 2014, Eq. 1",
            ),
            (
                "neuromodulator",
                "Neuromodulator Tone",
                "β",
                -3.0,
                3.0,
                0.0,
                0.01,
                "Friston et al. 2012, Eq. 4",
            ),
        ]

        for p_name, label, sym, mn, mx, df, step, cit in sliders:
            slider = APGIParameterSlider(
                p_name,
                label,
                sym,
                mn,
                mx,
                df,
                step,
                cit,
                parent=self,
                callback=self._on_param_changed,
            )
            slider.pack(pady=5, fill=tk.X)
            self.current_params[p_name] = df

        # Dynamic State Badge Placeholder
        self.badge_container = tk.Frame(self, bg="#1A2634")
        self.badge_container.pack(pady=20, fill=tk.X)
        self._update_state_badge()

    def _on_param_changed(self, param_name, value):
        self.current_params[param_name] = value
        if self.canvas:
            self.canvas.update_plot(self.current_params)
        self._update_state_badge()

    def _update_state_badge(self):
        # Clear existing badge
        for widget in self.badge_container.winfo_children():
            widget.destroy()

        # Example Logic for classification (mapping to category 8 if threshold wildly out of sync)
        bt = self.current_params.get("threshold", 3.0)
        eps = self.current_params.get("prediction_error", 1.5)
        pi = self.current_params.get("precision", 0.5)

        if pi > 0.9 and eps > 4.0:
            cat = 8
            state_name = "Hyper-Precision Crisis"
        elif bt > 7.0 and pi > 0.7:
            cat = 6
            state_name = "Anxiety / Hypervigilance"
        elif bt < 2.0 and pi > 0.6:
            cat = 1
            state_name = "Optimal / Flow"
        else:
            cat = 3
            state_name = "Balanced / Regulated"

        cfg_str = f"Bt:{bt:.2f} | Π:{pi:.3f} | ε:{eps:.2f}"
        badge = APGIStateBadge(state_name, cat, cfg_str, parent=self.badge_container)
        badge.pack(fill=tk.X)


class APGIMainWindow(tk.Tk):
    """Three-Zone Layout: Header, Main Canvas, Control Panel"""

    def __init__(self, app_name: str):
        super().__init__()
        self.title(f"APGI {app_name}")
        self.geometry("1200x800")
        self.configure(bg="#1A2634")

        self._build_header(app_name)
        self._build_body()

        # Initial Plot Trigger
        self.control_panel._on_param_changed("init", 0.0)

    def _build_header(self, app_name: str):
        header = APGIHeaderWidget(app_name)
        header.pack(side=tk.TOP, fill=tk.X)

    def _build_body(self):
        # Main body frame
        body = tk.Frame(self, bg="#1A2634")
        body.pack(fill=tk.BOTH, expand=True)

        # Canvas Zone (Authoritative) - 65%
        canvas_frame = tk.Frame(body, bg="#1A2634")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = APGICanvas(canvas_frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Control Panel Zone (Compassionate) - 35%
        self.control_panel = APGIControlPanel(body, canvas=self.canvas)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)


# --- NOTEBOOK COMPATIBILITY MODULE (apgi/simulation/widgets.py) ---
# Included here to satisfy 100% implementation spec, used when in Jupyter.

import ipywidgets as widgets  # type: ignore


def create_apgi_slider(
    param_name, symbol, min_val, max_val, default, citation, step=0.01
):
    """Branded APGI parameter slider for Jupyter environments."""
    color = PARAM_COLORS.get(param_name, "#E8F4FD")
    return widgets.FloatSlider(
        value=default,
        min=min_val,
        max=max_val,
        step=step,
        description=f"{symbol}  ({param_name})",
        style={"description_width": "200px", "handle_color": color},
        layout=widgets.Layout(width="600px"),
        continuous_update=True,
        readout_format=".3f",
    )


def create_standard_apgi_sliders():
    return {
        "epsilon": create_apgi_slider(
            "prediction_error", "ε", 0.0, 5.0, 1.5, "Barrett & Simmons 2015, Eq. 2"
        ),
        "pi": create_apgi_slider(
            "precision", "Π", 0.0, 1.0, 0.5, "Friston 2010, Eq. 7"
        ),
        "bt": create_apgi_slider(
            "threshold", "Bt", 0.0, 10.0, 3.0, "Dehaene et al. 2014, Eq. 1"
        ),
        "beta": create_apgi_slider(
            "neuromodulator", "β", -3.0, 3.0, 0.0, "Friston et al. 2012, Eq. 4"
        ),
    }


# --- EXECUTION ---

if __name__ == "__main__":
    # Initialize Core Application Fonts
    setup_apgi_fonts()

    # Launch APGI Neuroscape / Architect standard layout
    window = APGIMainWindow("Neuroscape")
    window.mainloop()
