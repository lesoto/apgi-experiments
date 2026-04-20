import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk

# --- APGI Visual Identity System ---
APGI_BLUE = "#00B4FF"  # Threshold (Bt)
APGI_RED = "#FF3366"  # Interoceptive Precision (PI)
APGI_YELLOW = "#FFCC00"  # Prediction Error (|ε|)
APGI_GREEN = "#00CC99"  # Neuromodulator Tone
APGI_PURPLE = "#9966FF"  # Global Workspace / Ignition
APGI_DARK = "#2C3E50"  # Background / Structure
APGI_BG = "#1A2634"  # Dark background
APGI_FG = "#E8F4FD"  # Light foreground

# Parameter -> Color map
PARAM_COLORS = {
    "threshold": APGI_BLUE,
    "precision": APGI_RED,
    "prediction_error": APGI_YELLOW,
    "neuromodulator": APGI_GREEN,
    "ignition": APGI_PURPLE,
}

# matplotlib rcParams
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
    "font.family": "sans-serif",
}


# --- Font Setup ---
def setup_apgi_fonts():
    """Call once at app startup before any widget creation."""
    # Tkinter uses system fonts; custom fonts would need to be registered via tkfont
    # For now, we'll use standard fonts that are likely available
    pass


# --- Visualization Functions ---
def plot_apgi_radar(ax, values, title="APGI Signature", fill_alpha=0.25):
    """APGI Signature Radar Chart."""
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
    ax.set_facecolor("#1A2634")
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
    """SDE Trajectory Visualization."""
    ax.set_facecolor("#1A2634")
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
    """Parameter Correlation Heatmap."""
    from matplotlib.colors import LinearSegmentedColormap

    APGI_DIVERGING_CMAP = LinearSegmentedColormap.from_list(
        "apgi_diverge", ["#00B4FF", "#1A2634", "#FF3366"], N=256
    )
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


# --- APGI State Logic ---
def get_apgi_state(threshold, precision, pred_error, neuromodulator):
    """Determine psychological state and category based on APGI parameters."""
    # Logic based on Friston 2010, Barrett 2017
    score = (precision * pred_error) - threshold

    if score > 2.0:
        return "Optimal / Flow", 1
    elif score > 0.5:
        return "Heightened Awareness", 2
    elif abs(score) <= 0.5:
        return "Balanced / Regulated", 3
    elif score > -1.0:
        return "Transitional / Learning", 4
    elif neuromodulator > 1.5:
        return "Stress / Arousal", 5
    elif precision > 0.8 and pred_error > 3.0:
        return "Anxiety / Hypervigilance", 6
    elif threshold > 8.0:
        return "Dissociation", 7
    else:
        return "Pathological / Crisis", 8


# --- GUI Widgets ---
class APGIParameterSlider(tk.Frame):
    """APGI Branded Parameter Slider."""

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
        self.label = label
        self.step = step
        self.value_callback = None
        self.color = PARAM_COLORS.get(param_name, "#E8F4FD")
        self._build_ui(label, symbol, min_val, max_val, default, citation)

    def _build_ui(self, label, symbol, lo, hi, default, citation):
        # Configure frame
        self.configure(bg=APGI_DARK)

        # Label with symbol
        lbl = tk.Label(
            self,
            text=f"{symbol}  {label}",
            fg=self.color,
            bg=APGI_DARK,
            font=("Inter", 10),
        )
        lbl.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        if citation:
            lbl.tooltip = citation  # Store for potential tooltip implementation

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
            bg=APGI_DARK,
            fg=APGI_FG,
            highlightthickness=0,
            troughcolor=APGI_BG,
            command=self._on_value_change,
        )
        self.scale.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Readout label
        self.readout = tk.Label(
            self,
            text=f"{default:.3f}",
            fg=self.color,
            bg=APGI_DARK,
            font=("JetBrains Mono", 10),
        )
        self.readout.grid(row=0, column=2, padx=2, pady=2)

        # Configure grid weights
        self.columnconfigure(1, weight=1)

    def _on_value_change(self, value):
        val = float(value)
        self.readout.config(text=f"{val:.3f}")
        if self.value_callback:
            self.value_callback(self.label, val)

    def set_value_callback(self, callback):
        """Set callback for value changes: callback(label, value)"""
        self.value_callback = callback

    def get_value(self):
        return self.value_var.get()


class APGIStateBadge(tk.Frame):
    """APGI Psychological State Badge."""

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

    def __init__(self, parent, state_name, category, param_config):
        super().__init__(parent)
        self.state_name = state_name
        self.category = category
        self.param_config = param_config
        self.configure(bg=APGI_DARK)

        if category == 8:
            self._show_clinical_flag()

        color = self.STATE_CATEGORY_COLORS.get(category, "#E8F4FD")
        self._build_badge(color)

    def update_state(self, state_name, category, param_config):
        """Update the badge with new state information."""
        self.state_name = state_name
        self.category = category
        self.param_config = param_config

        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        if category == 8:
            self._show_clinical_flag()

        color = self.STATE_CATEGORY_COLORS.get(category, "#E8F4FD")
        self._build_badge(color)

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

    def _build_badge(self, color):
        inner_frame = tk.Frame(self, bg=APGI_DARK)
        inner_frame.pack(fill=tk.X)

        # State badge label
        lbl = tk.Label(
            inner_frame,
            text=f"  {self.state_name}  ",
            fg="white",
            bg=color,
            font=("Inter", 10, "bold"),
            relief=tk.FLAT,
            padx=8,
            pady=2,
        )
        lbl.pack(side=tk.LEFT)

        # Config label
        config_lbl = tk.Label(
            inner_frame,
            text=self.param_config,
            fg=APGI_FG,
            bg=APGI_DARK,
            font=("JetBrains Mono", 9),
        )
        config_lbl.pack(side=tk.LEFT, padx=(10, 0))


class APGICanvas(FigureCanvasTkAgg):
    """Embedded Matplotlib Canvas for APGI Visualizations."""

    def __init__(self, parent, width=8, height=6, dpi=120):
        plt.rcParams.update(APGI_RCPARAMS)
        self.fig = Figure(
            figsize=(width, height),
            dpi=dpi,
            facecolor=APGI_RCPARAMS["figure.facecolor"],
        )
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig, master=parent)
        self.draw()

    def update_plot(self, data: dict):
        self.axes.cla()
        if "radar" in data:
            plot_apgi_radar(self.axes, data["radar"])
        elif "trajectory" in data:
            plot_sde_trajectory(
                self.axes,
                data["trajectory"]["t"],
                data["trajectory"]["S_t"],
                data["trajectory"]["B_t"],
                data["trajectory"].get("ignition_events"),
            )
        elif "heatmap" in data:
            plot_correlation_heatmap(self.axes, data["heatmap"])
        self.draw()


# --- Main Window ---
class APGIHeaderWidget(tk.Frame):
    """APGI Header Zone."""

    def __init__(self, parent, app_name):
        super().__init__(parent)
        self.app_name = app_name
        self.configure(bg=APGI_DARK, padx=10, pady=5)
        self._build_header()

    def _build_header(self):
        # APGI Logo
        apgi_logo = tk.Label(
            self, text="APGI", fg=APGI_BLUE, bg=APGI_DARK, font=("Inter", 16, "bold")
        )
        apgi_logo.pack(side=tk.LEFT)

        # Subtitle
        subtitle = tk.Label(
            self,
            text=f"|  {self.app_name}",
            fg=APGI_FG,
            bg=APGI_DARK,
            font=("Inter", 12),
        )
        subtitle.pack(side=tk.LEFT, padx=(5, 0))

        # Live equation
        live_eq = tk.Label(
            self,
            text="Π × |ε| > Bt",
            fg=PARAM_COLORS["ignition"],
            bg=APGI_DARK,
            font=("Computer Modern", 12),
        )
        live_eq.pack(side=tk.LEFT, padx=(20, 0))

        # Parameter badges frame
        badges_frame = tk.Frame(self, bg=APGI_DARK)
        badges_frame.pack(side=tk.LEFT, padx=(20, 0))

        for param, color in PARAM_COLORS.items():
            badge = tk.Label(
                badges_frame,
                text=f" {param[0].upper()} ",
                fg="white",
                bg=color,
                font=("JetBrains Mono", 9),
                padx=3,
                pady=1,
            )
            badge.pack(side=tk.LEFT, padx=2)

        # Session indicator
        self.session_indicator = tk.Label(
            self, text="● Idle", fg="#999", bg=APGI_DARK, font=("Inter", 10)
        )
        self.session_indicator.pack(side=tk.RIGHT)


class APGIControlPanel(tk.Frame):
    """APGI Control Panel."""

    def __init__(self, parent, update_callback=None):
        super().__init__(parent)
        self.configure(bg=APGI_DARK, padx=5, pady=5)
        self.sliders = {}
        self.update_callback = update_callback
        self._build_panel()

    def _build_panel(self):
        # Parameter Sliders Section
        sliders_frame = tk.LabelFrame(
            self, text="Parameter Sliders", fg=APGI_FG, bg=APGI_DARK, font=("Inter", 11)
        )
        sliders_frame.pack(fill=tk.X, pady=5)

        # Create sliders
        self.sliders["threshold"] = APGIParameterSlider(
            sliders_frame,
            "threshold",
            "Threshold",
            "Bt",
            0.0,
            10.0,
            3.0,
            citation="Dehaene et al. 2014, Eq. 1",
        )
        self.sliders["threshold"].pack(fill=tk.X, pady=2)
        self.sliders["threshold"].set_value_callback(self._on_any_value_change)

        self.sliders["precision"] = APGIParameterSlider(
            sliders_frame,
            "precision",
            "Precision",
            "Π",
            0.0,
            1.0,
            0.5,
            citation="Friston 2010, Eq. 7",
        )
        self.sliders["precision"].pack(fill=tk.X, pady=2)
        self.sliders["precision"].set_value_callback(self._on_any_value_change)

        self.sliders["prediction_error"] = APGIParameterSlider(
            sliders_frame,
            "prediction_error",
            "Pred. Error",
            "ε",
            0.0,
            5.0,
            1.5,
            citation="Barrett & Simmons 2015, Eq. 2",
        )
        self.sliders["prediction_error"].pack(fill=tk.X, pady=2)
        self.sliders["prediction_error"].set_value_callback(self._on_any_value_change)

        self.sliders["neuromodulator"] = APGIParameterSlider(
            sliders_frame,
            "neuromodulator",
            "Neuromodulator",
            "β",
            -3.0,
            3.0,
            0.0,
            citation="Friston et al. 2012, Eq. 4",
        )
        self.sliders["neuromodulator"].pack(fill=tk.X, pady=2)
        self.sliders["neuromodulator"].set_value_callback(self._on_any_value_change)

        # State Badge
        self.state_badge = APGIStateBadge(
            self, "Balanced / Regulated", 3, "Bt=3.0, Π=0.5, |ε|=1.5, β=0.0"
        )
        self.state_badge.pack(fill=tk.X, pady=10)

    def _on_any_value_change(self, label, value):
        params = {name: slider.get_value() for name, slider in self.sliders.items()}

        state_name, category = get_apgi_state(
            params["threshold"],
            params["precision"],
            params["prediction_error"],
            params["neuromodulator"],
        )

        config_str = f"Bt={params['threshold']:.1f}, Π={params['precision']:.2f}, |ε|={params['prediction_error']:.1f}, β={params['neuromodulator']:.1f}"
        self.state_badge.update_state(state_name, category, config_str)

        if self.update_callback:
            self.update_callback(params)

    def get_params(self):
        return {name: slider.get_value() for name, slider in self.sliders.items()}

        # Export Controls
        export_frame = tk.LabelFrame(
            self, text="Export", fg=APGI_FG, bg=APGI_DARK, font=("Inter", 11)
        )
        export_frame.pack(fill=tk.X, pady=5)

        export_btn1 = tk.Button(
            export_frame,
            text="Export Data",
            bg=APGI_BG,
            fg=APGI_FG,
            font=("Inter", 10),
            activebackground=APGI_BLUE,
            activeforeground="white",
        )
        export_btn1.pack(fill=tk.X, pady=2)

        export_btn2 = tk.Button(
            export_frame,
            text="Export Plot",
            bg=APGI_BG,
            fg=APGI_FG,
            font=("Inter", 10),
            activebackground=APGI_BLUE,
            activeforeground="white",
        )
        export_btn2.pack(fill=tk.X, pady=2)


class APGIMainWindow:
    """APGI Main Window with Three-Zone Layout."""

    def __init__(self, root, app_name: str):
        self.root = root
        self.root.title(app_name)
        self.root.geometry("1000x700")
        self.root.configure(bg=APGI_DARK)

        self._build_header(app_name)
        self._build_body()

    def _build_header(self, app_name: str):
        self.header = APGIHeaderWidget(self.root, app_name)
        self.header.pack(fill=tk.X)

    def _build_body(self):
        # Main content frame with two columns
        body_frame = tk.Frame(self.root, bg=APGI_DARK)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure grid weights for proportional sizing (65/35 split)
        body_frame.columnconfigure(0, weight=65)
        body_frame.columnconfigure(1, weight=35)
        body_frame.rowconfigure(0, weight=1)

        # Canvas (left side)
        self.canvas_frame = tk.Frame(body_frame, bg=APGI_DARK)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.canvas_frame.rowconfigure(0, weight=1)
        self.canvas_frame.columnconfigure(0, weight=1)

        self.canvas = APGICanvas(self.canvas_frame, width=8, height=6, dpi=100)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg=APGI_BG)
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

        # Control panel (right side)
        self.control_panel = APGIControlPanel(
            body_frame, update_callback=self._on_params_changed
        )
        self.control_panel.grid(row=0, column=1, sticky="nsew")

        # Set minimum sizes to maintain usability
        self.canvas_frame.config(width=600, height=400)
        self.control_panel.config(width=300, height=400)

    def _on_params_changed(self, params):
        """Handle parameter changes from control panel."""
        # Generate new simulation data based on parameters
        t = np.linspace(0, 10, 500)

        # SDE-like trajectory simulation
        noise = np.random.normal(0, 0.1, len(t))
        signal_base = params["precision"] * params["prediction_error"]
        S_t = signal_base + np.cumsum(noise)
        B_t = np.full_like(t, params["threshold"])

        ignition_events = []
        if any(S_t > B_t):
            ignition_indices = np.where(np.diff((S_t > B_t).astype(int)) > 0)[0]
            ignition_events = t[ignition_indices].tolist()

        data = {
            "radar": [
                params["threshold"] / 10.0,
                params["precision"],
                params["prediction_error"] / 5.0,
                (params["neuromodulator"] + 3.0) / 6.0,
                0.5,  # Static somatic bias for now
            ],
            "trajectory": {
                "t": t,
                "S_t": S_t,
                "B_t": B_t,
                "ignition_events": ignition_events,
            },
        }

        # We'll default to trajectory for live updates
        self.canvas.update_plot(data)

    def update_visualization(self, data: dict):
        self.canvas.update_plot(data)


# --- Main Application ---
def main():
    setup_apgi_fonts()
    root = tk.Tk()
    window = APGIMainWindow(root, "APGI Explorer")

    # Initial update based on default slider values
    params = window.control_panel.get_params()
    window._on_params_changed(params)

    root.mainloop()


if __name__ == "__main__":
    main()
