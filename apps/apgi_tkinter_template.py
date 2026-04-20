import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from apgi_framework.utils.colors import (
    APGI_BLUE,
    APGI_RED,
    APGI_YELLOW,
    APGI_GREEN,
    APGI_PURPLE,
    APGI_DARK,
    APGI_BG,
    APGI_TEXT,
    APGI_RCPARAMS,
)

# Apply Matplotlib styling
plt.rcParams.update(APGI_RCPARAMS)


class APGITemplate(tk.Tk):
    """
    Standard Python tkinter template implementing the APGI Visual Identity System.
    Layout: Header Zone (top), Main Canvas (left), Control Panel (right).
    """

    def __init__(self, app_name="Neuroscape"):
        super().__init__()
        self.title(f"APGI | {app_name}")
        self.geometry("1200x800")
        self.configure(bg=APGI_BG)

        # Initialize parameter variables
        self.bt_val = tk.DoubleVar(value=0.5)
        self.pi_val = tk.DoubleVar(value=0.8)
        self.eps_val = tk.DoubleVar(value=0.2)
        self.beta_val = tk.DoubleVar(value=0.4)

        self._setup_styles()
        self._build_header(app_name)
        self._build_body()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Header style
        style.configure("Header.TFrame", background=APGI_DARK)
        style.configure("Header.TLabel", background=APGI_DARK, foreground=APGI_TEXT)

        # Badge style
        style.configure(
            "Badge.TLabel", background=APGI_DARK, font=("JetBrains Mono", 10)
        )

        # Control panel style
        style.configure("Control.TFrame", background=APGI_BG)
        style.configure("Control.TLabel", background=APGI_BG, foreground=APGI_TEXT)

    def _build_header(self, app_name):
        header = ttk.Frame(self, style="Header.TFrame", height=50)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        # APGI Wordmark
        wordmark = tk.Label(
            header, text="APGI", fg=APGI_BLUE, bg=APGI_DARK, font=("Inter", 18, "bold")
        )
        wordmark.pack(side="left", padx=(15, 5))

        # Divider and Subtitle
        divider = tk.Label(
            header, text="|", fg=APGI_TEXT, bg=APGI_DARK, font=("Inter", 12)
        )
        divider.pack(side="left")
        subtitle = tk.Label(
            header, text=app_name, fg=APGI_TEXT, bg=APGI_DARK, font=("Inter", 12)
        )
        subtitle.pack(side="left", padx=5)

        # Live Equation
        self.eq_label = tk.Label(
            header,
            text="Π × |ε| > Bt",
            fg=APGI_TEXT,
            bg=APGI_DARK,
            font=("JetBrains Mono", 14),
        )
        self.eq_label.pack(side="left", expand=True)

        # Parameter Badges (Pills)
        self.badges = {}
        for param, color, var in [
            ("Bt", APGI_BLUE, self.bt_val),
            ("PI", APGI_RED, self.pi_val),
            ("ε", APGI_YELLOW, self.eps_val),
            ("β", APGI_GREEN, self.beta_val),
        ]:
            frame = tk.Frame(header, bg=color, padx=10, pady=2)
            frame.pack(side="left", padx=5)
            lbl = tk.Label(
                frame,
                text=f"{param}: {var.get():.2f}",
                bg=color,
                fg="white",
                font=("JetBrains Mono", 10, "bold"),
            )
            lbl.pack()
            self.badges[param] = lbl

    def _build_body(self):
        # Body Container
        body = ttk.Frame(self, style="Control.TFrame")
        body.pack(side="top", fill="both", expand=True)

        # Left: Main Canvas (65%)
        self.canvas_frame = ttk.Frame(body, style="Control.TFrame")
        self.canvas_frame.place(relx=0, rely=0, relwidth=0.65, relheight=1)
        self._setup_matplotlib()

        # Right: Control Panel (35%)
        self.controls = ttk.Frame(body, style="Control.TFrame", padding=20)
        self.controls.place(relx=0.65, rely=0, relwidth=0.35, relheight=1)
        self._build_controls()

    def _setup_matplotlib(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self._update_plot()

    def _update_plot(self):
        self.ax.clear()
        x = np.linspace(0, 10, 100)
        # Example visualization: Threshold ignition
        y = self.pi_val.get() * np.sin(x) * (self.eps_val.get() * 5)
        self.ax.plot(
            x, y, color=APGI_PURPLE, linewidth=2, label="Integrated Signal (St)"
        )
        self.ax.axhline(
            y=self.bt_val.get(), color=APGI_BLUE, linestyle="--", label="Threshold (Bt)"
        )
        self.ax.set_title(
            "Neural Ignition Dynamics",
            color=APGI_TEXT,
            fontname="Crimson Pro",
            fontsize=16,
        )
        self.ax.legend(facecolor=APGI_BG, edgecolor=APGI_DARK, labelcolor=APGI_TEXT)
        self.canvas.draw()

    def _build_controls(self):
        # Section Header
        lbl = tk.Label(
            self.controls,
            text="PARAMETER CONTROL",
            fg=APGI_TEXT,
            bg=APGI_BG,
            font=("Crimson Pro", 14, "bold"),
        )
        lbl.pack(anchor="w", pady=(0, 20))

        # Sliders
        params = [
            ("Threshold (Bt)", self.bt_val, APGI_BLUE),
            ("Precision (PI)", self.pi_val, APGI_RED),
            ("Pred. Error (|ε|)", self.eps_val, APGI_YELLOW),
            ("Neuromodulator (β)", self.beta_val, APGI_GREEN),
        ]

        for label, var, color in params:
            f = tk.Frame(self.controls, bg=APGI_BG)
            f.pack(fill="x", pady=10)

            tk.Label(f, text=label, fg=APGI_TEXT, bg=APGI_BG, font=("Inter", 11)).pack(
                anchor="w"
            )

            s = tk.Scale(
                f,
                variable=var,
                from_=0,
                to=1,
                resolution=0.01,
                orient="horizontal",
                bg=APGI_BG,
                fg=APGI_TEXT,
                highlightthickness=0,
                troughcolor=APGI_DARK,
                activebackground=color,
                command=lambda _: self._on_param_change(),
            )
            s.pack(fill="x")

    def _on_param_change(self):
        # Update badges
        self.badges["Bt"].config(text=f"Bt: {self.bt_val.get():.2f}")
        self.badges["PI"].config(text=f"PI: {self.pi_val.get():.2f}")
        self.badges["ε"].config(text=f"ε: {self.eps_val.get():.2f}")
        self.badges["β"].config(text=f"β: {self.beta_val.get():.2f}")

        # Update equation color/glow if Bt exceeded
        if self.pi_val.get() * self.eps_val.get() > self.bt_val.get():
            self.eq_label.config(fg=APGI_PURPLE)
        else:
            self.eq_label.config(fg=APGI_TEXT)

        self._update_plot()


if __name__ == "__main__":
    app = APGITemplate()
    app.mainloop()
