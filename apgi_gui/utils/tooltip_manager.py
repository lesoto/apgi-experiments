"""
Tooltip Manager for APGI Framework GUI

Provides a comprehensive tooltip system for explaining parameters and their valid ranges.
Supports both tkinter and customtkinter widgets.
"""

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Dict, Optional, Union

import customtkinter as ctk


class TooltipManager:
    """Manages tooltips for GUI widgets with parameter descriptions and valid ranges."""

    def __init__(self):
        self.tooltips = {}
        self.tooltip_windows = {}
        self.tooltip_timers = {}
        self._active_tooltips = set()  # Track widgets with active tooltips
        self._load_parameter_descriptions()

    def _load_parameter_descriptions(self):
        """Load parameter descriptions and valid ranges."""
        self.parameter_descriptions = {
            # APGI Framework Core Parameters
            "exteroceptive_precision": {
                "description": "Precision of exteroceptive sensory information",
                "range": "0.1 - 10.0",
                "default": "1.0",
                "details": "Controls how much weight the system gives to external sensory input. Higher values mean more precise exteroceptive information.",
            },
            "interoceptive_precision": {
                "description": "Precision of interoceptive bodily signals",
                "range": "0.1 - 10.0",
                "default": "1.0",
                "details": "Controls the precision of internal bodily signals. Higher values indicate clearer interoceptive signals.",
            },
            "somatic_gain": {
                "description": "Gain factor for somatic marker signals",
                "range": "0.0 - 5.0",
                "default": "1.0",
                "details": "Amplifies or dampens somatic marker influences on decision making. Higher values increase emotional/bodily influence.",
            },
            "threshold": {
                "description": "Decision threshold for consciousness emergence",
                "range": "0.1 - 10.0",
                "default": "1.0",
                "details": "Threshold value that must be exceeded for conscious processing. Higher values require stronger evidence.",
            },
            "steepness": {
                "description": "Steepness of the sigmoid activation function",
                "range": "0.1 - 10.0",
                "default": "1.0",
                "details": "Controls how sharply the system transitions from unconscious to conscious processing.",
            },
            # Neural Signature Parameters
            "gamma_oscillation_power": {
                "description": "Power of gamma frequency oscillations (30-100 Hz)",
                "range": "0.0 - 10.0",
                "default": "1.0",
                "details": "Gamma oscillations are associated with conscious awareness and cognitive processing.",
            },
            "p3b_amplitude": {
                "description": "Amplitude of the P3b ERP component",
                "range": "0.0 - 50.0 μV",
                "default": "5.0",
                "details": "P3b is associated with conscious stimulus processing and working memory updating.",
            },
            "bold_signal_strength": {
                "description": "Strength of BOLD fMRI signal changes",
                "range": "0.0 - 5.0 %",
                "default": "1.0",
                "details": "Blood oxygen level dependent signal changes indicating neural activity.",
            },
            "pci_value": {
                "description": "Perturbational Complexity Index value",
                "range": "0.0 - 1.0",
                "default": "0.5",
                "details": "Measures the complexity of brain responses to perturbations. Higher values indicate more conscious states.",
            },
            # Experimental Parameters
            "num_trials": {
                "description": "Number of experimental trials",
                "range": "1 - 10000",
                "default": "100",
                "details": "Total number of trials to run in the experiment. More trials provide better statistics but take longer.",
            },
            "n_participants": {
                "description": "Number of participants in the study",
                "range": "1 - 1000",
                "default": "20",
                "details": "Number of simulated or real participants. More participants improve generalizability.",
            },
            "n_trials_per_condition": {
                "description": "Number of trials per experimental condition",
                "range": "10 - 1000",
                "default": "50",
                "details": "Trials allocated to each condition in the experimental design.",
            },
            "session_duration": {
                "description": "Duration of experimental session in minutes",
                "range": "1 - 480 minutes",
                "default": "60",
                "details": "Total time allocated for the experimental session.",
            },
            # General Parameters
            "prediction_error_weight": {
                "description": "Weight given to prediction error signals",
                "range": "0.0 - 1.0",
                "default": "0.5",
                "details": "Controls how much prediction errors influence learning and updating.",
            },
            "threshold_sensitivity": {
                "description": "Sensitivity of threshold detection mechanisms",
                "range": "0.1 - 10.0",
                "default": "1.0",
                "details": "How sensitive the system is to detecting threshold crossings.",
            },
            "somatic_marker_strength": {
                "description": "Strength of somatic marker influences",
                "range": "0.0 - 1.0",
                "default": "0.5",
                "details": "Controls how strongly somatic markers affect decision processes.",
            },
            "precision_weight": {
                "description": "Weight given to precision estimates",
                "range": "0.0 - 1.0",
                "default": "0.5",
                "details": "Influence of precision weighting on perception and action.",
            },
            "sample_rate": {
                "description": "Data sampling rate in Hz",
                "range": "100 - 10000 Hz",
                "default": "1000",
                "details": "Sampling frequency for data acquisition. Higher rates capture more detail.",
            },
            "duration": {
                "description": "Duration of stimulus or recording in seconds",
                "range": "0.1 - 3600 seconds",
                "default": "1.0",
                "details": "Length of time for stimulus presentation or data recording.",
            },
            # Experiment Types
            "interoceptive_gating": {
                "description": "Interoceptive attention gating experiment",
                "details": "Tests how interoceptive signals are gated by attention and affect conscious perception.",
            },
            "somatic_marker_priming": {
                "description": "Somatic marker priming experiment",
                "details": "Examines how somatic markers prime decision processes and influence choices.",
            },
            "metabolic_cost": {
                "description": "Metabolic cost of consciousness experiment",
                "details": "Investigates the energy requirements of conscious vs unconscious processing.",
            },
        }

    def get_tooltip_text(self, param_name: str) -> str:
        """Get formatted tooltip text for a parameter."""
        if param_name not in self.parameter_descriptions:
            return f"No description available for '{param_name}'"

        info = self.parameter_descriptions[param_name]

        tooltip_lines = [f"**{param_name.replace('_', ' ').title()}**"]
        tooltip_lines.append(f"Description: {info['description']}")

        if "range" in info:
            tooltip_lines.append(f"Valid Range: {info['range']}")

        if "default" in info:
            tooltip_lines.append(f"Default: {info['default']}")

        if "details" in info:
            tooltip_lines.append(f"\nDetails: {info['details']}")

        return "\n".join(tooltip_lines)

    def create_tooltip(self, widget, param_name: str, delay: int = 500) -> None:
        """Create a tooltip for a widget."""

        def on_enter(event):
            tooltip_text = self.get_tooltip_text(param_name)
            self._schedule_tooltip(widget, event, tooltip_text)

        def on_leave(event):
            self._hide_tooltip(widget)

        # Bind events based on widget type
        if hasattr(widget, "bind"):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        # Store tooltip info
        self.tooltips[id(widget)] = {
            "param_name": param_name,
            "delay": delay,
            "widget": widget,
        }

    def _schedule_tooltip(self, widget, event, tooltip_text: str) -> None:
        """Schedule tooltip to show after a delay to prevent rapid creation."""
        widget_id = id(widget)

        # Cancel any existing timer for this widget
        if widget_id in self.tooltip_timers:
            widget.after_cancel(self.tooltip_timers[widget_id])
            del self.tooltip_timers[widget_id]

        # Schedule new tooltip
        self.tooltip_timers[widget_id] = widget.after(
            500, lambda: self._show_tooltip(widget, event, tooltip_text)
        )

    def _show_tooltip(self, widget, event, tooltip_text: str) -> None:
        """Show tooltip window."""
        widget_id = id(widget)

        # Don't create tooltip if one is already active for this widget
        if widget_id in self._active_tooltips:
            return

        # Hide any existing tooltip for this widget
        self._hide_tooltip(widget)

        # Create tooltip window
        tooltip_window = tk.Toplevel(widget)
        tooltip_window.wm_overrideredirect(True)
        tooltip_window.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

        # Create label with tooltip text
        label = tk.Label(
            tooltip_window,
            text=tooltip_text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 9),
        )
        label.pack()

        # Store reference and mark as active
        self.tooltip_windows[widget_id] = tooltip_window
        self._active_tooltips.add(widget_id)

    def _hide_tooltip(self, widget) -> None:
        """Hide tooltip window."""
        widget_id = id(widget)

        # Cancel any pending timer
        if widget_id in self.tooltip_timers:
            widget.after_cancel(self.tooltip_timers[widget_id])
            del self.tooltip_timers[widget_id]

        # Destroy existing tooltip window
        if widget_id in self.tooltip_windows:
            try:
                self.tooltip_windows[widget_id].destroy()
            except:
                pass  # Window might already be destroyed
            finally:
                del self.tooltip_windows[widget_id]
                self._active_tooltips.discard(widget_id)

    def add_parameter_tooltips(
        self,
        parent_widget: tk.Widget,
        parameter_widgets: Dict[str, Any],
    ) -> None:
        """Add tooltips to multiple parameter widgets at once."""
        for param_name, widget in parameter_widgets.items():
            self.create_tooltip(widget, param_name)

    def clear_all_tooltips(self) -> None:
        """Clear all active tooltips and timers."""
        # Clear all timers
        for widget_id, timer in self.tooltip_timers.items():
            try:
                # Find the widget and cancel its timer
                for tooltip_info in self.tooltips.values():
                    if id(tooltip_info["widget"]) == widget_id:
                        tooltip_info["widget"].after_cancel(timer)
                        break
            except:
                pass

        self.tooltip_timers.clear()

        # Clear all tooltip windows
        for tooltip_window in self.tooltip_windows.values():
            try:
                tooltip_window.destroy()
            except:
                pass

        self.tooltip_windows.clear()

    def save_descriptions_to_file(self, filepath: str) -> None:
        """Save parameter descriptions to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.parameter_descriptions, f, indent=2)

    def load_descriptions_from_file(self, filepath: str) -> None:
        """Load parameter descriptions from JSON file."""
        try:
            with open(filepath, "r") as f:
                loaded_descriptions = json.load(f)
                self.parameter_descriptions.update(loaded_descriptions)
        except Exception as e:
            print(f"Error loading descriptions from {filepath}: {e}")


# Global tooltip manager instance
_tooltip_manager = None


def get_tooltip_manager() -> TooltipManager:
    """Get the global tooltip manager instance."""
    global _tooltip_manager
    if _tooltip_manager is None:
        _tooltip_manager = TooltipManager()
    return _tooltip_manager


def add_tooltip(widget, param_name: str) -> None:
    """Convenience function to add a tooltip to a widget."""
    manager = get_tooltip_manager()
    manager.create_tooltip(widget, param_name)


def add_parameter_tooltips(
    parameter_widgets: Dict[str, Any],
) -> None:
    """Convenience function to add tooltips to multiple parameter widgets."""
    manager = get_tooltip_manager()
    manager.add_parameter_tooltips(None, parameter_widgets)
