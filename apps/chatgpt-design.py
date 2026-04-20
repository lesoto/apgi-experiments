import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap

# =========================
# APGI COLOR SYSTEM
# =========================

APGI_BLUE = "#00B4FF"
APGI_RED = "#FF3366"
APGI_YELLOW = "#FFCC00"
APGI_GREEN = "#00CC99"
APGI_PURPLE = "#9966FF"
APGI_DARK = "#2C3E50"

PARAM_COLORS = {
    "threshold": APGI_BLUE,
    "precision": APGI_RED,
    "prediction_error": APGI_YELLOW,
    "neuromodulator": APGI_GREEN,
    "ignition": APGI_PURPLE,
}

plt.rcParams.update(
    {
        "figure.facecolor": "#1A2634",
        "axes.facecolor": "#1A2634",
        "axes.edgecolor": "#2C3E50",
        "axes.labelcolor": "#E8F4FD",
        "xtick.color": "#E8F4FD",
        "ytick.color": "#E8F4FD",
        "text.color": "#E8F4FD",
        "grid.color": "#2C3E50",
    }
)

# =========================
# CORE APGI LOGIC
# =========================


def compute_apgi_signal(epsilon, precision):
    return precision * abs(epsilon)


def compute_threshold(beta, base_bt):
    return base_bt + beta


def detect_ignition(St, Bt):
    return St > Bt


def integrate_euler_maruyama(mu=0.1, sigma=0.2, dt=0.1, steps=100):
    X = np.zeros(steps)
    for i in range(1, steps):
        X[i] = X[i - 1] + mu * dt + sigma * np.sqrt(dt) * np.random.randn()
    return X


# =========================
# VISUALIZATION FUNCTIONS
# =========================


def plot_radar(ax, values):
    labels = ["Threshold", "Precision", "Pred Error", "Neuromod", "Bias"]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    values = np.append(values, values[0])
    angles = np.append(angles, angles[0])

    ax.clear()
    ax.plot(angles, values, color=APGI_PURPLE)
    ax.fill(angles, values, color=APGI_PURPLE, alpha=0.3)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)


def plot_trajectory(ax, St, Bt):
    t = np.arange(len(St))
    ax.clear()
    ax.plot(t, St, color=APGI_PURPLE, label="St")
    ax.plot(t, Bt, color=APGI_BLUE, linestyle="--", label="Bt")

    for i in range(len(St)):
        if St[i] > Bt[i]:
            ax.axvline(i, color=APGI_YELLOW, linestyle=":")

    ax.legend()


def plot_heatmap(ax):
    data = np.random.uniform(-1, 1, (5, 5))

    cmap = LinearSegmentedColormap.from_list("apgi", [APGI_BLUE, "#1A2634", APGI_RED])

    ax.clear()
    im = ax.imshow(data, cmap=cmap, vmin=-1, vmax=1)
    ax.figure.colorbar(im, ax=ax)


# =========================
# GUI APP
# =========================


class APGIExplorer:

    def __init__(self, root):
        self.root = root
        self.root.title("APGI Explorer")

        self.build_header()
        self.build_body()

        self.update_visuals()

    # =========================
    # HEADER
    # =========================

    def build_header(self):
        frame = tk.Frame(self.root, bg=APGI_DARK)
        frame.pack(fill="x")

        self.title = tk.Label(
            frame,
            text="APGI | Explorer",
            fg=APGI_BLUE,
            bg=APGI_DARK,
            font=("Arial", 14, "bold"),
        )
        self.title.pack(side="left", padx=10)

        self.eq_label = tk.Label(frame, text="Π × |ε| > Bt", fg="white", bg=APGI_DARK)
        self.eq_label.pack(side="right", padx=10)

    # =========================
    # BODY
    # =========================

    def build_body(self):
        main = tk.Frame(self.root)
        main.pack(fill="both", expand=True)

        self.canvas_frame = tk.Frame(main)
        self.canvas_frame.pack(side="left", fill="both", expand=True)

        self.control_frame = tk.Frame(main, bg=APGI_DARK)
        self.control_frame.pack(side="right", fill="y")

        self.build_controls()
        self.build_plots()

    # =========================
    # CONTROLS
    # =========================

    def build_controls(self):

        self.epsilon = tk.DoubleVar(value=1.5)
        self.precision = tk.DoubleVar(value=0.5)
        self.bt = tk.DoubleVar(value=3.0)
        self.beta = tk.DoubleVar(value=0.0)

        self.add_slider("ε Prediction Error", self.epsilon, 0, 5, APGI_YELLOW)
        self.add_slider("Π Precision", self.precision, 0, 1, APGI_RED)
        self.add_slider("Bt Threshold", self.bt, 0, 10, APGI_BLUE)
        self.add_slider("β Neuromod", self.beta, -3, 3, APGI_GREEN)

    def add_slider(self, label, var, minv, maxv, color):
        frame = tk.Frame(self.control_frame, bg=APGI_DARK)
        frame.pack(pady=10)

        lbl = tk.Label(frame, text=label, fg=color, bg=APGI_DARK)
        lbl.pack()

        slider = tk.Scale(
            frame,
            variable=var,
            from_=minv,
            to=maxv,
            resolution=0.01,
            orient="horizontal",
            command=lambda e: self.update_visuals(),
        )
        slider.pack()

    # =========================
    # PLOTS
    # =========================

    def build_plots(self):
        self.fig = Figure(figsize=(8, 6))
        self.ax1 = self.fig.add_subplot(131, polar=True)
        self.ax2 = self.fig.add_subplot(132)
        self.ax3 = self.fig.add_subplot(133)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # =========================
    # UPDATE LOOP
    # =========================

    def update_visuals(self):

        eps = self.epsilon.get()
        pi = self.precision.get()
        bt = self.bt.get()
        beta = self.beta.get()

        St = compute_apgi_signal(eps, pi)
        Bt = compute_threshold(beta, bt)

        ignition = detect_ignition(St, Bt)

        self.eq_label.config(
            text=f"{pi:.2f} × {abs(eps):.2f} {'>' if ignition else '<'} {Bt:.2f}"
        )

        # Radar normalized
        radar_vals = [bt / 10, pi, eps / 5, (beta + 3) / 6, (beta + 3) / 6]

        plot_radar(self.ax1, radar_vals)

        traj = integrate_euler_maruyama(steps=100)
        Bt_series = np.ones(100) * Bt
        plot_trajectory(self.ax2, traj, Bt_series)

        plot_heatmap(self.ax3)

        self.fig.text(
            0.01,
            0.01,
            "APGI Framework — Friston 2010; Barrett 2017; Dehaene 2014",
            fontsize=6,
            color="#4A5568",
        )

        self.canvas.draw()


# =========================
# RUN
# =========================

if __name__ == "__main__":
    root = tk.Tk()
    app = APGIExplorer(root)
    root.geometry("1200x600")
    root.mainloop()
